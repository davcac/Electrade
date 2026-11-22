#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_surplus_adj_macrozone.py - SLIDE 5/nuovo: surplus adj per la macrozona.

Identico a 04_surplus_adj_3zone.png ma per la macrozona Sud+Calabria+Sicilia aggregata.
Carico (nera) vs produzione + net import (grigia), area verde/rossa.

Uso:
  python slide_5_mappa_transiti/nuovo/plot_surplus_adj_macrozone.py
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
BASE = os.path.dirname(HERE)
DEFAULT_SURPLUS_CSV = os.path.join(BASE, "..", "slide_4_carico_production", "dati", "carico_produzione_48h.csv")
DEFAULT_TRANSITI_CSV = os.path.join(HERE, "..", "dati", "transiti_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None


def main():
    ap = argparse.ArgumentParser(description="Surplus adj macrozona (slide 5)")
    ap.add_argument("--surplus-csv", default=DEFAULT_SURPLUS_CSV, help="CSV carico/produzione slide 4")
    ap.add_argument("--transiti-csv", default=DEFAULT_TRANSITI_CSV, help="CSV transiti slide 5")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "05_surplus_adj_macrozone.png"),
                    help="percorso PNG output")
    args = ap.parse_args()

    if not os.path.exists(args.surplus_csv):
        raise SystemExit("CSV surplus non trovato: %s" % args.surplus_csv)

    df = pd.read_csv(args.surplus_csv)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    zone_macro = ["IT Sud", "IT Calabria", "IT Sicilia"]
    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    gen = df[df["source"] != "load"].copy()
    gen_tot = gen.pivot_table(index="ts", columns="zone", values="mw", aggfunc="sum")

    load_macro = load[zone_macro].sum(axis=1)
    gen_macro = gen_tot[zone_macro].sum(axis=1)
    all_ts = load_macro.index.union(gen_macro.index)
    load_macro = load_macro.reindex(all_ts)
    gen_macro = gen_macro.reindex(all_ts)

    # net import per la macrozona (somma flussi esterni)
    net_import = pd.Series(0.0, index=all_ts)
    if os.path.exists(args.transiti_csv):
        tdf = pd.read_csv(args.transiti_csv)
        tdf["ts"] = pd.to_datetime(tdf["timestamp_utc"], utc=True)
        external = ["IT Sud -> IT Centro-Sud", "IT Centro-Sud -> IT Sud",
                    "IT Sud -> Grecia", "Grecia -> IT Sud",
                    "IT Sud -> Grecia (XGRE)", "Grecia (XGRE) -> IT Sud",
                    "IT Sicilia -> Malta", "Malta -> IT Sicilia"]
        sub = tdf[tdf["border"].isin(external)]
        imp = sub[sub["in_zone"].isin(zone_macro)].groupby("ts")["flow_physical_mw"].sum()
        exp = sub[sub["out_zone"].isin(zone_macro)].groupby("ts")["flow_physical_mw"].sum()
        net = (imp - exp).reindex(all_ts, method="ffill")
        net_import = net.fillna(0)

    ts = load_macro.index
    l = load_macro.fillna(0).values
    g = gen_macro.fillna(0).values
    ni = net_import.values
    g2 = g + ni

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")

    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(ts, l, color="black", lw=1.6, label="carico (macrozona)", zorder=5)
    ax.plot(ts, g2, color="#555555", lw=1.6, ls="-", label="produzione + net import (macrozona)", zorder=5)
    ax.fill_between(ts, g2, l, where=(g2 >= l), color="#2e8b57", alpha=0.35,
                    label="surplus", interpolate=True)
    ax.fill_between(ts, g2, l, where=(g2 < l), color="#c00000", alpha=0.35,
                    label="deficit", interpolate=True)
    ax.axhline(0, color="#555555", lw=0.8, ls="--", zorder=2)
    ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30,
               zorder=6, clip_on=False, transform=ax.get_xaxis_transform())

    ax.set_ylabel("MW", fontsize=9)
    ax.set_title("Macrozona Sud+Calabria+Sicilia \— surplus adj (surplus + net import)", fontsize=12,
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
               Line2D([0], [0], color="#555555", lw=1.6, label="produzione + net import"),
               Patch(facecolor="#2e8b57", alpha=0.35, label="surplus"),
               Patch(facecolor="#c00000", alpha=0.35, label="deficit"),
               Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="ore a prezzo zero")]
    ax.legend(handles=handles, loc="lower right", fontsize=8, frameon=True,
              facecolor="white", edgecolor="#cccccc")

    fig.suptitle("Surplus adj macrozona \— ENTSO-E \— 12/11 \→ 13/11/2026 (UTC)",
                 fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
