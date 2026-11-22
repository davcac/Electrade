#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_produzione.py - legge il carico A65 dal CSV e le serie A75 dagli XML.
Mostra le immissioni per fonte, la produzione al netto degli assorbimenti
degli accumuli (G - A) e il carico A65 per le sette zone.

Non richiede il token ENTSO-E. Gli XML A75 sono cercati accanto al CSV,
oppure nella cartella indicata con --a75-dir.

Uso:
  python slide_4_carico_production/plot_produzione.py
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from scarica_entsoe import STORAGE_PSR_TYPES, ZONES, parse_load_or_generation

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "dati", "carico_produzione_48h.csv")
GRAFICI = os.path.join(HERE, "grafici")
NET_COLOR = "#542477"
NET_LABEL = f"Immissioni A75 − assorbimenti A75 ({', '.join(sorted(STORAGE_PSR_TYPES))})"

try:
    from zoneinfo import ZoneInfo
    ROME = ZoneInfo("Europe/Rome")
except ImportError:
    ROME = None


def read_a75(directory, zones):
    rows = []
    for zone in zones:
        name = f"A75_{zone.replace(' ', '_')}.xml"
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            raise SystemExit(f"XML A75 non trovato: {path}. Indica la cartella con --a75-dir.")
        zone_rows = parse_load_or_generation(path, separate_absorption=True)
        if not zone_rows:
            raise SystemExit(f"Nessun dato A75 trovato in {path}.")
        rows.extend(zone_rows)
    data = pd.DataFrame(rows, columns=["zone", "source", "ts", "mw"])
    data["ts"] = pd.to_datetime(data["ts"], utc=True).dt.tz_convert(ROME)
    return data


def read_production_and_load(csv_path, a75_dir=None):
    if not os.path.exists(csv_path):
        raise SystemExit(
            "CSV non trovato: %s\nLancia prima scarica_entsoe.py (step 1) per crearlo." % csv_path
        )

    df = pd.read_csv(csv_path)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True).dt.tz_convert(ROME)

    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    a75_dir = a75_dir or os.path.dirname(os.path.abspath(csv_path))
    a75 = read_a75(a75_dir, [zone for zone in ZONES if zone in load.columns])
    absorption = (a75[a75["source"] == "storage_absorption"]
                  .pivot_table(index="ts", columns="zone", values="mw", aggfunc="sum"))
    gen = a75[~a75["source"].isin(["load", "storage_absorption", "other_absorption"])].copy()
    gen["fonte"] = gen["source"].map(lambda s: "solare" if s == "solar"
                                     else ("eolico" if s == "wind" else "resto"))
    gen = gen.pivot_table(index=["zone", "ts"], columns="fonte", values="mw", aggfunc="sum")
    generation = gen.sum(axis=1, min_count=1).unstack("zone").reindex(index=load.index)
    absorbed = absorption.reindex(index=generation.index, columns=generation.columns).fillna(0)
    return load, gen, generation - absorbed


def main():
    ap = argparse.ArgumentParser(description="Grafico della produzione e del carico della slide 8")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "01_produzione_carico_7zone.png"),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    load, gen, net_generation = read_production_and_load(args.csv, args.a75_dir)

    FONTE_COLORI = {"solare": "#f2c14e", "eolico": "#4c9f70", "resto": "#8d9db6"}

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome")
    zone_zero = {"IT Sud", "IT Calabria", "IT Sicilia"}

    fig, axes = plt.subplots(4, 2, figsize=(14, 12), dpi=150)
    fig.patch.set_facecolor("white")
    for idx, zona in enumerate(ZONES):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")
        if zona in gen.index.get_level_values(0):
            g = gen.loc[zona].reindex(index=load.index, columns=list(FONTE_COLORI))
            ax.stackplot(load.index, *g.fillna(0).to_numpy().T,
                         labels=["solare (A75)", "eolico (A75)", "resto (A75)"],
                         colors=list(FONTE_COLORI.values()), alpha=0.9)
            ax.plot(load.index, net_generation[zona].values, color=NET_COLOR, lw=1.7, ls="--",
                    label=NET_LABEL, zorder=7)
        if zona in load.columns:
            ax.plot(load.index, load[zona].values, color="black", lw=1.6,
                    label="carico (A65)", zorder=5)
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
        # nessuna etichetta sull'asse X per i pannelli superiori
        ax.tick_params(axis="x", which="both", labelbottom=False)

    # solo il pannello in basso a sinistra mostra tutte le etichette (date + ore)
    ax_bl = axes[3, 0]
    ax_bl.tick_params(axis="x", which="both", labelbottom=True, length=3)
    for lbl in ax_bl.get_xticklabels(minor=True):
        lbl.set_fontsize(7)
        lbl.set_rotation(45)
        lbl.set_ha("right")

    ax = axes[3, 1]
    ax.axis("off")
    handles = [plt.Line2D([0], [0], color=FONTE_COLORI["solare"], lw=6, label="solare (A75)"),
               plt.Line2D([0], [0], color=FONTE_COLORI["eolico"], lw=6, label="eolico (A75)"),
               plt.Line2D([0], [0], color=FONTE_COLORI["resto"], lw=6, label="resto (A75)"),
               plt.Line2D([0], [0], color="black", lw=2, label="carico (A65)"),
               plt.Line2D([0], [0], color=NET_COLOR, lw=2, ls="--", label=NET_LABEL),
               plt.Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="ore a prezzo zero")]
    ax.legend(handles=handles, loc="upper center", fontsize=9, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Periodo: 12/11 \u2192 13/11/2026 (48h, UTC)\n"
                       "Fonte: ENTSO-E (A65+A75)\n"
                       "Punti rossi: ore a zero (Sud, Calabria, Sicilia)\n"
                       "Dati in MW per intervallo",
            ha="right", va="bottom", fontsize=7, color="#555555",
            transform=ax.transAxes, linespacing=1.1,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.6))

    fig.suptitle("Carico e produzione fisica per zona \u2014 ENTSO-E \u2014 12/11 \u2192 13/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", args.out)


if __name__ == "__main__":
    main()
