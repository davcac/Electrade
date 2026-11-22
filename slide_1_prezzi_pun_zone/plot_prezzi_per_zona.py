# -*- coding: utf-8 -*-
"""
plot_prezzi_per_zona.py - SLIDE 1: 7 grafici, uno per zona, del prezzo orario MGP
(esclude il PUN Index GME), dal 1/1/2026 al 15/11/2026.

Input:  slide_1_prezzi/20260101_20261115_MGP_PrezziZonali.xlsx
Output: slide_1_prezzi/grafici/04_serie_per_zona.png

Uso:
  python slide_1_prezzi/plot_prezzi_per_zona.py
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
OUT = os.path.join(HERE, "grafici")
os.makedirs(OUT, exist_ok=True)

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
    z = pd.read_excel(os.path.join(HERE, "20260101_20261115_MGP_PrezziZonali.xlsx"))
    z["ts"] = _ts_locale(z)
    z = z.rename(columns=COLONNE_ZONE)
    return z[["ts"] + ORDINE_ZONE].sort_values("ts").reset_index(drop=True)


def main():
    df = leggi()
    print("righe: %d  periodo: %s -> %s" % (len(df), df["ts"].min(), df["ts"].max()))

    fig, axes = plt.subplots(4, 2, figsize=(16, 12), dpi=150, sharex=True)
    fig.patch.set_facecolor("white")

    # ordine dei pannelli: 4 colonne x 2 righe, l'ultimo (in basso a destra) per la legenda
    posizioni = [(r, c) for r in range(4) for c in range(2)]
    zone_pannelli = ORDINE_ZONE  # 7 zone

    for idx, zona in enumerate(zone_pannelli):
        r, c = posizioni[idx]
        ax = axes[r, c]
        ax.set_facecolor("white")
        s = df[zona]
        ax.plot(df["ts"], s, color=COLORI[zona], lw=0.9, alpha=0.9, zorder=2)
        ax.axhline(0, color="#808080", lw=0.6, zorder=1)
        # banda attorno allo zero per evidenziare le ore a prezzo zero
        ax.axhspan(-2, 2, color="#fde9e9", alpha=0.7, zorder=1)
        # rug delle ore a prezzo zero
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
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # ultimo pannello (in basso a destra): legenda + nota
    ax = axes[3, 1]
    ax.axis("off")
    handles = [plt.Line2D([0], [0], color=COLORI[z], lw=2, label=z) for z in ORDINE_ZONE]
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 1.0), ncol=2)
    ax.text(0.5, 0.02, "Periodo: 01/01/2026 \u2192 15/11/2026 (UTC)\n"
                       "Granularit\u00e0: oraria (24 h/giorno)\n"
                       "Banda rossa: ore a prezzo zero (= 0 \u20ac/MWh)\n"
                       "Il PUN Index GME \u00e8 escluso\n(vedi 01_serie_prezzi_mgp.png)",
            ha="center", va="bottom", fontsize=8, color="#555555",
            transform=ax.transAxes, linespacing=1.2)

    fig.suptitle("Prezzo orario zonale MGP per zona \u2014 01/01/2026 \u2192 15/11/2026 (UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.autofmt_xdate(rotation=30, ha="right")

    out = os.path.join(OUT, "04_serie_per_zona.png")
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out)


if __name__ == "__main__":
    main()
