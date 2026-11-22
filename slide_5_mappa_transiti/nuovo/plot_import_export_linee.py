#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_import_export_linee.py - SLIDE 5/nuovo: linee orarie import/export + net import.

Un unico grafico (3 pannelli, uno per zona) con:
  - linee di import da ciascuna zona vicina (scambi programmati A09, orario)
  - linee di export verso ciascuna zona vicina (scambi programmati A09, orario)
  - una linea di net import fisico (A11, somma confini, orario)
Finestra 48 ore (12-13/11/2026, UTC).

Uso:
  python slide_5_mappa_transiti/nuovo/plot_import_export_linee.py
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
DEFAULT_CSV = os.path.join(os.path.dirname(HERE), "dati", "transiti_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
os.makedirs(GRAFICI, exist_ok=True)

ZONES = ["IT Sud", "IT Calabria", "IT Sicilia"]

# colori per vicino
NEIGHBOR_COLORS = {
    "IT Centro-Sud": "#1f77b4",
    "IT Calabria": "#ff7f0e",
    "IT Sicilia": "#2ca02c",
    "Grecia": "#9467bd",
    "Malta": "#8c564b",
    "Grecia (XGRE)": "#e377c2",
}


def main():
    ap = argparse.ArgumentParser(description="Linee import/export/net import (slide 5 nuovo)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso CSV transiti")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "import_export_linee_48h.png"),
                    help="percorso PNG output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s\nEsegui prima scarica_transiti_entsoe.py." % args.csv)

    df = pd.read_csv(args.csv)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    zero_ts = pd.date_range("2026-11-13 09:00", periods=5, freq="h", tz="UTC")

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), dpi=150, sharex=True)
    fig.patch.set_facecolor("white")

    for idx, zona in enumerate(ZONES):
        ax = axes[idx]
        ax.set_facecolor("white")

        # pallini rossi sulle 5 ore a prezzo zero
        ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30, zorder=6,
                   clip_on=False, transform=ax.get_xaxis_transform())

        # vicini della zona
        neighbors = sorted(set(df[df["out_zone"] == zona]["in_zone"].tolist() +
                             df[df["in_zone"] == zona]["out_zone"].tolist()))

        # import lines (scheduled in->zona)
        for nb in neighbors:
            sub = df[(df["out_zone"] == nb) & (df["in_zone"] == zona)].sort_values("timestamp_utc")
            if not sub.empty:
                color = NEIGHBOR_COLORS.get(nb, "#7f7f7f")
                ax.plot(sub["timestamp_utc"], sub["scheduled_mw"], color=color, lw=1.2,
                        ls="-", label="import da %s (A09)" % nb.replace("IT ", ""), zorder=3)

        # export lines (scheduled zona->vicino)
        for nb in neighbors:
            sub = df[(df["out_zone"] == zona) & (df["in_zone"] == nb)].sort_values("timestamp_utc")
            if not sub.empty:
                color = NEIGHBOR_COLORS.get(nb, "#7f7f7f")
                ax.plot(sub["timestamp_utc"], sub["scheduled_mw"], color=color, lw=1.2,
                        ls="--", label="export verso %s (A09)" % nb.replace("IT ", ""), zorder=3)

        # net import fisico: sum(in) - sum(out) per ora
        ts_all = sorted(df["timestamp_utc"].unique())
        net_series = []
        for ts in ts_all:
            imp = df[(df["in_zone"] == zona) & (df["timestamp_utc"] == ts)]["flow_physical_mw"].sum()
            exp = df[(df["out_zone"] == zona) & (df["timestamp_utc"] == ts)]["flow_physical_mw"].sum()
            net_series.append(imp - exp)
        ax.plot(ts_all, net_series, color="black", lw=2.0, ls="-",
                label="net import (A11)", zorder=5)

        ax.axhline(0, color="#555555", lw=0.8, ls=":", zorder=2)
        ax.set_title(zona.replace("IT ", ""), fontsize=11, fontweight="bold", pad=6)
        ax.set_ylabel("MW", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0)
        ax.grid(axis="y", color="#e0e0e0", lw=0.4, alpha=0.6)
        ax.legend(loc="upper left", fontsize=7, frameon=True, facecolor="white",
                  edgecolor="#cccccc", ncol=2)

    # asse X sull'ultimo pannello
    ax = axes[-1]
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

    fig.suptitle("Import / Export / Net import per zona \u2014 12/11 \u2192 13/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
