#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
elabora_limiti_gme.py - SLIDE 5: parse dei file XML GME (ME_TransmissionLimits)
e produzione di un CSV orario dei limiti di transito per i confini delle zone a zero.

Input:  cartella con file XML GME (es. MGP_LimitiTransito2026111220261113/*.xml)
Output: dati/limiti_transito_48h.csv (granularita' oraria, media dei 4 periodi di 15 min)

Uso:
  python slide_5_mappa_transiti/elabora_limiti_gme.py --dir "slide_5_mappa_transiti/MGP_LimitiTransito2026111220261113"
  python slide_5_mappa_transiti/elabora_limiti_gme.py --dir "..." --all   # tutte le 42 coppie
"""
import argparse
import os
import glob
import xml.etree.ElementTree as ET

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "dati", "limiti_transito_48h.csv")
os.makedirs(os.path.join(HERE, "dati"), exist_ok=True)

# mappa codici GME -> nomi zona (coerenti con transiti_48h.csv)
GME_TO_ZONE = {
    "NORD": "IT Nord",
    "CNOR": "IT Centro-Nord",
    "CSUD": "IT Centro-Sud",
    "SUD": "IT Sud",
    "CALA": "IT Calabria",
    "SICI": "IT Sicilia",
    "SARD": "IT Sardegna",
    "GREC": "Grecia",
    "XGRE": "Grecia (XGRE)",
    "MALT": "Malta",
    "AUST": "Austria",
    "FRAN": "Francia",
    "SLOV": "Slovenia",
    "SVIZ": "Svizzera",
    "CORS": "Corsica",
    "COAC": "Corsica AC",
    "COUP": "Coupling",
    "XAUS": "Austria (XAUS)",
    "XFRA": "Francia (XFRA)",
    "BSP": "BSP",
    "MONT": "Montenegro",
}

# confini di interesse (almeno una delle due zone e' tra le zone a zero o loro vicini diretti)
ZONES_OF_INTEREST = {"IT Sud", "IT Calabria", "IT Sicilia"}


def parse_xml(path):
    root = ET.parse(path).getroot()
    rows = []
    for rec in root.findall("LimitiTransito"):
        data = rec.find("Data").text.strip()
        ora = int(rec.find("Ora").text.strip())
        periodo = int(rec.find("Periodo").text.strip())
        da = rec.find("Da").text.strip()
        a = rec.find("A").text.strip()
        limite_raw = rec.find("Limite").text.strip().replace(",", ".")
        try:
            limite = float(limite_raw)
        except ValueError:
            limite = None
        coeff = rec.find("Coefficiente").text.strip()
        rows.append({
            "data": data,
            "ora": ora,
            "periodo": periodo,
            "da_code": da,
            "a_code": a,
            "limite_mw": limite,
            "coeff": coeff,
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="Parse limiti transito GME -> CSV orario")
    ap.add_argument("--dir", required=True, help="cartella con file XML GME")
    ap.add_argument("--out", default=DEFAULT_OUT, help="percorso CSV output")
    ap.add_argument("--all", action="store_true", help="includi tutte le coppie (default: solo zone di interesse)")
    args = ap.parse_args()

    xml_files = sorted(glob.glob(os.path.join(args.dir, "*.xml")))
    if not xml_files:
        raise SystemExit("Nessun file XML trovato in %s" % args.dir)

    frames = [parse_xml(f) for f in xml_files]
    df = pd.concat(frames, ignore_index=True)

    # mappa codici -> nomi zona
    df["out_zone"] = df["da_code"].map(lambda c: GME_TO_ZONE.get(c, c))
    df["in_zone"] = df["a_code"].map(lambda c: GME_TO_ZONE.get(c, c))

    # filtro coppie di interesse (a meno di --all)
    if not args.all:
        mask = df["out_zone"].isin(ZONES_OF_INTEREST) | df["in_zone"].isin(ZONES_OF_INTEREST)
        df = df[mask].copy()

    # timestamp locale (GME e' in ora italiana)
    df["timestamp_local"] = pd.to_datetime(df["data"], format="%Y%m%d") + pd.to_timedelta(df["ora"] - 1, unit="h")
    # timestamp UTC (CET = UTC+1 a novembre)
    df["timestamp_utc"] = df["timestamp_local"] - pd.Timedelta(hours=1)

    # aggrega a orario: media dei 4 periodi di 15 min
    agg = df.groupby(["out_zone", "in_zone", "timestamp_utc", "timestamp_local"], as_index=False)["limite_mw"].mean()
    agg = agg.rename(columns={"limite_mw": "limite_mw"})

    # etichetta confine coerente con transiti_48h.csv
    agg["border"] = agg["out_zone"] + " -> " + agg["in_zone"]

    # ordina
    agg = agg.sort_values(["border", "timestamp_utc"]).reset_index(drop=True)

    # colonne finali
    out_cols = ["border", "out_zone", "in_zone", "timestamp_utc", "timestamp_local", "limite_mw"]
    agg[out_cols].to_csv(args.out, index=False, encoding="utf-8")
    print("Scritto:", args.out, "(%d righe, %d confini)" % (len(agg), agg["border"].nunique()))
    print("Confini:", sorted(agg["border"].unique()))


if __name__ == "__main__":
    main()
