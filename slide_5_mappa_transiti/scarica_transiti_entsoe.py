#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scarica_transiti_entsoe.py - SLIDE 5: flussi fisici, scambi programmati e NTC
day-ahead per i confini delle zone con prezzo zero (Calabria, Sud, Sicilia).

Scarica da ENTSO-E Transparency Platform:
  A11  flussi fisici (reali) tra due zone
  A09  scambi commerciali programmati (day-ahead, contract_MarketAgreement.Type=A01)
  A61  capacita' di trasferimento day-ahead (NTC)

Confini analizzati (interni + esteri) per Calabria, Sud, Sicilia:
  Sud <-> Centro-Sud, Calabria, Sicilia, Grecia, Malta
  Calabria <-> Sicilia
  Sicilia <-> Malta

Output: dati/transiti_48h.csv (una riga per confine per ora, con 3 colonne di valore)
        + XML grezzi in dati/

  python slide_5_mappa_transiti/scarica_transiti_entsoe.py
  python slide_5_mappa_transiti/scarica_transiti_entsoe.py --start 2026-11-12 --end 2026-11-13
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "dati")
os.makedirs(OUT_DIR, exist_ok=True)

API_URL = "https://web-api.tp.entsoe.eu/api"
try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None

# confini non orientati per le 3 zone con prezzo zero
_UNDIRECTED = [
    ("IT Sud", "IT Centro-Sud", "10Y1001A1001A788", "10Y1001A1001A71M"),
    ("IT Sud", "IT Calabria", "10Y1001A1001A788", "10Y1001C--00096J"),
    ("IT Sud", "Grecia", "10Y1001A1001A788", "10YGR-HTSO-----Y"),
    ("IT Calabria", "IT Sicilia", "10Y1001C--00096J", "10Y1001A1001A75E"),
    ("IT Sicilia", "Malta", "10Y1001A1001A75E", "10Y1001A1001A93C"),
]

# entrambe le direzioni per ogni confine (scarto i doppioni: ogni coppia orientata una sola volta)
BORDERS = []
_seen = set()
for a, b, ea, eb in _UNDIRECTED:
    for out_zone, in_zone, eic_out, eic_in in ((a, b, ea, eb), (b, a, eb, ea)):
        key = (out_zone, in_zone)
        if key in _seen:
            continue
        _seen.add(key)
        BORDERS.append(("%s -> %s" % (out_zone, in_zone), out_zone, in_zone, eic_out, eic_in))

# dataset: (nome_colonna, documentType, params_extra)
DATASETS = [
    ("flow_physical_mw", "A11", {}),
    ("scheduled_mw", "A09", {"contract_MarketAgreement.Type": "A01"}),
    ("ntc_mw", "A61", {"contract_MarketAgreement.Type": "A01"}),
]


def read_token():
    token = os.environ.get("ENTSOE_TOKEN", "").strip()
    if token:
        return token
    candidati = [os.path.join(HERE, "secrets.env"),
                 r"A:\secrets.env", r"A:\entsoe.env"]
    for path in candidati:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:].strip()
                if line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                if name.strip() == "ENTSOE_TOKEN":
                    return value.strip().strip('"').strip("'")
    raise SystemExit(
        "Token ENTSO-E non trovato. Monta il volume A: (che contiene ENTSOE_TOKEN) "
        "oppure imposta la variabile d'ambiente ENTSOE_TOKEN."
    )


def local_name(tag):
    return tag.split("}")[-1]


def children(element, name):
    return [c for c in list(element) if local_name(c.tag) == name]


def descendants(root, name):
    return [e for e in root.iter() if local_name(e.tag) == name]


def text_of(element, name):
    found = children(element, name)
    return found[0].text if found else None


def parse_instant(text):
    text = text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def resolution_minutes(resolution):
    if not resolution:
        return None
    if resolution.startswith("PT"):
        rest = resolution[2:]
        if rest.endswith("M"):
            return int(rest[:-1])
        if rest.endswith("H"):
            return int(rest[:-1]) * 60
    if resolution.startswith("P") and resolution.endswith("D"):
        return int(resolution[1:-1]) * 1440
    return None


def expand_series(periods):
    result = {}
    for period in periods:
        step = timedelta(minutes=period["minutes"])
        instant = period["start"]
        index = 1
        last = None
        while instant < period["end"]:
            if index in period["values"]:
                last = period["values"][index]
                result[instant] = last
            elif period["sparse"] and last is not None:
                result[instant] = last
            instant += step
            index += 1
    return result


def download(token, params, out_path):
    query = dict(params)
    query["securityToken"] = token
    response = requests.get(API_URL, params=query, timeout=120)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(response.text)
    if response.status_code != 200 or "Acknowledgement_MarketDocument" in response.text[:2000]:
        root = ET.fromstring(response.text)
        reasons = [e for e in root.iter() if local_name(e.tag) == "Reason"]
        detail = "; ".join(
            (text_of(r, "code") or "?") + " - " + (text_of(r, "text") or "")
            for r in reasons
        )
        return False, detail or response.text[:200]
    return True, ""


def parse_transit(path):
    """Restituisce lista di (instant_utc, value) per un XML di transito."""
    root = ET.parse(path).getroot()
    rows = []
    for series in descendants(root, "TimeSeries"):
        for period in children(series, "Period"):
            interval = children(period, "timeInterval")
            if not interval:
                continue
            minutes = resolution_minutes(text_of(period, "resolution") or "PT60M")
            if minutes is None:
                continue
            sparse = False
            # curveType puo' essere su TimeSeries
            ct = text_of(series, "curveType")
            if (ct or "").strip().upper() == "A03":
                sparse = True
            values = {}
            for point in children(period, "Point"):
                position = text_of(point, "position")
                value = text_of(point, "quantity")
                if position is None or value is None:
                    continue
                try:
                    values[int(position)] = float(value)
                except ValueError:
                    continue
            for instant, value in expand_series([{
                "start": parse_instant(text_of(interval[0], "start")),
                "end": parse_instant(text_of(interval[0], "end")),
                "minutes": minutes,
                "values": values,
                "sparse": sparse,
            }]).items():
                rows.append((instant, value))
    return rows


def to_hourly(df):
    """Riduce a una riga per ora (media) con timestamp UTC."""
    if df.empty:
        return df
    df = df.copy()
    df["ts"] = pd.to_datetime(df["instant"], utc=True)
    df = df.set_index("ts")
    out = df["value"].resample("1h").mean().reset_index()
    out = out.rename(columns={"ts": "timestamp_utc", "value": "value"})
    return out


def main():
    ap = argparse.ArgumentParser(description="Scarica transiti ENTSO-E per Calabria/Sud/Sicilia (slide 5)")
    ap.add_argument("--start", default="2026-11-12", help="primo giorno locale (YYYY-MM-DD)")
    ap.add_argument("--end", default="2026-11-13", help="ultimo giorno locale (YYYY-MM-DD)")
    ap.add_argument("--out", default=OUT_DIR, help="cartella output")
    args = ap.parse_args()

    start_local = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=ROME)
    end_local = datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=ROME) + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    ps = start_utc.strftime("%Y%m%d%H%M")
    pe = end_utc.strftime("%Y%m%d%H%M")

    print("SLIDE 5 - transiti ENTSO-E")
    print("  finestra locale : %s -> %s" % (start_local.strftime("%Y-%m-%d"), end_local.strftime("%Y-%m-%d")))
    print("  finestra UTC    : %s -> %s" % (ps, pe))
    print("  confini         : %d" % len(BORDERS))
    print("  dataset per confine: %d" % len(DATASETS))

    token = read_token()
    print("  token           : %d caratteri (non mostrato)" % len(token))

    os.makedirs(args.out, exist_ok=True)

    # struttura: border_label -> {dataset_col: DataFrame(timestamp_utc, value)}
    border_data = {b[0]: {} for b in BORDERS}

    for label, out_zone, in_zone, eic_out, eic_in in BORDERS:
        for col, doc, extra in DATASETS:
            params = {"documentType": doc,
                      "in_Domain": eic_in,
                      "out_Domain": eic_out,
                      "periodStart": ps,
                      "periodEnd": pe}
            params.update(extra)
            safe_label = label.replace(" ", "_").replace("->", "to")
            fname = "%s_%s_%s.xml" % (doc, safe_label, col)
            path = os.path.join(args.out, fname)
            ok, detail = download(token, params, path)
            if not ok:
                print("   %s %s: NESSUN DATO (%s)" % (doc, label, detail[:80]))
                border_data[label][col] = pd.DataFrame()
                continue
            rows = parse_transit(path)
            df = pd.DataFrame(rows, columns=["instant", "value"])
            dfh = to_hourly(df)
            border_data[label][col] = dfh
            print("   %s %s: %d punti -> %d ore" % (doc, label, len(rows), len(dfh)))

    # costruisci CSV unico: una riga per confine per ora
    all_rows = []
    for label, out_zone, in_zone, eic_out, eic_in in BORDERS:
        # unione degli timestamp di tutti e tre i dataset
        ts_set = set()
        for col, _, _ in DATASETS:
            df = border_data[label].get(col, pd.DataFrame())
            if not df.empty:
                ts_set.update(df["timestamp_utc"].tolist())
        if not ts_set:
            print("   (nessun dato per %s)" % label)
            continue
        ts_sorted = sorted(ts_set)
        # mappa timestamp -> valore per ciascun dataset
        val_maps = {}
        for col, _, _ in DATASETS:
            df = border_data[label].get(col, pd.DataFrame())
            if df.empty:
                val_maps[col] = {}
            else:
                val_maps[col] = dict(zip(df["timestamp_utc"], df["value"]))
        for ts in ts_sorted:
            all_rows.append({
                "border": label,
                "out_zone": out_zone,
                "in_zone": in_zone,
                "timestamp_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(ts, "strftime") else str(ts),
                "timestamp_local": ts.tz_convert(ROME).strftime("%Y-%m-%d %H:%M") if hasattr(ts, "tz_convert") else "",
                "flow_physical_mw": val_maps["flow_physical_mw"].get(ts),
                "scheduled_mw": val_maps["scheduled_mw"].get(ts),
                "ntc_mw": val_maps["ntc_mw"].get(ts),
            })

    df_out = pd.DataFrame(all_rows)
    csv_path = os.path.join(args.out, "transiti_48h.csv")
    df_out.to_csv(csv_path, index=False, encoding="utf-8")
    print("  dataset         : %s (%d righe)" % (csv_path, len(df_out)))
    print("  fatto.")


if __name__ == "__main__":
    main()
