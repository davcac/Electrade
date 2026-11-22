#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_import_export.py - SLIDE 5/nuovo: import/export giornaliero per le 3 zone a zero.

Legge dati/transiti_48h.csv e produce due grafici (uno per giorno):
  grafici/import_export_20261112.png
  grafici/import_export_20261113.png

Per ciascuna zona (Sud, Calabria, Sicilia): barre raggruppate per zona vicina,
con import (positivo) ed export (negativo) in MWh (somma delle 24 ore).
Dato: scambi programmati A09 (valori lordi per direzione).

Uso:
  python slide_5_mappa_transiti/nuovo/plot_import_export.py
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(os.path.dirname(HERE), "dati", "transiti_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

ZONES = ["IT Sud", "IT Calabria", "IT Sicilia"]


def compute_day(df, day_str):
    """Restituisce dict: zona -> {neighbor: (import_mwh, export_mwh)}."""
    d = df[df["timestamp_utc"].dt.strftime("%Y-%m-%d") == day_str].copy()
    result = {z: {} for z in ZONES}
    for z in ZONES:
        # confini uscenti da z (export)
        out_borders = d[d["out_zone"] == z]
        for nb in out_borders["in_zone"].unique():
            sub = out_borders[out_borders["in_zone"] == nb]
            export_mwh = sub["scheduled_mw"].sum()  # MW * 1h = MWh (orario)
            result[z].setdefault(nb, [0, 0, 0])[1] += export_mwh
        # confini entranti in z (import)
        in_borders = d[d["in_zone"] == z]
        for nb in in_borders["out_zone"].unique():
            sub = in_borders[in_borders["out_zone"] == nb]
            import_mwh = sub["scheduled_mw"].sum()
            result[z].setdefault(nb, [0, 0, 0])[0] += import_mwh
        # saldo netto (import - export) per vicino
        for nb in result[z]:
            result[z][nb][2] = result[z][nb][0] - result[z][nb][1]
    return result


def plot_day(result, day_str, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=150)
    fig.patch.set_facecolor("white")

    for idx, zona in enumerate(ZONES):
        ax = axes[idx]
        ax.set_facecolor("white")
        neighbors = sorted(result[zona].keys())
        imports = [result[zona][n][0] for n in neighbors]
        exports = [result[zona][n][1] for n in neighbors]
        saldi = [result[zona][n][2] for n in neighbors]

        x = np.arange(len(neighbors))
        width = 0.25
        ax.bar(x - width, imports, width, label="import", color="#2e8b57", alpha=0.35,
               edgecolor="#2e8b57", linewidth=1.2)
        ax.bar(x, [-e for e in exports], width, label="export", color="#c00000", alpha=0.35,
               edgecolor="#c00000", linewidth=1.2)
        ax.bar(x + width, saldi, width, label="saldo netto", color="#1f77b4", alpha=0.35,
               edgecolor="#1f77b4", linewidth=1.2)

        ax.set_xticks(x)
        ax.set_xticklabels([n.replace("IT ", "") for n in neighbors], rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("MWh", fontsize=9)
        ax.set_title(zona.replace("IT ", ""), fontsize=11, fontweight="bold", pad=6)
        ax.axhline(0, color="#555555", lw=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color="#e0e0e0", lw=0.4, alpha=0.6)

    axes[0].legend(loc="upper left", fontsize=8, frameon=True, facecolor="white", edgecolor="#cccccc")
    day_label = "%s/%s/%s" % (day_str[6:8], day_str[4:6], day_str[0:4])
    fig.suptitle("Import / Export giornaliero per zona \\u2014 Scambi programmati A09 \\u2014 %s" % day_label,
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out_path)


def main():
    ap = argparse.ArgumentParser(description="Import/Export giornaliero slide 5 (nuovo)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso CSV transiti")
    ap.add_argument("--out-dir", default=GRAFICI, help="cartella output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s\nEsegui prima scarica_transiti_entsoe.py." % args.csv)

    df = pd.read_csv(args.csv)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    os.makedirs(args.out_dir, exist_ok=True)

    for day in ["2026-11-12", "2026-11-13"]:
        # il CSV ha timestamp UTC; il giorno locale italiano e' UTC+1, quindi 12/11 locale = 11/11 23:00 UTC -> 12/11 22:00 UTC
        # per semplicita' usiamo il giorno UTC (che copre quasi tutto il giorno locale)
        day_utc = day
        result = compute_day(df, day_utc)
        out_path = os.path.join(args.out_dir, "import_export_%s.png" % day.replace("-", ""))
        plot_day(result, day, out_path)

    print("fatto.")


if __name__ == "__main__":
    main()
