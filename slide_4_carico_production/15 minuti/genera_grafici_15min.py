#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rigenera i grafici slide 4 con marker basati sui prezzi MGP esatti a 15 minuti.

I dati A65/A75 restano quelli ENTSO-E a 15 minuti già presenti nel progetto;
qui cambia solo l'evidenziazione del prezzo zero: un tick rosso per ogni MTU
con prezzo esattamente pari a zero, per zona. Tutti gli output restano in questa
sottocartella e non sovrascrivono i grafici orari del livello superiore.
"""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
PARENT = BASE / "slide_4_carico_production"
PRICE_CSV = BASE / "slide_2_scelta_evento_p_zero" / "15 minuti" / "dati" / "prezzi_zonali_15min_48h.csv"
LOAD_CSV = PARENT / "dati" / "carico_produzione_48h.csv"
OUT = HERE / "grafici"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PARENT))

from plot_produzione import read_production_and_load, NET_COLOR, NET_LABEL
from plot_surplus import ZERO_PRICE_ZONES, COMPARISON_Y_TICKS
from scarica_entsoe import ZONES

ZONE_NAMES = {"IT Nord": "Nord", "IT Centro-Nord": "Centro Nord", "IT Centro-Sud": "Centro Sud",
              "IT Sud": "Sud", "IT Calabria": "Calabria", "IT Sicilia": "Sicilia", "IT Sardegna": "Sardegna"}
FONTE_COLORI = {"solare": "#f2c14e", "eolico": "#4c9f70", "resto": "#8d9db6"}
UTC = "UTC"


def price_zero_times():
    if not PRICE_CSV.is_file():
        raise SystemExit("Prezzi normalizzati 15 min non trovati; esegui prima slide 2/15 minuti/genera_prezzi_15min.py")
    p = pd.read_csv(PRICE_CSV)
    p["ts"] = pd.to_datetime(p["timestamp_utc"], utc=True)
    return {zone: pd.DatetimeIndex(p.loc[p[zone] == 0, "ts"]) for zone in ZONE_NAMES.values()}


def convert_indexes_utc(load, gen, net_generation):
    load = load.copy()
    load.index = load.index.tz_convert(UTC)
    net_generation = net_generation.copy()
    net_generation.index = net_generation.index.tz_convert(UTC)
    gen = gen.reset_index()
    gen["ts"] = pd.to_datetime(gen["ts"], utc=True)
    gen = gen.set_index(["zone", "ts"]).sort_index()
    return load, gen, net_generation


def add_zero_ticks(ax, times):
    if len(times):
        ax.scatter(times, np.zeros(len(times)), marker="|", color="#c00000", s=75,
                   linewidths=1.2, zorder=8, clip_on=False,
                   transform=ax.get_xaxis_transform())


def set_time_axis(ax, *, labels=False):
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=UTC))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m", tz=UTC))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20], tz=UTC))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M", tz=UTC))
    ax.tick_params(axis="x", which="both", labelbottom=labels, length=3)
    if labels:
        for label in ax.get_xticklabels(minor=True):
            label.set_fontsize(7)
            label.set_rotation(45)
            label.set_ha("right")


def format_grid_axes(ax, zone, zero_map, row_count=4):
    ax.set_title(ZONE_NAMES[zone], fontsize=11, fontweight="bold", pad=6)
    ax.set_ylabel("MW", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0)
    add_zero_ticks(ax, zero_map.get(zone, []))
    set_time_axis(ax, labels=False)


def save_grid(fig, axes, title, handles, output, text):
    ax = axes[-1, 1]
    ax.axis("off")
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, text, ha="right", va="bottom", fontsize=7,
            color="#555555", transform=ax.transAxes, linespacing=1.05,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cccccc", lw=0.6))
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.savefig(output, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", output)


def plot_generation(load, gen, netgen, zero_map):
    fig, axes = plt.subplots(4, 2, figsize=(14, 12), dpi=150)
    fig.patch.set_facecolor("white")
    for idx, zone in enumerate(ZONES):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")
        if zone in gen.index.get_level_values("zone"):
            g = gen.loc[zone].reindex(load.index, columns=list(FONTE_COLORI)).fillna(0)
            ax.stackplot(load.index, *g[list(FONTE_COLORI)].to_numpy().T,
                         labels=["solare (A75)", "eolico (A75)", "resto (A75)"],
                         colors=list(FONTE_COLORI.values()), alpha=0.9)
        if zone in load.columns:
            ax.plot(load.index, load[zone], color="black", lw=1.6, label="carico (A65)", zorder=5)
            # A75 netto degli assorbimenti di accumulo (B10, B25, B32)
            ax.plot(load.index, netgen[zone].reindex(load.index), color=NET_COLOR, lw=1.7,
                    ls="--", label=NET_LABEL, zorder=7)
        format_grid_axes(ax, zone, zero_map)
    handles = [Line2D([0], [0], color=FONTE_COLORI["solare"], lw=6, label="solare (A75)"),
               Line2D([0], [0], color=FONTE_COLORI["eolico"], lw=6, label="eolico (A75)"),
               Line2D([0], [0], color=FONTE_COLORI["resto"], lw=6, label="resto (A75)"),
               Line2D([0], [0], color="black", lw=2, label="carico (A65)"),
               Line2D([0], [0], color=NET_COLOR, lw=2, ls="--", label=NET_LABEL),
               Line2D([0], [0], color="#c00000", marker="|", lw=0, markersize=9,
                      label="intervalli con prezzo esattamente zero")]
    save_grid(fig, axes, "Produzione A75 e generazione netta per zona - ENTSO-E - 15 min UTC", handles,
              OUT / "01_produzione_carico_7zone_15min.png",
              "Consegna: 12-13/11/2026 (CET)\nAsse temporale: UTC\nMarker: ogni MTU con prezzo GME esattamente zero")


def plot_balance(load, supply, zones, zero_map, output, title, scale=None):
    nrows = (len(zones) + 1) // 2
    fig, axes = plt.subplots(nrows, 2, figsize=(14, max(8, 3 * nrows)), dpi=150, squeeze=False)
    fig.patch.set_facecolor("white")
    for idx, zone in enumerate(zones):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")
        if zone in load.columns and zone in supply.columns:
            l = load[zone].to_numpy()
            p = supply[zone].reindex(load.index).to_numpy()
            bal = p - l
            ax.plot(load.index, l, color="black", lw=1.6, label="carico (A65)", zorder=5)
            ax.plot(load.index, p, color=NET_COLOR, lw=1.7, ls="--", label=NET_LABEL, zorder=7)
            ax.fill_between(load.index, p, l, where=bal > 0, color="#2e8b57", alpha=0.35,
                            label="surplus", interpolate=True)
            ax.fill_between(load.index, p, l, where=bal < 0, color="#c00000", alpha=0.35,
                            label="deficit", interpolate=True)
            if scale is not None:
                ax.set_ylim(0, scale)
            else:
                ax.set_ylim(bottom=0)
        format_grid_axes(ax, zone, zero_map)
    # right-bottom slot for legend
    ax = axes[-1, 1]
    ax.axis("off")
    handles = [Line2D([0], [0], color="black", lw=1.6, label="carico (A65)"),
               Line2D([0], [0], color=NET_COLOR, lw=1.7, ls="--", label=NET_LABEL),
               Patch(facecolor="#2e8b57", alpha=0.35, label="surplus"),
               Patch(facecolor="#c00000", alpha=0.35, label="deficit"),
               Line2D([0], [0], color="#c00000", marker="|", lw=0, markersize=9,
                      label="intervalli con prezzo esattamente zero")]
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Consegna: 12-13/11/2026 (CET)\nAsse temporale: UTC\nDati e prezzi: 15 minuti",
            ha="right", va="bottom", fontsize=7, color="#555555", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cccccc", lw=0.6))
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.savefig(output, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", output)


def plot_surplus_line(load, netgen, zero_map):
    zones = list(ZONES)
    fig, axes = plt.subplots(4, 2, figsize=(14, 12), dpi=150)
    fig.patch.set_facecolor("white")
    for idx, zone in enumerate(zones):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        if zone in netgen.columns and zone in load.columns:
            balance = netgen[zone].reindex(load.index).fillna(0).to_numpy() - load[zone].fillna(0).to_numpy()
            ax.plot(load.index, balance, color=NET_COLOR, lw=1.7, ls="--",
                    label="surplus = A75 netto - carico A65", zorder=5)
            ax.fill_between(load.index, balance, 0, where=balance >= 0, color="#2e8b57", alpha=0.35, interpolate=True)
            ax.fill_between(load.index, balance, 0, where=balance < 0, color="#c00000", alpha=0.35, interpolate=True)
            ax.axhline(0, color="#555555", lw=0.8, ls="--")
        format_grid_axes(ax, zone, zero_map)
    ax = axes[3, 1]
    ax.axis("off")
    handles = [Line2D([0], [0], color=NET_COLOR, lw=1.7, ls="--", label="Surplus = A75 netto - carico A65"),
               Patch(facecolor="#2e8b57", alpha=0.35, label="surplus"),
               Patch(facecolor="#c00000", alpha=0.35, label="deficit"),
               Line2D([0], [0], color="#c00000", marker="|", lw=0, markersize=9, label="prezzo zero (MGP 15 min)")]
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Surplus = immissioni A75 - assorbimenti accumuli (B10/B25/B32) - carico A65\nRisoluzione: 15 minuti",
            ha="right", va="bottom", fontsize=7, color="#555555", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cccccc", lw=0.6))
    fig.suptitle("Surplus netto (A75 al netto degli accumuli - A65) - 15 min UTC", fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")
    path = OUT / "03_surplus_linea_7zone_15min.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", path)

def plot_macrozone(load, netgen, zero_map):
    zones = list(ZERO_PRICE_ZONES)
    l = load[zones].sum(axis=1, min_count=len(zones))
    p = netgen[zones].sum(axis=1, min_count=len(zones))
    bal = p - l
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.plot(load.index, l, color="black", lw=1.6, label="carico macrozona", zorder=5)
    ax.plot(load.index, p, color=NET_COLOR, lw=1.7, ls="--", label=NET_LABEL + " (macrozona)", zorder=7)
    ax.fill_between(load.index, p, l, where=bal > 0, color="#2e8b57", alpha=0.35, label="surplus", interpolate=True)
    ax.fill_between(load.index, p, l, where=bal < 0, color="#c00000", alpha=0.35, label="deficit", interpolate=True)
    # If any constituent zone is at zero, mark the aggregated macrozone's corresponding QH.
    merged = sorted(set().union(*(set(zero_map.get(z, [])) for z in ZERO_PRICE_ZONES)))
    add_zero_ticks(ax, pd.DatetimeIndex(merged))
    ax.set_ylabel("MW")
    ax.set_title("Macrozona Sud + Calabria + Sicilia - carico vs produzione fisica (15 min UTC)", fontweight="bold")
    ax.grid(axis="y", color="#e8e8e8", lw=0.5)
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=UTC))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m", tz=UTC))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 4, 8, 12, 16, 20], tz=UTC))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M", tz=UTC))
    ax.tick_params(axis="x", which="both", labelbottom=True, rotation=30)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    path = OUT / "05_surplus_macrozone_15min.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", path)


def main():
    if not PRICE_CSV.is_file():
        raise SystemExit("Esegui prima slide 2/15 minuti/genera_prezzi_15min.py")
    prices = pd.read_csv(PRICE_CSV)
    prices["timestamp_utc"] = pd.to_datetime(prices["timestamp_utc"], utc=True)
    zero_map = {internal: pd.DatetimeIndex(prices.loc[prices[label] == 0, "timestamp_utc"])
                for internal, label in ZONE_NAMES.items()}

    load, gen, netgen = read_production_and_load(str(LOAD_CSV))
    load.index = load.index.tz_convert(UTC)
    netgen.index = netgen.index.tz_convert(UTC)
    gen = gen.reset_index()
    gen["ts"] = pd.to_datetime(gen["ts"], utc=True)
    gen = gen.set_index(["zone", "ts"]).sort_index()

    plot_generation(load, gen, netgen, zero_map)
    plot_balance(load, netgen, list(ZONES), zero_map, OUT / "02_surplus_7zone_15min.png",
                 "Carico vs produzione A75 netta degli accumuli - 15 min UTC")
    plot_balance(load, netgen, list(ZERO_PRICE_ZONES), zero_map, OUT / "02_surplus_3zone_15min.png",
                 "Carico vs produzione A75 netta degli accumuli - 3 zone, 15 min UTC",
                 scale=COMPARISON_Y_TICKS[-1])
    plot_surplus_line(load, netgen, zero_map)
    plot_macrozone(load, netgen, zero_map)


if __name__ == "__main__":
    main()
