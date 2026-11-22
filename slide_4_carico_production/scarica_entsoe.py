#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scarica_entsoe.py - SLIDE 4, STEP 1: scarica carico + produzione fisica per fonte
per le 7 zone italiane da ENTSO-E Transparency Platform e costruisce il CSV tidy.

Fa SOLO il download (A65 load + A75 generation) e il parsing: scrive gli XML grezzi
in dati/ e il dataset tidy dati/carico_produzione_48h.csv, poi si ferma.
Il grafico e' prodotto dallo step 2: plot_produzione.py (legge CSV e XML A75).

Uso (con il volume A: montato, OpenCode spento):
  python "presentazione lunedì 23/slide_4_per_fonte/scarica_entsoe.py"
  python "presentazione lunedì 23/slide_4_per_fonte/scarica_entsoe.py" --start 2026-11-12 --end 2026-11-13
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "dati")

API_URL = "https://web-api.tp.entsoe.eu/api"
try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None

ZONES = {
    "IT Nord": "10Y1001A1001A73I",
    "IT Centro-Nord": "10Y1001A1001A70O",
    "IT Centro-Sud": "10Y1001A1001A71M",
    "IT Sud": "10Y1001A1001A788",
    "IT Calabria": "10Y1001C--00096J",
    "IT Sicilia": "10Y1001A1001A75E",
    "IT Sardegna": "10Y1001A1001A74G",
}

PSR_TO_SOURCE = {
    "B16": "solar",
    "B18": "wind",
    "B19": "wind",
    "B10": "hydro",
    "B11": "hydro",
    "B12": "hydro",
    "B04": "gas",
}
STORAGE_PSR_TYPES = {"B10", "B25", "B32"}


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


def read_periods(root, value_tag):
    periods = []
    for series in descendants(root, "TimeSeries"):
        sparse = (text_of(series, "curveType") or "").strip().upper() == "A03"
        for period in children(series, "Period"):
            interval = children(period, "timeInterval")
            if not interval:
                continue
            minutes = resolution_minutes(text_of(period, "resolution") or "PT60M")
            if minutes is None:
                continue
            values = {}
            for point in children(period, "Point"):
                position = text_of(point, "position")
                value = text_of(point, value_tag)
                if position is None or value is None:
                    continue
                try:
                    values[int(position)] = float(value)
                except ValueError:
                    continue
            periods.append({
                "start": parse_instant(text_of(interval[0], "start")),
                "end": parse_instant(text_of(interval[0], "end")),
                "minutes": minutes,
                "values": values,
                "sparse": sparse,
            })
    return periods


def download(token, params, out_path):
    import requests

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
        raise RuntimeError("ENTSO-E ha rifiutato la richiesta: %s" % (detail or response.text[:300]))
    return out_path


def parse_load_or_generation(path, *, separate_absorption=False):
    root = ET.parse(path).getroot()
    rows = []
    for series in descendants(root, "TimeSeries"):
        psr = descendants(series, "psrType")
        psr_code = (psr[0].text or "").strip() if psr else ""
        out_zone = text_of(series, "outBiddingZone_Domain.mRID")
        source = PSR_TO_SOURCE.get(psr_code, "other")
        if not psr:
            source = "load"
        elif separate_absorption and out_zone:
            source = "storage_absorption" if psr_code in STORAGE_PSR_TYPES else "other_absorption"
        eic = (out_zone
               or text_of(series, "inBiddingZone_Domain.mRID")
               or text_of(series, "in_Domain.mRID")
               or text_of(series, "out_Domain.mRID") or "").strip()
        zone_name = None
        for name, code in ZONES.items():
            if code == eic:
                zone_name = name
                break
        if zone_name is None:
            zone_name = eic
        sparse = (text_of(series, "curveType") or "").strip().upper() == "A03"
        for period in children(series, "Period"):
            interval = children(period, "timeInterval")
            if not interval:
                continue
            minutes = resolution_minutes(text_of(period, "resolution") or "PT60M")
            if minutes is None:
                continue
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
                rows.append((zone_name, source, instant, value))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Scarica carico + produzione ENTSO-E per le 7 zone italiane (step 1: solo dati + CSV)")
    ap.add_argument("--start", default="2026-11-12", help="primo giorno locale (YYYY-MM-DD)")
    ap.add_argument("--end", default="2026-11-13", help="ultimo giorno locale (YYYY-MM-DD)")
    ap.add_argument("--out", default=OUT_DIR, help="cartella per gli XML grezzi e il CSV")
    args = ap.parse_args()

    start_local = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=ROME)
    end_local = datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=ROME) + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    print("SLIDE 4 - STEP 1: scarico dati ENTSO-E + CSV")
    print("  finestra locale : %s -> %s" % (start_local.strftime("%Y-%m-%d"), end_local.strftime("%Y-%m-%d")))
    print("  finestra UTC    : %s -> %s" % (start_utc.strftime("%Y%m%d%H%M"), end_utc.strftime("%Y%m%d%H%M")))
    print("  zone            : %d" % len(ZONES))

    token = read_token()
    print("  token           : %d caratteri (non mostrato)" % len(token))

    os.makedirs(args.out, exist_ok=True)
    raw_paths = []
    for name, eic in ZONES.items():
        for doc, tag, extra in (("A65", "A65", {"outBiddingZone_Domain": eic}),
                                ("A75", "A75", {"in_Domain": eic})):
            path = os.path.join(args.out, "%s_%s.xml" % (tag, name.replace(" ", "_")))
            params = {"documentType": doc, "processType": "A16",
                      "periodStart": start_utc.strftime("%Y%m%d%H%M"),
                      "periodEnd": end_utc.strftime("%Y%m%d%H%M")}
            params.update(extra)
            download(token, params, path)
            raw_paths.append(path)
            print("   %s %s -> %s" % (tag, name, os.path.basename(path)))

    all_rows = []
    for path in raw_paths:
        rows = parse_load_or_generation(path)
        all_rows.extend(rows)
        print("   parsato %s: %d punti" % (os.path.basename(path), len(rows)))

    records = []
    for zone, source, instant, mw in all_rows:
        records.append({
            "zone": zone,
            "source": source,
            "timestamp_utc": instant.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timestamp_local": instant.astimezone(ROME).strftime("%Y-%m-%d %H:%M"),
            "mw": mw,
        })
    df = pd.DataFrame(records)
    csv_path = os.path.join(args.out, "carico_produzione_48h.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print("  dataset         : %s (%d righe)" % (csv_path, len(df)))
    print("  fatto (step 1). Per il grafico lancia: plot_produzione.py")


if __name__ == "__main__":
    main()
