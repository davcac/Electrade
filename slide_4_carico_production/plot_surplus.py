#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_surplus.py - saldo fisico per zona.

Usa le stesse serie della slide 8: carico A65 dal CSV e immissioni e
assorbimenti dagli XML A75. Produce grafici/02_surplus_7zone.png con l'area
tra la produzione al netto degli assorbimenti degli accumuli e il carico,
verde per il saldo positivo e rossa per quello negativo.

Uso:
  python slide_4_carico_production/plot_surplus.py
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

from plot_produzione import DEFAULT_CSV, GRAFICI, NET_COLOR, NET_LABEL, read_production_and_load
from scarica_entsoe import ZONES

ZERO_PRICE_ZONES = ("IT Sud", "IT Calabria", "IT Sicilia")
COMPARISON_Y_TICKS = tuple(range(0, 6001, 1000))


def plot_zonal_balance(load, supply, *, zones, output, title="Saldo fisico zonale",
                       supply_label=NET_LABEL, datasets="A65+A75",
                       balance_caption="Saldo = immissioni − assorbimenti degli accumuli − carico",
                       y_ticks=None, x_limits=None):
    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome").tz_convert("UTC")
    rows = (len(zones) + 2) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(14, max(8, 3 * rows)), dpi=150, squeeze=False)
    fig.patch.set_facecolor("white")

    for idx, zona in enumerate(zones):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")

        if zona in load.columns and zona in supply.columns:
            ts = load.index
            demand = load[zona].to_numpy()
            net = supply[zona].reindex(ts).to_numpy()
            balance = net - demand
            ax.plot(ts, demand, color="black", lw=1.6, label="Carico (A65)", zorder=5)
            ax.plot(ts, net, color=NET_COLOR, lw=1.7, ls="--", label=supply_label, zorder=5)
            ax.fill_between(ts, net, demand, where=(balance > 0), color="#2e8b57", alpha=0.35,
                            label="surplus", interpolate=True)
            ax.fill_between(ts, net, demand, where=(balance < 0), color="#c00000", alpha=0.35,
                            label="deficit", interpolate=True)

        ax.set_title(zona.replace("IT ", ""), fontsize=11, fontweight="bold", pad=6)
        ax.set_ylabel("MW", fontsize=9)
        if y_ticks is None:
            ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
        else:
            ax.set_yticks(y_ticks)
            ax.set_ylim(y_ticks[0], y_ticks[-1])
        if zona in ZERO_PRICE_ZONES:
            ax.scatter(zero_ts, [0] * len(zero_ts), color="#c00000", s=30,
                       zorder=6, clip_on=False, transform=ax.get_xaxis_transform())
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0)
        if x_limits is not None:
            ax.set_xlim(*x_limits)
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        minor_hours = mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20])
        ax.xaxis.set_minor_locator(minor_hours)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", which="both", labelbottom=False)

    # solo il pannello in basso a sinistra mostra tutte le etichette
    ax_bl = axes[-1, 0]
    ax_bl.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax_bl.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")

    # ultimo pannello: legenda + testo
    ax = axes[-1, 1]
    ax.axis("off")
    handles = [Line2D([0], [0], color="black", lw=1.6, label="Carico (A65)"),
               Line2D([0], [0], color=NET_COLOR, lw=1.7, ls="--", label=supply_label),
               Patch(facecolor="#2e8b57", alpha=0.35, label="Surplus (saldo positivo)"),
               Patch(facecolor="#c00000", alpha=0.35, label="Deficit (saldo negativo)"),
               Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="Ore a prezzo zero")]
    ax.legend(handles=handles, loc="upper center", fontsize=9, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Periodo: 12/11 \u2192 13/11/2026 (48h, UTC)\n"
                       f"Fonte: ENTSO-E ({datasets})\n{balance_caption}",
            ha="right", va="bottom", fontsize=7, color="#555555",
            transform=ax.transAxes, linespacing=1.1,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.6))
    fig.suptitle(f"{title} \u2014 ENTSO-E \u2014 12/11 \u2192 13/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", output)


def main(*, zones=tuple(ZONES), output_name="02_surplus_7zone.png"):
    ap = argparse.ArgumentParser(description="Saldo fisico per zona")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--out", default=os.path.join(GRAFICI, output_name),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    load, _, net_generation = read_production_and_load(args.csv, args.a75_dir)
    plot_zonal_balance(load, net_generation, zones=zones, output=args.out)


if __name__ == "__main__":
    main()
