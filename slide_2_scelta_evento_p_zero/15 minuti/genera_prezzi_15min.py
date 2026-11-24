#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Normalizza e plotta i prezzi zonali MGP a 15 minuti del 12-13/11/2026.

Nel file GME Ora=1, Periodo=1 indica l'intervallo di consegna 00:00-00:15 CET.
Il grafico mostra i timestamp in UTC e marca soltanto i prezzi esattamente pari a zero.
Scrive un CSV tidy da riutilizzare nelle successive analisi a 15 minuti.
"""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
SOURCE = os.path.join(PARENT, "20261112_20261113_MGP_PrezziZonali_15min.xlsx")
OUT_CSV = os.path.join(HERE, "dati", "prezzi_zonali_15min_48h.csv")
OUT_PNG = os.path.join(HERE, "grafici", "prezzi_zonali_15min_48h.png")
LOCAL = ZoneInfo("Europe/Rome")
UTC = ZoneInfo("UTC")

ZONES = {
    "Nord": "Nord",
    "Centro Nord": "Centro Nord",
    "Centro Sud": "Centro Sud",
    "Sud": "Sud",
    "Calabria": "Calabria",
    "Sicilia": "Sicilia",
    "Sardegna": "Sardegna",
}
ORDER = list(ZONES)
COLORS = {
    "Nord": "#1f4e79", "Centro Nord": "#2e75b6", "Centro Sud": "#70ad47",
    "Sud": "#ed7d31", "Calabria": "#ffc000", "Sicilia": "#7030a0",
    "Sardegna": "#00b0b0",
}


def to_number(value):
    if pd.isna(value):
        raise ValueError("Prezzo mancante nel file GME")
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
    return float(value)


def read_prices():
    if not os.path.isfile(SOURCE):
        raise SystemExit("File GME 15 minuti non trovato: %s" % SOURCE)
    raw = pd.read_excel(SOURCE, sheet_name=0)
    required = {"Data", "Ora", "Periodo", *ZONES.values()}
    missing = required.difference(raw.columns)
    if missing:
        raise SystemExit("Colonne mancanti nel file GME: %s" % sorted(missing))
    if len(raw) != 192:
        raise SystemExit("Attese 192 righe quartorarie; trovate %d" % len(raw))

    rows = []
    for _, row in raw.iterrows():
        date = pd.to_datetime(row["Data"], dayfirst=True).date()
        hour = int(row["Ora"])
        period = int(row["Periodo"])
        quarter = (period - 1) % 4
        if not 1 <= hour <= 24 or period != (hour - 1) * 4 + quarter + 1:
            raise SystemExit("Ora/Periodo incoerenti: Ora=%s, Periodo=%s" % (hour, period))
        local_start = datetime(date.year, date.month, date.day, tzinfo=LOCAL)
        local_start += timedelta(hours=hour - 1, minutes=15 * quarter)
        record = {
            "timestamp_local": local_start.isoformat(),
            "timestamp_utc": local_start.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "ora_gme": hour,
            "periodo_gme": period,
        }
        for zone, column in ZONES.items():
            record[zone] = to_number(row[column])
        rows.append(record)

    df = pd.DataFrame(rows).sort_values("timestamp_utc").reset_index(drop=True)
    if df["timestamp_utc"].duplicated().any():
        raise SystemExit("Timestamp duplicati nel file prezzi.")
    expected = pd.date_range("2026-11-11 23:00", periods=192, freq="15min", tz="UTC")
    actual = pd.DatetimeIndex(pd.to_datetime(df["timestamp_utc"], utc=True))
    if list(actual) != list(expected):
        raise SystemExit("I timestamp non coprono esattamente le 48 ore previste.")
    return df


def plot_prices(df):
    timestamps = pd.to_datetime(df["timestamp_utc"], utc=True)
    fig, axes = plt.subplots(4, 2, figsize=(16, 12), dpi=150)
    fig.patch.set_facecolor("white")
    positions = [(r, c) for r in range(4) for c in range(2)]

    for idx, zone in enumerate(ORDER):
        r, c = positions[idx]
        ax = axes[r, c]
        ax.set_facecolor("white")
        values = df[zone].to_numpy(dtype=float)
        ax.plot(timestamps, values, color=COLORS[zone], lw=1.1, alpha=0.9,
                zorder=2, marker="o", ms=2)
        ax.axhline(0, color="#808080", lw=0.6, zorder=1)
        ax.axhspan(-2, 2, color="#fde9e9", alpha=0.7, zorder=1)
        zero = values == 0
        if zero.any():
            ax.scatter(timestamps[zero], np.zeros(zero.sum()), marker="|", color="#c00000",
                       s=65, linewidths=1.2, zorder=4, clip_on=False,
                       transform=ax.get_xaxis_transform())
        ax.set_title("%s (intervalli esattamente a zero: %d)" % (zone, int(zero.sum())),
                     fontsize=10, fontweight="bold", color=COLORS[zone], pad=5)
        ax.set_ylabel("€/MWh", fontsize=8)
        ax.grid(True, axis="y", color="#e8e8e8", lw=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim(timestamps.iloc[0], timestamps.iloc[-1] + pd.Timedelta(minutes=15))
        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz=UTC))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M", tz=UTC))
        ax.tick_params(axis="x", labelsize=7, rotation=45)

    ax = axes[3, 1]
    ax.axis("off")
    handles = [Line2D([0], [0], color=COLORS[z], lw=1.8, label=z) for z in ORDER]
    handles.append(Line2D([0], [0], color="#c00000", marker="|", lw=0,
                          markersize=8, label="Prezzo esattamente 0 €/MWh"))
    ax.legend(handles=handles, loc="upper center", fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, 1.0), ncol=2)
    ax.text(0.5, 0.02,
            "Consegna: 12-13/11/2026 (ora italiana)\nAsse temporale: UTC\n"
            "Granularità: 15 minuti (192 intervalli)",
            ha="center", va="bottom", fontsize=8, color="#555555",
            transform=ax.transAxes, linespacing=1.2)
    fig.suptitle("Prezzi zonali MGP ogni 15 minuti — consegna 12-13 novembre 2026 (asse UTC)",
                 fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.autofmt_xdate(rotation=30, ha="right")
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    fig.savefig(OUT_PNG, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    df = read_prices()
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    plot_prices(df)
    print("CSV:", OUT_CSV, "(%d intervalli)" % len(df))
    print("grafico:", OUT_PNG)
    for zone in ORDER:
        values = df[zone].to_numpy(dtype=float)
        print("%-12s zero=%d negative=%d" % (zone, int((values == 0).sum()), int((values < 0).sum())))


if __name__ == "__main__":
    main()
