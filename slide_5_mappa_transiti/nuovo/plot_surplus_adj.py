#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_surplus_adj.py - SLIDE 4: surplus adj (carico vs produzione + net import).

Per le 3 zone a prezzo zero (Sud, Calabria, Sicilia):
  - carico (nera)
  - produzione + net import (grigia)
  - area verde/rossa tra le due
Finestra 48 ore (12-13/11/2026, UTC).

Uso:
  python slide_4_carico_production/plot_surplus_adj.py
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
DEFAULT_CSV = os.path.join(os.path.dirname(HERE), "..", "slide_4_carico_production", "dati", "carico_produzione_48h.csv")
TRANSITI_CSV = os.path.join(os.path.dirname(HERE), "dati", "transiti_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None


def main():
    ap = argparse.ArgumentParser(description="Surplus adj (carico vs produzione + net import) (slide 4)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso CSV carico/produzione")
    ap.add_argument("--transiti", default=TRANSITI_CSV, help="percorso CSV transiti slide 5")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "04_surplus_adj_3zone.png"),
                    help="percorso PNG output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s" % args.csv)

    df = pd.read_csv(args.csv)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    zone_ordinate = ["IT Sud", "IT Calabria", "IT Sicilia"]

    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    gen = df[df["source"] != "load"].copy()
    gen_tot = gen.pivot_table(index="ts", columns="zone", values="mw", aggfunc="sum")

    all_ts = load.index.union(gen_tot.index)
    load = load.reindex(all_ts)
    gen_tot = gen_tot.reindex(all_ts)

    net_import = {}
    if os.path.exists(args.transiti):
        tdf = pd.read_csv(args.transiti)
        tdf["ts"] = pd.to_datetime(tdf["timestamp_utc"], utc=True)
        for zona in zone_ordinate:
            imp = tdf[tdf["in_zone"] == zona].groupby("ts")["flow_physical_mw"].sum()
            exp = tdf[tdf["out_zone"] == zona].groupby("ts")["flow_physical_mw"].sum()
            net = (imp - exp).reindex(all_ts, method="ffill")
            net_import[zona] = net

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")
    zone_zero = {"IT Sud", "IT Calabria", "IT Sicilia"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("white")

    for idx, zona in enumerate(zone_ordinate):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")

        if zona in load.columns and zona in gen_tot.columns:
            ts = load.index
            l = load[zona].fillna(0).values
            g = gen_tot[zona].fillna(0).values
            if zona in net_import:
                ni = net_import[zona].fillna(0).values
                g2 = g + ni
            else:
                g2 = g
            ax.plot(ts, l, color="black", lw=1.4, label="carico", zorder=5)
            ax.plot(ts, g2, color="#555555", lw=1.4, ls="-", label="produzione + net import", zorder=5)
            ax.fill_between(ts, g2, l, where=(g2 >= l), color="#2e8b57", alpha=0.25,
                            label="surplus", interpolate=True)
            ax.fill_between(ts, g2, l, where=(g2 < l), color="#c00000", alpha=0.25,
                            label="deficit", interpolate=True)
            ax.set_ylim(bottom=0)

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

    ax_bl = axes[1, 0]
    ax_bl.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax_bl.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")

    ax = axes[1, 1]
    ax.axis("off")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([0], [0], color="black", lw=1.4, label="carico"),
               Line2D([0], [0], color="#555555", lw=1.4, label="produzione + net import"),
               Patch(facecolor="#2e8b57", alpha=0.25, label="surplus (prod+net > carico)"),
               Patch(facecolor="#c00000", alpha=0.25, label="deficit (prod+net < carico)"),
               Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="ore a prezzo zero")]
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Periodo:\n12/11→13/11/2026\n(48h, UTC)\n"
                       "Fonte: ENTSO-E\n(A65+A75)+A11\n"
                       "Dato orario,\n"
                       "estrapolato (IT)",
            ha="right", va="bottom", fontsize=7, color="#555555",
            transform=ax.transAxes, linespacing=1.0,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", lw=0.6))

    fig.suptitle("Surplus adj per zona — ENTSO-E — 12/11 → 13/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
