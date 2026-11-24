#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ricostruisce un CSV a 15 minuti dai XML ENTSO-E A09/A11/A61 già scaricati.

Legge solo gli XML originali in ../dati (non fa richieste API). Le serie PT15
restano quartorarie. Le serie PT60 sono riportate ai quattro quarti coperti,
con la risoluzione nativa esplicitata nel CSV. Non sostituisce i file orari.
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE.parent / "dati"
OUT_CSV = HERE / "dati" / "transiti_48h_15min.csv"
ROME = ZoneInfo("Europe/Rome")

BORDERS = [
    ("IT Sud", "IT Centro-Sud"), ("IT Centro-Sud", "IT Sud"),
    ("IT Sud", "IT Calabria"), ("IT Calabria", "IT Sud"),
    ("IT Sud", "Grecia"), ("Grecia", "IT Sud"),
    ("IT Calabria", "IT Sicilia"), ("IT Sicilia", "IT Calabria"),
    ("IT Sicilia", "Malta"), ("Malta", "IT Sicilia"),
]
DATASETS = {
    "A11": ("flow_physical_mw", "flow_physical_resolution_min"),
    "A09": ("scheduled_mw", "scheduled_resolution_min"),
    "A61": ("ntc_mw", "ntc_resolution_min"),
}


def local_name(tag):
    return tag.split("}")[-1]


def children(element, name):
    return [child for child in list(element) if local_name(child.tag) == name]


def text_of(element, name):
    found = children(element, name)
    return found[0].text.strip() if found and found[0].text else None


def parse_instant(value):
    return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


def resolution_minutes(value):
    if not value or not value.startswith("PT"):
        return None
    suffix = value[2:]
    if suffix.endswith("M"):
        return int(suffix[:-1])
    if suffix.endswith("H"):
        return 60 * int(suffix[:-1])
    return None


def parse_xml(path):
    """Expand ENTSO-E Period/Point records at their native resolution."""
    root = ET.parse(path).getroot()
    result = []
    for series in (node for node in root.iter() if local_name(node.tag) == "TimeSeries"):
        sparse = (text_of(series, "curveType") or "").upper() == "A03"
        for period in children(series, "Period"):
            intervals = children(period, "timeInterval")
            if not intervals:
                continue
            minutes = resolution_minutes(text_of(period, "resolution"))
            if minutes is None:
                continue
            start = parse_instant(text_of(intervals[0], "start"))
            end = parse_instant(text_of(intervals[0], "end"))
            point_values = {}
            for point in children(period, "Point"):
                position = text_of(point, "position")
                quantity = text_of(point, "quantity")
                if position is None or quantity is None:
                    continue
                try:
                    point_values[int(position)] = float(quantity)
                except ValueError:
                    continue
            instant, position, last = start, 1, None
            while instant < end:
                if position in point_values:
                    last = point_values[position]
                    result.append((instant, instant + timedelta(minutes=minutes), last, minutes))
                elif sparse and last is not None:
                    result.append((instant, instant + timedelta(minutes=minutes), last, minutes))
                instant += timedelta(minutes=minutes)
                position += 1
    return result


def safe_border(out_zone, in_zone):
    return (out_zone + " -> " + in_zone).replace(" ", "_").replace("->", "to")


def main():
    if not RAW_DIR.is_dir():
        raise SystemExit("Cartella XML originali non trovata: %s" % RAW_DIR)
    local_start = datetime(2026, 11, 12, 0, 0, tzinfo=ROME)
    local_end = datetime(2026, 11, 14, 0, 0, tzinfo=ROME)
    start_utc = local_start.astimezone(timezone.utc)
    end_utc = local_end.astimezone(timezone.utc)
    grid = pd.date_range(start_utc, end_utc, freq="15min", inclusive="left")
    output = []
    resolution_summary = {key: set() for key in DATASETS}

    for out_zone, in_zone in BORDERS:
        border = "%s -> %s" % (out_zone, in_zone)
        values = {column: {} for column, _ in DATASETS.values()}
        native_res = {column: {} for column, _ in DATASETS.values()}
        for doc, (value_col, res_col) in DATASETS.items():
            filename = "%s_%s_%s.xml" % (
                doc, safe_border(out_zone, in_zone), value_col
            )
            path = RAW_DIR / filename
            if not path.is_file():
                continue
            for interval_start, interval_end, value, minutes in parse_xml(path):
                resolution_summary[doc].add(minutes)
                # Map the native interval to the 15-minute slots it covers.
                qh = interval_start
                while qh < interval_end:
                    if qh in grid:
                        values[value_col][qh] = value
                        native_res[value_col][qh] = minutes
                    qh += timedelta(minutes=15)

        for ts in grid:
            row = {
                "border": border,
                "out_zone": out_zone,
                "in_zone": in_zone,
                "timestamp_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "timestamp_local": ts.tz_convert(ROME).strftime("%Y-%m-%d %H:%M"),
            }
            for doc, (value_col, res_col) in DATASETS.items():
                row[value_col] = values[value_col].get(ts)
                row[res_col] = native_res[value_col].get(ts)
            output.append(row)

    result = pd.DataFrame(output)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print("CSV:", OUT_CSV, "(%d righe, %d intervalli per direzione)" % (len(result), len(grid)))
    for doc in DATASETS:
        print("%s risoluzione nativa: %s" % (doc, sorted(resolution_summary[doc])))


if __name__ == "__main__":
    main()
