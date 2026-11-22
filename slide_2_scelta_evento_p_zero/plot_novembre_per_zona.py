# -*- coding: utf-8 -*-
"""
plot_novembre_per_zona.py - SLIDE 2 (supporto): 7 grafici, uno per zona, del
prezzo orario MGP nel mese di novembre 2026 (01/11 -> 15/11), a partire dal
file zonale orario.

Input:  ../slide_1_prezzi_pun_zone/20260101_20261115_MGP_PrezziZonali.xlsx
Output: slide_2_evento/grafici/01_serie_per_zona_novembre.png

Uso:
  python slide_2_evento/plot_novembre_per_zona.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
INPUT = os.path.join(BASE, "slide_1_prezzi_pun_zone", "20260101_20261115_MGP_PrezziZonali.xlsx")
OUT_DIR = os.path.join(HERE, "grafici")
os.makedirs(OUT_DIR, exist_ok=True)

ROMA = ZoneInfo("Europe/Rome")

COLONNE_ZONE = {
    "North": "Nord",
    "Central-northern Italy": "Centro Nord",
    "Centeral-southern Italy": "Centro Sud",
    "Southern-Italy": "Sud",
    "Calabria": "Calabria",
    "Sicilia": "Sicilia",
    "Sardegna": "Sardegna",
}
ORDINE_ZONE = ["Nord", "Centro Nord", "Centro Sud", "Sud", "Calabria", "Sicilia", "Sardegna"]

COLORI = {
    "Nord": "#1f4e79",
    "Centro Nord": "#2e75b6",
    "Centro Sud": "#70ad47",
    "Sud": "#ed7d31",
    "Calabria": "#ffc000",
    "Sicilia": "#7030a0",
    "Sardegna": "#00b0b0",
}


def _ts_locale(df):
    ts = []
    for _, row in df.iterrows():
        d = row["Date"]
        giorno_str = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else pd.to_datetime(str(d).strip(), format="%d/%m/%Y").strftime("%Y-%m-%d")
        istante = pd.Timestamp(giorno_str, tz=ROMA) + pd.Timedelta(hours=int(row["Hour"]) - 1)
        ts.append(istante)
    return pd.Series(ts, index=df.index)


def leggi():
    z = pd.read_excel(INPUT)
    z["ts"] = _ts_locale(z)
    z = z.rename(columns=COLONNE_ZONE)
    df = z[["ts"] + ORDINE_ZONE].copy()
    # filtro novembre 2026
    df = df[(df["ts"] >= pd.Timestamp("2026-11-01", tz=ROMA)) &
            (df["ts"] < pd.Timestamp("2026-12-01", tz=ROMA))].sort_values("ts").reset_index(drop=True)
    return df


def main():
    df = leggi()
    print("righe: %d  periodo: %s -> %s" % (len(df), df["ts"].min(), df["ts"].max()))

    fig, axes = plt.subplots(4, 2, figsize=(16, 12), dpi=150)
    fig.patch.set_facecolor("white")

    posizioni = [(r, c) for r in range(4) for c in range(2)]
    for idx, zona in enumerate(ORDINE_ZONE):
        r, c = posizioni[idx]
        ax = axes[r, c]
        ax.set_facecolor("white")
        s = df[zona]
        ax.plot(df["ts"], s, color=COLORI[zona], lw=1.0, alpha=0.9, zorder=2)
        ax.axhline(0, color="#808080", lw=0.6, zorder=1)
        ax.axhspan(-2, 2, color="#fde9e9", alpha=0.7, zorder=1)
        zero = s <= 0
        if zero.any():
            ax.plot(df.loc[zero, "ts"], np.zeros(zero.sum()) - 6, marker="|",
                    color="#c00000", ms=5, lw=0, zorder=3)
        zero_n = int(zero.sum())
        ax.set_title("%s  (ore a zero: %d)" % (zona, zero_n), fontsize=11,
                     fontweight="bold", color=COLORI[zona], pad=6)
        ax.set_ylabel("\u20ac/MWh", fontsize=9)
        ax.grid(True, axis="y", color="#e8e8e8", lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 12]))

    ax = axes[3, 1]
    ax.axis("off")
    import matplotlib.lines as mlines
    handles = [mlines.Line2D([0], [0], color=COLORI[z], lw=2, label=z) for z in ORDINE_ZONE]
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 1.0), ncol=2)
    ax.text(0.5, 0.02, "Periodo: 01/11/2026 \u2192 15/11/2026\n"
                       "Granularit\u00e0: oraria (24 h/giorno)\n"
                       "Banda rossa: ore a prezzo zero (= 0 \u20ac/MWh)\n"
                       "Il PUN Index GME \u00e8 escluso",
            ha="center", va="bottom", fontsize=8, color="#555555",
            transform=ax.transAxes, linespacing=1.2)

    fig.suptitle("Prezzo orario zonale MGP per zona \u2014 novembre 2026 (01/11 \u2192 15/11) (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    out = os.path.join(OUT_DIR, "01_serie_per_zona_novembre.png")
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out)


if __name__ == "__main__":
    main()
