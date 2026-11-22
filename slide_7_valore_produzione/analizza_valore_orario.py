"""Valorizzazione descrittiva del profilo solare Sud, a prezzi medi orari.

Legge soltanto fonti gia presenti nel progetto. Nessun download e nessuna
interpolazione: ogni ora deve contenere esattamente quattro misure di potenza.
E_h [MWh] = somma(P_quarto [MW] * 0.25 [h]).
"""

import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GENERATION = ROOT / "slide_4_carico_production/dati/carico_produzione_48h.csv"
PRICES = ROOT / "slide_1_prezzi_pun_zone/20260101_20261115_MGP_PrezziZonali.xlsx"
# Nel periodo selezionato l'ora italiana e CET (UTC+1), senza cambio d'ora.
CET = timezone(timedelta(hours=1), "CET")
START = datetime(2026, 11, 12, tzinfo=CET)
END = START + timedelta(hours=48)
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_prices():
    with ZipFile(PRICES) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(n.itertext()) for n in root.findall("s:si", NS)]
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    records = []
    for row in root.findall("s:sheetData/s:row", NS):
        values = []
        for cell in row.findall("s:c", NS):
            value = cell.findtext("s:v", default="", namespaces=NS)
            if cell.get("t") == "s":
                value = shared[int(value)]
            elif cell.get("t") == "inlineStr":
                value = "".join(cell.find("s:is", NS).itertext())
            values.append(value)
        records.append(values)
    header, *rows = records
    assert "Southern-Italy" in header and "Hour" in header
    result = {}
    for values in rows:
        row = dict(zip(header, values))
        instant = datetime.strptime(row["Date"], "%d/%m/%Y").replace(tzinfo=CET)
        instant += timedelta(hours=int(row["Hour"]) - 1)
        if START <= instant < END:
            assert instant not in result, f"Prezzo duplicato: {instant}"
            price = float(row["Southern-Italy"])
            assert math.isfinite(price)
            result[instant] = price
    return result


def main():
    quarters = defaultdict(dict)
    with GENERATION.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            if row["zone"] != "IT Sud" or row["source"] != "solar":
                continue
            instant = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00")).astimezone(CET)
            assert instant.strftime("%Y-%m-%d %H:%M") == row["timestamp_local"]
            if not START <= instant < END:
                continue
            power = float(row["mw"])
            assert math.isfinite(power) and power >= 0
            assert instant.second == 0 and instant.minute in (0, 15, 30, 45)
            hour = instant.replace(minute=0)
            assert instant.minute not in quarters[hour], f"Produzione duplicata: {instant}"
            quarters[hour][instant.minute] = power

    prices = read_prices()
    expected = [START + timedelta(hours=h) for h in range(48)]
    assert set(quarters) == set(prices) == set(expected), "Ore mancanti o eccedenti"
    rows = []
    for hour in expected:
        points = quarters[hour]
        assert set(points) == {0, 15, 30, 45}, f"Quarti d'ora mancanti: {hour}"
        energy = math.fsum(points.values()) * 0.25
        price = prices[hour]
        rows.append({
            "ora_inizio_cet": hour.isoformat(),
            "ora_inizio_utc": hour.astimezone(timezone.utc).isoformat(),
            "prezzo_medio_orario_eur_mwh": price,
            "potenza_media_oraria_mw": math.fsum(points.values()) / 4,
            "energia_solare_mwh": energy,
            "valore_teorico_orario_eur": energy * price,
            "prezzo_zero": price == 0,
            "prezzo_negativo": price < 0,
            **{f"potenza_quarto_{minute:02d}_mw": points[minute] for minute in (0, 15, 30, 45)},
        })

    energy = math.fsum(r["energia_solare_mwh"] for r in rows)
    value = math.fsum(r["valore_teorico_orario_eur"] for r in rows)
    mean_price = math.fsum(prices.values()) / 48
    captured_price = value / energy
    zero_energy = math.fsum(r["energia_solare_mwh"] for r in rows if r["prezzo_zero"])
    raw_energy = math.fsum(p for points in quarters.values() for p in points.values()) * 0.25
    assert math.isclose(energy, raw_energy, rel_tol=1e-12)
    assert min(prices.values()) <= captured_price <= max(prices.values())
    assert math.isclose(captured_price, math.fsum(r["potenza_media_oraria_mw"] * r["prezzo_medio_orario_eur_mwh"] for r in rows) / math.fsum(r["potenza_media_oraria_mw"] for r in rows), rel_tol=1e-12)
    summary = {
        "zona": "Sud", "fonte": "solare", "inizio_incluso": START.isoformat(),
        "fine_esclusa": END.isoformat(), "numero_ore": len(rows),
        "numero_quarti_ora": sum(len(p) for p in quarters.values()),
        "prezzo_medio_zonale_eur_mwh": mean_price,
        "prezzo_ponderato_produzione_eur_mwh": captured_price,
        "differenza_eur_mwh": captured_price - mean_price,
        "differenza_percento": (captured_price / mean_price - 1) * 100,
        "energia_aggregata_solare_mwh": energy,
        "valore_teorico_aggregato_eur": value,
        "energia_a_prezzo_zero_mwh": zero_energy,
        "quota_energia_a_prezzo_zero_percento": zero_energy / energy * 100,
        "numero_ore_prezzo_zero": sum(r["prezzo_zero"] for r in rows),
        "numero_ore_prezzo_negativo": sum(r["prezzo_negativo"] for r in rows),
        "fonti": [{"percorso": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GENERATION, PRICES)],
        "limite_metodo": "Stima a prezzi medi orari. Non ricostruisce il valore quartorario MGP o i ricavi contrattuali effettivi.",
    }
    (HERE / "dati").mkdir(parents=True, exist_ok=True)
    with (HERE / "dati/valorizzazione_oraria_sud.csv").open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "dati/risultati.json").write_text(json.dumps({"riepilogo": summary, "ore": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
