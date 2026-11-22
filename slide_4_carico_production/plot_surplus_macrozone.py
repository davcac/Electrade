#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Saldo fisico di Sud, Calabria e Sicilia, prima degli scambi esterni."""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from plot_produzione import DEFAULT_CSV, GRAFICI, NET_COLOR, NET_LABEL, read_production_and_load
from plot_surplus import ZERO_PRICE_ZONES


def read_macrozone_series(csv_path, a75_dir=None):
    load, _, production = read_production_and_load(csv_path, a75_dir)
    zones = list(ZERO_PRICE_ZONES)
    macro_load = load.reindex(columns=zones).sum(axis=1, min_count=len(zones))
    macro_production = production.reindex(columns=zones).sum(axis=1, min_count=len(zones))
    return macro_load, macro_production


def plot_macrozone_balance(load, supply, *, output, title, supply_label=NET_LABEL,
                           area_labels=("Surplus", "Deficit"), scale_reference=None):
    ts = load.index
    demand = load.to_numpy()
    available = supply.reindex(ts).to_numpy()
    balance = available - demand

    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(ts, demand, color="black", lw=1.6, label="Carico (A65)", zorder=5)
    ax.plot(ts, available, color=NET_COLOR, lw=1.7, ls="--", label=supply_label, zorder=5)
    ax.fill_between(ts, available, demand, where=(balance > 0), color="#2e8b57", alpha=0.35,
                    label=area_labels[0], interpolate=True)
    ax.fill_between(ts, available, demand, where=(balance < 0), color="#c00000", alpha=0.35,
                    label=area_labels[1], interpolate=True)

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")
    ax.axhline(0, color="#555555", lw=0.8, ls="--", zorder=2)
    ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30, label="Ore a prezzo zero",
               zorder=6, clip_on=False, transform=ax.get_xaxis_transform())

    ax.set_ylabel("MW", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0)
    if scale_reference is not None:
        reference_load, reference_supply = scale_reference
        reference_index = reference_load.index
        reference_values = pd.concat([reference_load, reference_supply.reindex(reference_index)])
        ax.dataLim.intervaly = (min(0.0, reference_values.min()), max(0.0, reference_values.max()))
        ax.autoscale_view(scalex=False)
        ax.set_xlim(min(reference_index.min(), zero_ts.min()), max(reference_index.max(), zero_ts.max()))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20]))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for label in ax.get_xticklabels(minor=True):
        label.set_fontsize(7)
        label.set_rotation(45)
        label.set_ha("right")

    ax.legend(loc="lower right", fontsize=8, frameon=True,
              facecolor="white", edgecolor="#cccccc")
    ax.set_title(f"{title}\nSud, Calabria e Sicilia · ENTSO-E · 12–13/11/2026 (UTC)",
                 fontsize=13, fontweight="bold", pad=10)
    fig.tight_layout()
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", output)


def main():
    ap = argparse.ArgumentParser(description="Saldo fisico di Sud, Calabria e Sicilia")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "05_surplus_macrozone.png"),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    load, production = read_macrozone_series(args.csv, args.a75_dir)
    plot_macrozone_balance(load, production, output=args.out, title="Saldo fisico prima degli scambi")


if __name__ == "__main__":
    main()
