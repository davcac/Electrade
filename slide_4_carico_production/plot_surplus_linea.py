#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_surplus_linea.py - SLIDE 4: surplus (produzione - carico) come singola linea.

Legge dati/carico_produzione_48h.csv e produce grafici/03_surplus_linea_7zone.png:
7 pannelli (uno per zona) con una sola linea: surplus in MW
(produzione totale - carico), area verde se surplus >= 0, rossa se < 0.
Finestra 48 ore (12-13/11/2026, UTC).

Uso:
  python slide_4_carico_production/plot_surplus_linea.py
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
    ap = argparse.ArgumentParser(description="Surplus (produzione - carico) come singola linea (slide 4)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "03_surplus_linea_7zone.png"),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s\nLancia prima scarica_entsoe.py (step 1)." % args.csv)

    df = pd.read_csv(args.csv)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    zone_ordinate = ["IT Nord", "IT Centro-Nord", "IT Centro-Sud", "IT Sud",
                     "IT Calabria", "IT Sicilia", "IT Sardegna"]

    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    gen = df[df["source"] != "load"].copy()
    gen_tot = gen.pivot_table(index="ts", columns="zone", values="mw", aggfunc="sum")

    all_ts = load.index.union(gen_tot.index)
    load = load.reindex(all_ts)
    gen_tot = gen_tot.reindex(all_ts)

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")
    zone_zero = {"IT Sud", "IT Calabria", "IT Sicilia"}

    fig, axes = plt.subplots(4, 2, figsize=(14, 12), dpi=150)
    fig.patch.set_facecolor("white")

    for idx, zona in enumerate(zone_ordinate):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")

        if zona in load.columns and zona in gen_tot.columns:
            ts = load.index
            surplus = (gen_tot[zona] - load[zona]).fillna(0).values
            ax.plot(ts, surplus, color="#1f4e79", lw=1.6, label="surplus (MW)", zorder=5)
            ax.fill_between(ts, surplus, 0, where=(surplus >= 0), color="#2e8b57", alpha=0.35,
                            interpolate=True)
            ax.fill_between(ts, surplus, 0, where=(surplus < 0), color="#c00000", alpha=0.35,
                            interpolate=True)
            ax.axhline(0, color="#555555", lw=0.8, ls="--", zorder=2)
            ax.set_ylim(bottom=min(surplus.min() * 1.1, 0) if surplus.min() < 0 else 0,
                        top=surplus.max() * 1.1 if surplus.max() > 0 else 1)

        if zona in zone_zero:
            ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30,
                       zorder=6, clip_on=False, transform=ax.get_xaxis_transform())

        ax.set_title(zona.replace("IT ", ""), fontsize=11, fontweight="bold", pad=6)
        ax.set_ylabel("MW", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0)
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        minor_hours = mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20])
        ax.xaxis.set_minor_locator(minor_hours)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", which="both", labelbottom=False)

    ax_bl = axes[3, 0]
    ax_bl.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax_bl.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")

    ax = axes[3, 1]
    ax.axis("off")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([0], [0], color="#1f4e79", lw=1.6, label="surplus (MW)"),
               Patch(facecolor="#2e8b57", alpha=0.35, label="surplus (prod > carico)"),
               Patch(facecolor="#c00000", alpha=0.35, label="deficit (prod < carico)")]
    ax.legend(handles=handles, loc="upper center", fontsize=9, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Periodo: 12/11 \u2192 13/11/2026 (48h, UTC)\n"
                       "Fonte: ENTSO-E (A65+A75)\n"
                       "Surplus = prod - carico\n"
                       "Dato orario, estrapolato (IT)",
            ha="right", va="bottom", fontsize=7, color="#555555",
            transform=ax.transAxes, linespacing=1.1,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.6))

    fig.suptitle("Surplus (produzione - carico) per zona \\u2014 ENTSO-E \\u2014 12/11 \\u2192 13/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
