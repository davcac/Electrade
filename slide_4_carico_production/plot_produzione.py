#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_produzione.py - SLIDE 4, STEP 2: legge il CSV prodotto da scarica_entsoe.py
e produce il grafico a 7 pannelli (generazione impilata per fonte + carico).

Non richiede il token ENTSO-E: lavora solo sul CSV.

Uso:
  python "presentazione lunedì 23/slide_4_per_fonte/plot_produzione.py"
  python "presentazione lunedì 23/slide_4_per_fonte/plot_produzione.py" --csv dati/carico_produzione_48h.csv
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

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
    ap = argparse.ArgumentParser(description="Grafico slide 4 da CSV (step 2)")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--out", default=os.path.join(GRAFICI, "01_produzione_carico_7zone.png"),
                    help="percorso del PNG di output")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit(
            "CSV non trovato: %s\nLancia prima scarica_entsoe.py (step 1) per crearlo." % args.csv
        )

    df = pd.read_csv(args.csv)
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True).dt.tz_convert(ROME)

    zone_ordinate = ["IT Nord", "IT Centro-Nord", "IT Centro-Sud", "IT Sud",
                     "IT Calabria", "IT Sicilia", "IT Sardegna"]

    load = (df[df["source"] == "load"]
            .pivot_table(index="ts", columns="zone", values="mw", aggfunc="mean"))
    gen = df[df["source"] != "load"].copy()
    gen["fonte"] = gen["source"].map(lambda s: "solare" if s == "solar"
                                     else ("eolico" if s == "wind" else "resto"))
    gen = gen.pivot_table(index=["zone", "ts"], columns="fonte", values="mw", aggfunc="sum")

    FONTE_COLORI = {"solare": "#f2c14e", "eolico": "#4c9f70", "resto": "#8d9db6"}

    zero_ts = pd.date_range("2026-11-13 10:00", periods=5, freq="h", tz="Europe/Rome")
    zone_zero = {"IT Sud", "IT Calabria", "IT Sicilia"}

    fig, axes = plt.subplots(4, 2, figsize=(14, 12), dpi=150)
    fig.patch.set_facecolor("white")
    for idx, zona in enumerate(zone_ordinate):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        ax.set_facecolor("white")
        if zona in gen.index.get_level_values(0):
            g = gen.loc[zona]
            g = g.reindex(load.index)
            sol = g.get("solare", pd.Series(0, index=load.index)).fillna(0)
            eol = g.get("eolico", pd.Series(0, index=load.index)).fillna(0)
            rest = g.get("resto", pd.Series(0, index=load.index)).fillna(0)
            ax.stackplot(load.index, sol.values, eol.values, rest.values,
                         labels=["solare (A75)", "eolico (A75)", "resto (A75)"],
                         colors=[FONTE_COLORI["solare"], FONTE_COLORI["eolico"],
                                 FONTE_COLORI["resto"]], alpha=0.9)
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
               plt.Line2D([0], [0], marker="o", color="#c00000", lw=0, ms=5, label="ore a prezzo zero")]
    ax.legend(handles=handles, loc="upper center", fontsize=9, frameon=False,
              bbox_to_anchor=(0.5, 0.95))
    ax.text(0.98, 0.02, "Periodo: 12/11 \u2192 13/11/2026 (48h, UTC)\n"
                       "Fonte: ENTSO-E (A65+A75)\n"
                       "Punti rossi: ore a zero (Sud, Calabria, Sicilia)\n"
                       "Dato orario, estrapolato (IT)",
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
