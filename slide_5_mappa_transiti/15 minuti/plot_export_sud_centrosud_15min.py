#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Esportazione Sud-Centro-Sud a 15 minuti con NTC PT60 e marker prezzo zero.

Gli scambi programmati A09 sono quartorari; i limiti A61 restano orari e sono
mostrati a gradino. Le tacche rosse corrispondono agli MTU con prezzo GME Sud
esattamente pari a zero; l'asse x è UTC e la finestra di consegna è CET.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
TRANSITS = HERE / "dati" / "transiti_48h_15min.csv"
PRICES = PROJECT / "slide_2_scelta_evento_p_zero" / "15 minuti" / "dati" / "prezzi_zonali_15min_48h.csv"
OUT = HERE / "grafici" / "export_sud_centrosud_15min.png"
TARGET_BORDER = "IT Sud -> IT Centro-Sud"
GREECE_BORDER = "IT Sud -> Grecia"
UTC = "UTC"


def main():
    if not TRANSITS.is_file() or not PRICES.is_file():
        raise SystemExit("Mancano il CSV transiti o quello prezzi a 15 minuti.")

    flows = pd.read_csv(TRANSITS)
    prices = pd.read_csv(PRICES)
    target = flows.loc[flows["border"] == TARGET_BORDER].copy()
    greece = flows.loc[flows["border"] == GREECE_BORDER].copy()
    if len(target) != 192:
        raise SystemExit("Attesi 192 MTU per Sud-Centro-Sud; trovati %d." % len(target))
    if target["scheduled_mw"].isna().any() or target["ntc_mw"].isna().any():
        raise SystemExit("A09 o A61 incompleto per Sud-Centro-Sud.")
    if not target["ntc_resolution_min"].dropna().eq(60).all():
        raise SystemExit("La risoluzione A61 Sud-Centro-Sud non risulta PT60.")

    target["ts"] = pd.to_datetime(target["timestamp_utc"], utc=True)
    prices["ts"] = pd.to_datetime(prices["timestamp_utc"], utc=True)
    zeros = prices.loc[prices["Sud"] == 0, "ts"]
    if len(zeros) != 23:
        raise SystemExit("Attesi 23 MTU a prezzo Sud zero; trovati %d." % len(zeros))

    fig, ax = plt.subplots(figsize=(16, 7.1), dpi=160)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(target["ts"], target["scheduled_mw"], color="#ff7f0e", lw=1.45, ls="-.",
            label="Export programmato A09 (PT15)", zorder=3)
    ax.step(target["ts"], target["ntc_mw"], where="post", color="#2ca02c", lw=1.45, ls=":",
            label="NTC A61 Sud–Centro-Sud (PT60, a gradino)", zorder=2)

    if not greece.empty and greece["ntc_mw"].notna().any():
        greece["ts"] = pd.to_datetime(greece["timestamp_utc"], utc=True)
        ax.step(greece["ts"], greece["ntc_mw"], where="post", color="#9467bd", lw=1.2, ls=":",
                label="NTC A61 Sud–Grecia (PT60, a gradino)", zorder=2)

    ax.scatter(zeros, np.zeros(len(zeros)), marker="|", color="#c00000", s=95,
               linewidths=1.5, clip_on=False, zorder=7,
               transform=ax.get_xaxis_transform(),
               label="Prezzo Sud = 0 €/MWh (23 MTU, CET)")

    ts = target["ts"]
    end = ts.max() + pd.Timedelta(minutes=15)
    ax.set_xlim(ts.min(), end)
    ymax = max(target["ntc_mw"].max(), target["scheduled_mw"].max(), 1)
    ax.set_ylim(bottom=0, top=float(ymax) * 1.12)
    ax.set_ylabel("MW")
    ax.set_title("Export Sud → Centro-Sud e capacità NTC — 12–13 novembre 2026",
                 fontsize=14, fontweight="bold", pad=10)
    ax.grid(axis="y", color="#e3e3e3", lw=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz=UTC))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M", tz=UTC))
    ax.tick_params(axis="x", labelsize=8, rotation=30)
    ax.legend(loc="upper left", fontsize=8, frameon=True, ncol=2)
    fig.text(0.08, 0.025,
             "Consegna italiana CET (UTC+1); asse x UTC. Tacche rosse: inizio dei quarti d’ora con prezzo zonale Sud esattamente zero.",
             fontsize=8, color="#444444")
    fig.tight_layout(rect=[0.04, 0.07, 0.99, 0.96])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Grafico:", OUT)
    print("Marker prezzo zero:", len(zeros), "MTU; da", zeros.min(), "a", zeros.max())


if __name__ == "__main__":
    main()
