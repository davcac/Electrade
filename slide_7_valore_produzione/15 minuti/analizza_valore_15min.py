#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Valorizzazione solare Sud con prezzi MGP e produzione entrambi a 15 minuti.

Prezzo medio semplice: media temporale dei 192 prezzi quartorari.
Prezzo medio ponderato: sum(prezzo * energia solare del quarto)/sum(energia solare).
Energia di ogni quarto = potenza media A75 [MW] * 0.25 h.
"""
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PRICE_CSV = PROJECT / "slide_2_scelta_evento_p_zero" / "15 minuti" / "dati" / "prezzi_zonali_15min_48h.csv"
PRODUCTION_CSV = PROJECT / "slide_4_carico_production" / "dati" / "carico_produzione_48h.csv"
OUT_CSV = HERE / "dati" / "valorizzazione_quartoraria_sud.csv"
OUT_JSON = HERE / "dati" / "risultati_15min.json"
OUT_PNG = HERE / "grafici" / "valorizzazione_solare_sud_15min.png"


def main():
    if not PRICE_CSV.is_file():
        raise SystemExit("Prezzi a 15 minuti mancanti: esegui prima slide 2/15 minuti/genera_prezzi_15min.py")
    if not PRODUCTION_CSV.is_file():
        raise SystemExit("Produzione/carico ENTSO-E mancante: %s" % PRODUCTION_CSV)

    prices = pd.read_csv(PRICE_CSV)
    prices["ts"] = pd.to_datetime(prices["timestamp_utc"], utc=True)
    prices = prices[["ts", "timestamp_local", "Sud"]].rename(columns={"Sud": "price_eur_mwh"})

    production = pd.read_csv(PRODUCTION_CSV)
    production = production[(production["zone"] == "IT Sud") & (production["source"] == "solar")].copy()
    production["ts"] = pd.to_datetime(production["timestamp_utc"], utc=True)
    production = production[["ts", "mw"]].rename(columns={"mw": "solar_power_mw"})

    if prices["ts"].duplicated().any() or production["ts"].duplicated().any():
        raise SystemExit("Trovati timestamp duplicati: interrompo l'analisi.")
    data = prices.merge(production, on="ts", how="outer", validate="one_to_one")
    if len(data) != 192 or data[["price_eur_mwh", "solar_power_mw"]].isna().any().any():
        raise SystemExit("Prezzi e produzione devono allinearsi su 192 quarti d'ora senza lacune.")
    data = data.sort_values("ts").reset_index(drop=True)
    data["energy_mwh"] = data["solar_power_mw"] * 0.25
    data["value_eur"] = data["price_eur_mwh"] * data["energy_mwh"]
    data["price_zero"] = data["price_eur_mwh"] == 0
    data["price_negative"] = data["price_eur_mwh"] < 0

    total_energy = math.fsum(data["energy_mwh"])
    weighted_price = math.fsum(data["value_eur"]) / total_energy if total_energy else float("nan")
    mean_price = math.fsum(data["price_eur_mwh"]) / len(data)
    zero_energy = math.fsum(data.loc[data.price_zero, "energy_mwh"])
    summary = {
        "zona": "Sud", "fonte": "solare A75", "intervalli": 192,
        "inizio_utc": data["ts"].min().isoformat(),
        "fine_utc_esclusa": (data["ts"].max() + pd.Timedelta(minutes=15)).isoformat(),
        "prezzo_medio_aritmetico_15min_eur_mwh": mean_price,
        "prezzo_medio_ponderato_sulla_produzione_eur_mwh": weighted_price,
        "differenza_ponderato_meno_aritmetico_eur_mwh": weighted_price - mean_price,
        "differenza_percentuale": (weighted_price / mean_price - 1) * 100 if mean_price else None,
        "energia_solare_mwh": total_energy,
        "valore_teorico_eur": math.fsum(data["value_eur"]),
        "energia_solare_a_prezzo_esattamente_zero_mwh": zero_energy,
        "quota_energia_a_prezzo_zero_percento": 100 * zero_energy / total_energy if total_energy else None,
        "intervalli_prezzo_zero": int(data["price_zero"].sum()),
        "intervalli_prezzo_negativo": int(data["price_negative"].sum()),
        "definizione_media": "media aritmetica temporale dei 192 prezzi quartorari",
        "definizione_ponderata": "sum(prezzo_qh * energia_solare_qh) / sum(energia_solare_qh)",
        "nota": "Stima descrittiva ex-post; non è un ricavo contrattuale né un settlement MGP.",
    }

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    data.assign(timestamp_utc=data["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")).drop(columns="ts").to_csv(
        OUT_CSV, index=False, encoding="utf-8-sig")
    OUT_JSON.write_text(json.dumps({"riepilogo": summary}, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax1 = plt.subplots(figsize=(14, 5), dpi=150)
    ax1.plot(data.ts, data.price_eur_mwh, color="#7030a0", lw=1.3, label="Prezzo MGP Sud (€/MWh)")
    ax1.set_ylabel("€/MWh", color="#7030a0")
    ax1.tick_params(axis="y", labelcolor="#7030a0")
    ax2 = ax1.twinx()
    ax2.fill_between(data.ts, data.solar_power_mw, color="#f2c14e", alpha=0.35, label="Produzione solare A75 (MW)")
    ax2.set_ylabel("MW", color="#9a7300")
    ax2.tick_params(axis="y", labelcolor="#9a7300")
    zero = data.price_zero
    if zero.any():
        ax1.scatter(data.loc[zero, "ts"], data.loc[zero, "price_eur_mwh"], color="#c00000", s=18,
                    label="Prezzo esattamente zero", zorder=5)
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz="UTC"))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M", tz="UTC"))
    ax1.tick_params(axis="x", rotation=35, labelsize=8)
    h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax1.legend(h1+h2,l1+l2,loc="upper left",fontsize=8,ncol=2)
    fig.suptitle("Prezzo MGP e produzione solare Sud - 15 minuti (UTC)",fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_PNG,bbox_inches="tight",facecolor="white")
    plt.close(fig)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("CSV:", OUT_CSV)
    print("grafico:", OUT_PNG)


if __name__ == "__main__":
    main()
