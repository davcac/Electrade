#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_macrozone.py - SLIDE 5/nuovo: macrozona Sud+Calabria+Sicilia.

Un unico grafico con i flussi lordi commerciali (A09) per ciascun confine esterno
della macrozona (import/export) + linea nera del net import fisico (A11).
Finestra 48 ore (12-13/11/2026, UTC).

Uso:
  python slide_5_mappa_transiti/nuovo/plot_macrozone.py
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

# confini esterni della macrozona: (nome vicino, lista border out->in per export, lista border in->out per import)
EXTERNAL = {
    "Centro-Sud": {"export": ["IT Sud -> IT Centro-Sud"],
                   "import": ["IT Centro-Sud -> IT Sud"]},
    "Grecia": {"export": ["IT Sud -> Grecia", "IT Sud -> Grecia (XGRE)"],
               "import": ["Grecia -> IT Sud", "Grecia (XGRE) -> IT Sud"]},
    "Malta": {"export": ["IT Sicilia -> Malta"],
              "import": ["Malta -> IT Sicilia"]},
}

COLORS = {
    "Centro-Sud": "#1f77b4",
    "Grecia": "#9467bd",
    "Malta": "#8c564b",
}


def main():
    ap = argparse.ArgumentParser(description="Macrozona Sud+Calabria+Sicilia (slide 5 nuovo)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso CSV transiti")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "macrozone_48h.png"),
                    help="percorso PNG output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit("CSV non trovato: %s\nEsegui prima scarica_transiti_entsoe.py." % args.csv)

    df = pd.read_csv(args.csv)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    ts_all = sorted(df["timestamp_utc"].unique())

    fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # import lines (scheduled in->macrozona)
    for nb, info in EXTERNAL.items():
        color = COLORS[nb]
        # import = somma dei border import
        imp_series = None
        for b in info["import"]:
            sub = df[df["border"] == b].sort_values("timestamp_utc")
            if imp_series is None:
                imp_series = sub[["timestamp_utc", "scheduled_mw"]].copy()
            else:
                imp_series = imp_series.merge(sub[["timestamp_utc", "scheduled_mw"]],
                                             on="timestamp_utc", how="outer", suffixes=("", "_dup"))
                imp_series["scheduled_mw"] = imp_series["scheduled_mw"].fillna(0) + imp_series["scheduled_mw_dup"].fillna(0)
                imp_series = imp_series[["timestamp_utc", "scheduled_mw"]]
        if imp_series is not None and not imp_series.empty:
            ax.plot(imp_series["timestamp_utc"], imp_series["scheduled_mw"], color=color, lw=1.4,
                    ls="-", label="import da %s (A09)" % nb, zorder=3)

        # export lines (scheduled macrozona->out)
        exp_series = None
        for b in info["export"]:
            sub = df[df["border"] == b].sort_values("timestamp_utc")
            if exp_series is None:
                exp_series = sub[["timestamp_utc", "scheduled_mw"]].copy()
            else:
                exp_series = exp_series.merge(sub[["timestamp_utc", "scheduled_mw"]],
                                             on="timestamp_utc", how="outer", suffixes=("", "_dup"))
                exp_series["scheduled_mw"] = exp_series["scheduled_mw"].fillna(0) + exp_series["scheduled_mw_dup"].fillna(0)
                exp_series = exp_series[["timestamp_utc", "scheduled_mw"]]
        if exp_series is not None and not exp_series.empty:
            ax.plot(exp_series["timestamp_utc"], exp_series["scheduled_mw"], color=color, lw=1.4,
                    ls="--", label="export verso %s (A09)" % nb, zorder=3)

    # net import fisico: somma flow_physical in ingresso - uscita sui confini esterni
    net_series = []
    for ts in ts_all:
        imp = 0.0
        exp = 0.0
        for nb, info in EXTERNAL.items():
            for b in info["import"]:
                sub = df[(df["border"] == b) & (df["timestamp_utc"] == ts)]
                if not sub.empty:
                    imp += sub["flow_physical_mw"].iloc[0]
            for b in info["export"]:
                sub = df[(df["border"] == b) & (df["timestamp_utc"] == ts)]
                if not sub.empty:
                    exp += sub["flow_physical_mw"].iloc[0]
        net_series.append(imp - exp)
    ax.plot(ts_all, net_series, color="black", lw=2.2, ls="-",
            label="net import macrozona (A11)", zorder=5)

    ax.axhline(0, color="#555555", lw=0.8, ls=":", zorder=2)
    ax.set_ylabel("MW", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0)
    ax.grid(axis="y", color="#e0e0e0", lw=0.4, alpha=0.6)
    ax.legend(loc="upper left", fontsize=8, frameon=True, facecolor="white",
              edgecolor="#cccccc", ncol=2)

    # pallini rossi sulle 5 ore a prezzo zero
    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")
    ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=40, zorder=6,
               clip_on=False, transform=ax.get_xaxis_transform(), label="ore a prezzo zero")

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

    ax.set_title("Macrozona Sud + Calabria + Sicilia \u2014 Import/Export/Net import \u2014 12/11 \u2192 13/11/2026 (UTC)",
                 fontsize=13, fontweight="bold", pad=10)

    fig.tight_layout()
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
