#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_surplus_macrozone.py - SLIDE 4: carico vs produzione per la macrozona Sud+Calabria+Sicilia.

Identico a 02_surplus_3zone.png ma per la zona aggregata (somma delle 3 zone).
Un solo grafico con carico (nero) e produzione fisica (grigia), area verde/rossa.

Uso:
  python slide_4_carico_production/plot_surplus_macrozone.py
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "dati", "carico_produzione_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None


def main():
    ap = argparse.ArgumentParser(description="Surplus macrozona Sud+Calabria+Sicilia (slide 4)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "05_surplus_macrozone.png"),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s\nLancia prima scarica_entsoe.py (step 1)." % args.csv)

    df = pd.read_csv(args.csv)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    zone_macro = ["IT Sud", "IT Calabria", "IT Sicilia"]

    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    gen = df[df["source"] != "load"].copy()
    gen_tot = gen.pivot_table(index="ts", columns="zone", values="mw", aggfunc="sum")

    # aggrega le 3 zone
    load_macro = load[zone_macro].sum(axis=1)
    gen_macro = gen_tot[zone_macro].sum(axis=1)

    all_ts = load_macro.index.union(gen_macro.index)
    load_macro = load_macro.reindex(all_ts)
    gen_macro = gen_macro.reindex(all_ts)

    ts = load_macro.index
    l = load_macro.fillna(0).values
    g = gen_macro.fillna(0).values

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")

    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(ts, l, color="black", lw=1.6, label="carico (macrozona)", zorder=5)
    ax.plot(ts, g, color="#555555", lw=1.6, ls="-", label="produzione fisica (macrozona)", zorder=5)
    ax.fill_between(ts, g, l, where=(g >= l), color="#2e8b57", alpha=0.35,
                    label="surplus", interpolate=True)
    ax.fill_between(ts, g, l, where=(g < l), color="#c00000", alpha=0.35,
                    label="deficit", interpolate=True)
    ax.axhline(0, color="#555555", lw=0.8, ls="--", zorder=2)
    ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30,
               zorder=6, clip_on=False, transform=ax.get_xaxis_transform())

    ax.set_ylabel("MW", fontsize=9)
    ax.set_title("Macrozona Sud + Calabria + Sicilia  -  carico vs produzione", fontsize=12,
                 fontweight="bold", pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    minor_hours = mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20])
    ax.xaxis.set_minor_locator(minor_hours)
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([0], [0], color="black", lw=1.6, label="carico"),
               Line2D([0], [0], color="#555555", lw=1.6, label="produzione fisica"),
               Patch(facecolor="#2e8b57", alpha=0.35, label="surplus"),
               Patch(facecolor="#c00000", alpha=0.35, label="deficit"),
               Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="ore a prezzo zero")]
    ax.legend(handles=handles, loc="lower right", fontsize=8, frameon=True,
              facecolor="white", edgecolor="#cccccc")



    fig.suptitle("Macrozona Sud+Calabria+Sicilia  -  carico vs produzione  -  12/11 \u2192 13/11/2026 (UTC)",
                 fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
