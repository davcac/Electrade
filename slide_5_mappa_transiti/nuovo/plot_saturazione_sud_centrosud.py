#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_saturazione_sud_centrosud.py - SLIDE 5/nuovo: saturazione confine Sud-CentroSud.

2 pannelli (export Sud->CentroSud e import CentroSud->Sud), 48 ore (UTC).
Per ciascuno: linea limite GME, flusso fisico A11, scheduled A09, NTC A61.
Area rossa dove il flusso fisico >= 90% del limite (saturazione).

Uso:
  python slide_5_mappa_transiti/nuovo/plot_saturazione_sud_centrosud.py
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
DEFAULT_TRANSITI = os.path.join(os.path.dirname(HERE), "dati", "transitis_48h.csv")
DEFAULT_LIMITI = os.path.join(os.path.dirname(HERE), "dati", "limiti_transito_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

# correzione typo filename
DEFAULT_TRANSITI = os.path.join(os.path.dirname(HERE), "dati", "transiti_48h.csv")


def main():
    ap = argparse.ArgumentParser(description="Saturazione confine Sud-CentroSud (slide 5)")
    ap.add_argument("--transiti", default=DEFAULT_TRANSITI, help="CSV transiti")
    ap.add_argument("--limiti", default=DEFAULT_LIMITI, help="CSV limiti GME")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "export_sud_centrosud.png"),
                    help="PNG output")
    args = ap.parse_args()

    if not os.path.exists(args.transiti):
        raise SystemExit("CSV transiti non trovato: %s" % args.transiti)
    if not os.path.exists(args.limiti):
        raise SystemExit("CSV limiti non trovato: %s" % args.limiti)

    tdf = pd.read_csv(args.transiti)
    tdf["ts"] = pd.to_datetime(tdf["timestamp_utc"], utc=True)
    ldf = pd.read_csv(args.limiti)
    ldf["ts"] = pd.to_datetime(ldf["timestamp_utc"], utc=True)

    fig, axes = plt.subplots(1, 1, figsize=(14, 5), dpi=150)
    fig.patch.set_facecolor("white")

    directions = [("IT Sud -> IT Centro-Sud", "Export Sud \u2192 Centro-Sud")]

    for idx, (border, title) in enumerate(directions):
        ax = axes
        ax.set_facecolor("white")

        zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")

        sub_t = tdf[tdf["border"] == border].sort_values("ts")
        sub_l = ldf[ldf["border"] == border].sort_values("ts")

        if sub_t.empty:
            ax.text(0.5, 0.5, "nessun dato", ha="center", va="center", transform=ax.transAxes)
            continue

        ts = sub_t["ts"]
        ax.plot(ts, sub_t["scheduled_mw"].values, color="#ff7f0e", lw=1.2, ls="-.",
                label="scheduled A09 (day-ahead A01) (MW)", zorder=3)
        ax.plot(ts, sub_t["ntc_mw"].values, color="#2ca02c", lw=1.2, ls=":",
                label="NTC A61 (day-ahead) (MW)", zorder=3)

        # NTC Sud->Grecia (capacita' trascurabile)
        sub_g = tdf[tdf["border"] == "IT Sud -> Grecia"].sort_values("ts")
        if not sub_g.empty:
            ax.plot(sub_g["ts"], sub_g["ntc_mw"].values, color="#9467bd", lw=1.2, ls=":",
                    label="NTC Sud->Grecia", zorder=3)

        ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30, zorder=6,
                   clip_on=False, transform=ax.get_xaxis_transform())


        ax.set_title("Export Sud -> Centro-sud - 12/11 -> 13/11/2026 (UTC)", fontsize=12, fontweight="bold", pad=6)
        ax.set_ylabel("MW", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0)
        ax.grid(axis="y", color="#e0e0e0", lw=0.4, alpha=0.6)
        ax.legend(loc="upper left", fontsize=8, frameon=True, facecolor="white",
                  edgecolor="#cccccc", ncol=2)

    ax = axes
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    minor_hours = mdates.HourLocator(byhour=[0, 6, 12, 18])
    ax.xaxis.set_minor_locator(minor_hours)
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")


    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
