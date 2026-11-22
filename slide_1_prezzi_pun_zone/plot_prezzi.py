# -*- coding: utf-8 -*-
"""
plot_prezzi.py - SLIDE 1: grafico dei prezzi MGP (PUN Index GME + 7 zone) dal
1/1/2026 al 15/11/2026, a partire dai due file scaricati a mano dal sito GME.

Input (nella stessa cartella):
  20260101_20261115_MGP_PrezziZonali.xlsx  (Date, Hour, Calabria, Central-northern Italy,
                                             Centeral-southern Italy, North, Sardegna,
                                             Sicilia, Southern-Italy, ...)
  20260101_20261115_PUN.xlsx                (Date, Hour, €/MWh = PUN Index GME)

Output in grafici/:
  01_serie_prezzi_mgp.png   - serie orarie delle 8 grandezze, con le ore a zero evidenziate
  02_heatmap_ore_zero.png    - heatmap zona x mese, conteggio ore a prezzo zero
  03_statistiche_zero.txt   - conteggi, sequenze consecutive, min/max, per zona

Uso:
  python slide_1_prezzi/plot_prezzi.py
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
    "PUN Index GME": "#1a1a1a",
    "Nord": "#1f4e79",
    "Centro Nord": "#2e75b6",
    "Centro Sud": "#70ad47",
    "Sud": "#ed7d31",
    "Calabria": "#ffc000",
    "Sicilia": "#7030a0",
    "Sardegna": "#00b0b0",
}


def _ts_locale(df):
    """Timestamp locale (Europe/Rome) per ogni riga: la giornata di mercato parte
    dalla mezzanotte locale e procede per ore consecutive di tempo reale, quindi
    il cambio dell'ora legale (23 o 25 ore) e' gestito automaticamente."""
    ts = []
    for _, row in df.iterrows():
        d = row["Date"]
        giorno_str = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else pd.to_datetime(str(d).strip(), format="%d/%m/%Y").strftime("%Y-%m-%d")
        istante = pd.Timestamp(giorno_str, tz=ROMA) + pd.Timedelta(hours=int(row["Hour"]) - 1)
        ts.append(istante)
    return pd.Series(ts, index=df.index)


def leggi():
    z = pd.read_excel(os.path.join(HERE, "20260101_20261115_MGP_PrezziZonali.xlsx"))
    p = pd.read_excel(os.path.join(HERE, "20260101_20261115_PUN.xlsx"))
    z["ts"] = _ts_locale(z)
    p["ts"] = _ts_locale(p)
    z = z.rename(columns=COLONNE_ZONE)
    df = z[["ts"] + ORDINE_ZONE].merge(
        p[["ts", "\u20ac/MWh"]].rename(columns={"\u20ac/MWh": "PUN Index GME"}),
        on="ts", how="left", validate="one_to_one")
    df = df.sort_values("ts").reset_index(drop=True)
    return df


def sequenze_zero(series):
    """Restituisce le sequenze (inizio, fine, lunghezza) di ore a prezzo <= 0."""
    seq = []
    inizio = None
    for i, v in enumerate(series):
        if v <= 0:
            if inizio is None:
                inizio = i
        else:
            if inizio is not None:
                seq.append((inizio, i - 1, i - inizio))
                inizio = None
    if inizio is not None:
        seq.append((inizio, len(series) - 1, len(series) - inizio))
    return seq


def main():
    df = leggi()
    print("righe: %d  periodo: %s -> %s" % (len(df), df["ts"].min(), df["ts"].max()))
    print("zone: %s" % ", ".join(ORDINE_ZONE))

    # ------------------------------------------------------------------ grafico A
    fig, ax = plt.subplots(figsize=(16, 7), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.axhspan(-2, 2, color="#fde9e9", alpha=0.7, zorder=1, label="_nolegend_")

    for nome in ORDINE_ZONE:
        ax.plot(df["ts"], df[nome], color=COLORI[nome], lw=1.0, alpha=0.85,
                label=nome, zorder=2)
    ax.plot(df["ts"], df["PUN Index GME"], color=COLORI["PUN Index GME"], lw=2.2,
            label="PUN Index GME", zorder=3)

    zero_mask = (df[ORDINE_ZONE] <= 0).any(axis=1)
    ax.plot(df.loc[zero_mask, "ts"], np.zeros(zero_mask.sum()) - 8,
            marker="|", color="#c00000", ms=6, lw=0, label="ore a prezzo zero (almeno una zona)",
            zorder=4)

    ax.axhline(0, color="#808080", lw=0.8, zorder=1)
    ax.set_ylabel("Prezzo (\u20ac/MWh)", fontsize=11)
    ax.set_title("Prezzi orari MGP zonali e PUN Index GME \u2014 01/01/2026 \u2192 15/11/2026",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(True, axis="y", color="#e8e8e8", lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
    fig.autofmt_xdate(rotation=30, ha="right")

    ax.legend(loc="upper left", fontsize=8.5, ncol=3, frameon=True,
              facecolor="white", edgecolor="#cccccc")
    fig.tight_layout()
    out_a = os.path.join(OUT, "01_serie_prezzi_mgp.png")
    fig.savefig(out_a, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out_a)

    # ------------------------------------------------------------------ heatmap
    df["mese"] = df["ts"].dt.tz_convert(ROMA).dt.to_period("M").astype(str)
    mesi = sorted(df["mese"].unique())
    mat = np.zeros((len(ORDINE_ZONE), len(mesi)), dtype=int)
    for j, z in enumerate(ORDINE_ZONE):
        for i, m in enumerate(mesi):
            sub = df.loc[(df["mese"] == m) & (df[z] <= 0)]
            mat[j, i] = len(sub)

    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=160)
    fig.patch.set_facecolor("white")
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_xticks(range(len(mesi)))
    ax.set_xticklabels([m[5:7] + "/" + m[2:4] for m in mesi], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(ORDINE_ZONE)))
    ax.set_yticklabels(ORDINE_ZONE, fontsize=9)
    ax.set_title("Ore a prezzo zero per zona e mese (prezzo orario \u2264 0 \u20ac/MWh)", fontsize=12,
                 fontweight="bold", pad=8)
    for j in range(len(ORDINE_ZONE)):
        for i in range(len(mesi)):
            v = mat[j, i]
            if v > 0:
                ax.text(i, j, str(v), ha="center", va="center", fontsize=7,
                        color="white" if v > mat.max() * 0.55 else "black")
    cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("ore a prezzo zero", fontsize=9)
    fig.tight_layout()
    out_b = os.path.join(OUT, "02_heatmap_ore_zero.png")
    fig.savefig(out_b, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out_b)

    # ------------------------------------------------------------------ statistiche
    log = os.path.join(OUT, "03_statistiche_zero.txt")
    with open(log, "w", encoding="utf-8") as fh:
        fh.write("STATISTICHE SLIDE 1 - prezzi MGP 01/01/2026 -> 15/11/2026\n")
        fh.write("=" * 70 + "\n")
        fh.write("righe: %d   periodo: %s -> %s\n\n" % (len(df), df["ts"].min(), df["ts"].max()))
        fh.write("per zona: n.osservazioni, ore a prezzo 0, ore negative, min, max, media\n")
        for z in ORDINE_ZONE + ["PUN Index GME"]:
            v = df[z].dropna()
            fh.write("  %-14s : %6d oss, zero=%4d, negative=%4d, min=%8.2f, max=%8.2f, media=%8.2f\n"
                     % (z, len(v), (v <= 0).sum(), (v < 0).sum(), v.min(), v.max(), v.mean()))
        fh.write("\nsequenze consecutive di ore a prezzo zero (solo >= 3 ore)\n")
        for z in ORDINE_ZONE:
            seq = [s for s in sequenze_zero(df[z].values) if s[2] >= 3]
            seq.sort(key=lambda s: -s[2])
            if not seq:
                fh.write("  %-14s : nessuna sequenza >= 3 ore\n" % z)
                continue
            fh.write("  %-14s : %d sequenze, la piu' lunga %d ore (dal %s)\n"
                     % (z, len(seq), seq[0][2],
                        df["ts"].iloc[seq[0][0]].strftime("%d/%m/%Y %H:%M")))
            for inizio, fine, lun in seq[:5]:
                fh.write("      %s -> %s  (%d ore, min=%.2f)\n"
                         % (df["ts"].iloc[inizio].strftime("%d/%m %H:%M"),
                            df["ts"].iloc[fine].strftime("%d/%m %H:%M"), lun,
                            df[z].iloc[inizio:fine + 1].min()))
        fh.write("\nconfronto PUN Index GME vs colonna 'Italia' del file zonale (sanity check)\n")
        z2b = pd.read_excel(os.path.join(HERE, "20260101_20261115_MGP_PrezziZonali.xlsx"))
        z2b["_k"] = z2b["Date"].astype(str) + "|" + z2b["Hour"].astype(str)
        dfb = pd.read_excel(os.path.join(HERE, "20260101_20261115_PUN.xlsx"))
        dfb["_k"] = dfb["Date"].astype(str) + "|" + dfb["Hour"].astype(str)
        merged = dfb[["_k", "\u20ac/MWh"]].merge(z2b[["_k", "Italia"]], on="_k", how="inner")
        diff = (merged["\u20ac/MWh"] - merged["Italia"]).abs()
        fh.write("  righe confrontate: %d  differenza massima: %.4f  media: %.4f\n"
                 % (len(merged), diff.max(), diff.mean()))
    print("scritto:", log)


if __name__ == "__main__":
    main()
