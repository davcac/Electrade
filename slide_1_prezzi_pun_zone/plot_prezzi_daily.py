# -*- coding: utf-8 -*-
"""
plot_prezzi_daily.py - SLIDE 1 (variante giornaliera): stessi 3 file della
versione oraria, ma sui prezzi giornalieri (media del giorno) del MGP.

Input (nella stessa cartella):
  20260101_20261115_MGP_PrezziZonali_daily.xlsx  (Date, Italia, Calabria, ...)
  20260101_20261115_PUN_daily.xlsx                (Date, €/MWh = PUN Index GME)

Output in grafici/:
  01_serie_prezzi_mgp_DAILY.png   - serie giornaliere delle 8 grandezze
  02_heatmap_prezzi_DAILY.png     - heatmap zona x mese, prezzo medio giornaliero
  03_statistiche_zero_DAILY.txt   - statistiche giornaliere, per zona

Uso:
  python slide_1_prezzi/plot_prezzi_daily.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "grafici")
os.makedirs(OUT, exist_ok=True)

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


def leggi():
    z = pd.read_excel(os.path.join(HERE, "20260101_20261115_MGP_PrezziZonali_daily.xlsx"))
    p = pd.read_excel(os.path.join(HERE, "20260101_20261115_PUN_daily.xlsx"))
    z["ts"] = pd.to_datetime(z["Date"], format="%d/%m/%Y")
    p["ts"] = pd.to_datetime(p["Date"], format="%d/%m/%Y")
    z = z.rename(columns=COLONNE_ZONE)
    df = z[["ts"] + ORDINE_ZONE].merge(
        p[["ts", "\u20ac/MWh"]].rename(columns={"\u20ac/MWh": "PUN Index GME"}),
        on="ts", how="left", validate="one_to_one")
    df = df.sort_values("ts").reset_index(drop=True)
    return df


def main():
    df = leggi()
    print("righe: %d  periodo: %s -> %s" % (len(df), df["ts"].min().date(), df["ts"].max().date()))

    # ------------------------------------------------------------------ grafico A
    fig, ax = plt.subplots(figsize=(16, 7), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for nome in ORDINE_ZONE:
        ax.plot(df["ts"], df[nome], color=COLORI[nome], lw=1.1, alpha=0.85,
                label=nome, marker="o", ms=2.2, zorder=2)
    ax.plot(df["ts"], df["PUN Index GME"], color=COLORI["PUN Index GME"], lw=2.2,
            label="PUN Index GME", marker="o", ms=2.6, zorder=3)

    # giorni con prezzo medio molto basso (<= 30 €/MWh) evidenziati
    basso = (df[ORDINE_ZONE].min(axis=1) <= 30)
    if basso.any():
        ax.plot(df.loc[basso, "ts"], df.loc[basso, "PUN Index GME"],
                marker="o", color="#c00000", ms=5, lw=0, label="giorni con almeno una zona \u2264 30 \u20ac/MWh",
                zorder=4)

    ax.axhline(0, color="#808080", lw=0.8, zorder=1)
    ax.set_ylabel("Prezzo medio giornaliero (\u20ac/MWh)", fontsize=11)
    ax.set_title("Prezzi giornalieri MGP zonali e PUN Index GME \u2014 01/01/2026 \u2192 15/11/2026",
                 fontsize=13, fontweight="bold", pad=10)
    ax.grid(True, axis="y", color="#e8e8e8", lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30, ha="right")

    ax.legend(loc="upper left", fontsize=8.5, ncol=3, frameon=True,
              facecolor="white", edgecolor="#cccccc")
    fig.tight_layout()
    out_a = os.path.join(OUT, "01_serie_prezzi_mgp_DAILY.png")
    fig.savefig(out_a, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out_a)

    # ------------------------------------------------------------------ heatmap
    df["mese"] = df["ts"].dt.to_period("M").astype(str)
    mesi = sorted(df["mese"].unique())
    mat = np.zeros((len(ORDINE_ZONE), len(mesi)))
    for j, z in enumerate(ORDINE_ZONE):
        for i, m in enumerate(mesi):
            mat[j, i] = df.loc[df["mese"] == m, z].mean()

    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=160)
    fig.patch.set_facecolor("white")
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_xticks(range(len(mesi)))
    ax.set_xticklabels([m[5:7] + "/" + m[2:4] for m in mesi], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(ORDINE_ZONE)))
    ax.set_yticklabels(ORDINE_ZONE, fontsize=9)
    ax.set_title("Prezzo medio giornaliero per zona e mese (\u20ac/MWh)", fontsize=12,
                 fontweight="bold", pad=8)
    for j in range(len(ORDINE_ZONE)):
        for i in range(len(mesi)):
            v = mat[j, i]
            ax.text(i, j, "%.0f" % v, ha="center", va="center", fontsize=7,
                    color="white" if v > mat.max() * 0.55 else "black")
    cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("prezzo medio giornaliero (\u20ac/MWh)", fontsize=9)
    fig.tight_layout()
    out_b = os.path.join(OUT, "02_heatmap_prezzi_DAILY.png")
    fig.savefig(out_b, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("scritto:", out_b)

    # ------------------------------------------------------------------ statistiche
    log = os.path.join(OUT, "03_statistiche_zero_DAILY.txt")
    with open(log, "w", encoding="utf-8") as fh:
        fh.write("STATISTICHE SLIDE 1 - prezzi GIORNALIERI MGP 01/01/2026 -> 15/11/2026\n")
        fh.write("=" * 70 + "\n")
        fh.write("righe: %d   periodo: %s -> %s\n\n" % (len(df), df["ts"].min().date(), df["ts"].max().date()))
        fh.write("per zona: n.giorni, min, max, media, giorni con prezzo <= 0, <= 20, <= 50\n")
        for z in ORDINE_ZONE + ["PUN Index GME"]:
            v = df[z].dropna()
            fh.write("  %-14s : %4d gg, min=%8.2f, max=%8.2f, media=%8.2f, <=0=%3d, <=20=%3d, <=50=%3d\n"
                     % (z, len(v), v.min(), v.max(), v.mean(),
                        (v <= 0).sum(), (v <= 20).sum(), (v <= 50).sum()))
        fh.write("\nconfronto PUN Index GME vs colonna 'Italia' del file zonale (sanity check)\n")
        z2 = pd.read_excel(os.path.join(HERE, "20260101_20261115_MGP_PrezziZonali_daily.xlsx"))
        z2["_k"] = z2["Date"].astype(str)
        dfb = pd.read_excel(os.path.join(HERE, "20260101_20261115_PUN_daily.xlsx"))
        dfb["_k"] = dfb["Date"].astype(str)
        merged = dfb[["_k", "\u20ac/MWh"]].merge(z2[["_k", "Italia"]], on="_k", how="inner")
        diff = (merged["\u20ac/MWh"] - merged["Italia"]).abs()
        fh.write("  righe confrontate: %d  differenza massima: %.4f  media: %.4f\n"
                 % (len(merged), diff.max(), diff.mean()))
        fh.write("\nNOTA: il prezzo giornaliero e' la media del giorno. I giorni a prezzo\n")
        fh.write("esattamente zero non esistono sulla media (le ore a zero si contano\n")
        fh.write("sui dati orari: vedi grafici/01_serie_prezzi_mgp.png).\n")
    print("scritto:", log)


if __name__ == "__main__":
    main()
