#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Curve aggregate di domanda e offerta GME per il periodo 38, 13/11/2026.

Le curve di merito usano le offerte semplici MTU15 e MTU60 del file GME.
I prodotti semplici di diversa durata possono incrociarsi nel coupling: i MW
MTU60 sono quindi presenti in ciascun quarto coperto, non divisi per quattro.
Le offerte a blocchi restano fuori dalla curva semplice e sono riepilogate a parte.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SOURCE = PROJECT / "DomandaOffertaME_20261113_38_MGP.xlsx"
OUT_DIR = HERE / "grafici"
DATA_DIR = HERE / "dati"
OUT_PNG = OUT_DIR / "domanda_offerta_macrozona_20261113_periodo38.png"
OUT_CSV = DATA_DIR / "curve_macrozona_20261113_periodo38.csv"

OFFERED_QTY = "Quantità offerta(MW)"
ACCEPTED_QTY = "Quantità accettata(MW)"
OFFERED_PRICE = "Prezzo offerto(€/MWh)"
ACCEPTED_PRICE = "Prezzo accettato(€/MWh)"
ZONE = "Mercato/Zona"


def number(value):
    """Parse GME decimals, including Italian thousands/decimal separators."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)
    text = str(value).strip().replace(".", "").replace(",", ".")
    return float(text)


def load_sheet(sheet_name):
    frame = pd.read_excel(SOURCE, sheet_name=sheet_name, dtype=str)
    for column in (OFFERED_QTY, ACCEPTED_QTY, OFFERED_PRICE, ACCEPTED_PRICE):
        frame[column] = frame[column].map(number)
    frame["MTU"] = pd.to_numeric(frame["MTU"], errors="raise").astype(int)
    frame["Intervallo"] = pd.to_numeric(frame["Intervallo"], errors="raise").astype(int)
    return frame


def curve_by_side(simple, side):
    """Aggregate equal-price orders and calculate positive cumulative MW."""
    curve = simple.loc[simple["Tipo"] == side].groupby(OFFERED_PRICE, as_index=False).agg(
        offered_mw=(OFFERED_QTY, "sum"),
        accepted_mw=(ACCEPTED_QTY, "sum"),
        mtu15_mw=(OFFERED_QTY, lambda s: s[simple.loc[s.index, "MTU"] == 15].sum()),
        mtu60_mw=(OFFERED_QTY, lambda s: s[simple.loc[s.index, "MTU"] == 60].sum()),
    )
    ascending = side == "OFF"
    curve = curve.sort_values(OFFERED_PRICE, ascending=ascending).reset_index(drop=True)
    curve["side"] = side
    curve["cumulative_mw"] = curve["offered_mw"].cumsum()
    return curve


def stairs(ax, curve, *, color, label):
    edges = np.r_[0.0, curve["cumulative_mw"].to_numpy(dtype=float)]
    values = curve[OFFERED_PRICE].to_numpy(dtype=float)
    # Draw only the horizontal merit-order steps; avoid artificial vertical
    # closures at the first and last quantities.
    ax.step(edges, np.r_[values, values[-1]], where="post", color=color,
            linewidth=1.65, label=label, zorder=3)


def format_block_summary(blocks):
    accepted = blocks.loc[blocks[ACCEPTED_QTY] > 0]
    if accepted.empty:
        return "Offerte a blocchi accettate: nessuna"
    parts = []
    for (side, mtu), group in accepted.groupby(["Tipo", "MTU"], sort=True):
        label = "BID" if side == "BID" else "OFF"
        parts.append("%s %.1f MW (MTU%d)" % (label, group[ACCEPTED_QTY].sum(), mtu))
    return "Blocchi accettati (separati dalle curve semplici): " + "; ".join(parts)


def main():
    if not SOURCE.is_file():
        raise SystemExit("File GME non trovato: %s" % SOURCE)

    simple = load_sheet("Offerte semplici")
    blocks = load_sheet("Offerte a blocchi")
    all_rows = pd.concat([simple, blocks], ignore_index=True)

    if set(all_rows["Data"].astype(str)) != {"13/11/2026"}:
        raise SystemExit("La data del file non corrisponde al 13/11/2026.")
    if set(all_rows["Intervallo"]) != {38}:
        raise SystemExit("Il file contiene intervalli diversi dal periodo 38.")
    if set(simple["MTU"]) - {15, 60}:
        raise SystemExit("Granularità MTU semplice inattesa: %s" % sorted(set(simple["MTU"])))
    if not simple.loc[simple["MTU"] == 15, "Durata intervallo"].astype(str).eq("09:15-09:30").all():
        raise SystemExit("Le offerte MTU15 non riportano tutte 09:15-09:30.")

    zones = sorted(set(all_rows[ZONE].dropna().astype(str)))
    if len(zones) != 1:
        raise SystemExit("Il file non contiene una sola macrozona: %s" % zones)

    # Per definizione GME, PREZZO_ACCETTATO è il prezzo accettato nella zona.
    settlements = sorted(set(all_rows[ACCEPTED_PRICE].dropna().astype(float)))
    if len(settlements) != 1:
        raise SystemExit("Prezzo accettato non univoco: %s" % settlements)
    settlement = settlements[0]

    supply = curve_by_side(simple, "OFF")
    demand = curve_by_side(simple, "BID")
    if supply.empty or demand.empty:
        raise SystemExit("Mancano offerte semplici BID o OFF.")

    # Compare the demand quantity at the settlement price with the supply
    # plateau at that price. For this aggregate macrozone they need not match:
    # the auction is coupled across zones and the exported orders are not a
    # closed, isolated market balance.
    clearing_mw = float(simple.loc[
        (simple["Tipo"] == "BID") & (simple[OFFERED_PRICE] >= settlement), OFFERED_QTY
    ].sum())
    supply_below = float(simple.loc[
        (simple["Tipo"] == "OFF") & (simple[OFFERED_PRICE] < settlement), OFFERED_QTY
    ].sum())
    supply_at_or_below = float(simple.loc[
        (simple["Tipo"] == "OFF") & (simple[OFFERED_PRICE] <= settlement), OFFERED_QTY
    ].sum())
    curves_meet_at_settlement = supply_below - 1e-6 <= clearing_mw <= supply_at_or_below + 1e-6

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    audit = pd.concat([supply, demand], ignore_index=True)
    audit = audit.rename(columns={OFFERED_PRICE: "price_eur_mwh"})[
        ["side", "price_eur_mwh", "offered_mw", "accepted_mw", "mtu15_mw", "mtu60_mw", "cumulative_mw"]
    ]
    audit.to_csv(OUT_CSV, index=False, encoding="utf-8-sig", float_format="%.3f")

    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=160)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    stairs(ax, supply, color="#c00000", label="Supply — offerte semplici")
    stairs(ax, demand, color="#0070c0", label="Demand — offerte semplici")

    ax.axhline(settlement, color="#333333", linestyle="--", linewidth=1.15,
               label="Settlement: %.2f €/MWh" % settlement, zorder=2)
    if curves_meet_at_settlement:
        ax.axvline(clearing_mw, color="#666666", linestyle=":", linewidth=0.9, zorder=1)
        ax.scatter([clearing_mw], [settlement], s=52, color="#f2c14e", edgecolor="#333333",
                   linewidth=0.8, zorder=6)
        settlement_note = "Settlement: %.2f €/MWh\nPunto curve: %s MW" % (
            settlement, f"{clearing_mw:,.1f}"
        )
    else:
        settlement_note = (
            "Settlement GME: %.2f €/MWh\n"
            "BID a prezzo ≥ settlement: %s MW\n"
            "Gradino OFF al settlement: %s–%s MW"
        ) % (
            settlement, f"{clearing_mw:,.1f}", f"{supply_below:,.1f}", f"{supply_at_or_below:,.1f}"
        )
    ax.text(0.015, 0.975, settlement_note, transform=ax.transAxes, ha="left", va="top",
            fontsize=8.5, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#aaaaaa", alpha=0.96))

    xmax = max(float(supply["cumulative_mw"].max()), float(demand["cumulative_mw"].max()))
    ymin = min(float(supply[OFFERED_PRICE].min()), float(demand[OFFERED_PRICE].min()))
    ymax = max(float(supply[OFFERED_PRICE].max()), float(demand[OFFERED_PRICE].max()))
    ax.set_xlim(0, xmax * 1.025)
    ax.set_ylim(min(-550.0, ymin - 0.04 * abs(ymin)), max(4200.0, ymax + 0.04 * abs(ymax)))
    ax.set_xlabel("Quantità cumulata (MW)", fontsize=11)
    ax.set_ylabel("Prezzo offerto (€/MWh)", fontsize=11)
    zone_label = " · ".join(part for part in zones[0].split(";") if part)
    ax.set_title(
        "Macrozona %s\nMGP — 13 novembre 2026, periodo 38: 09:15–09:30 CET (08:15–08:30 UTC)" % zone_label,
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.grid(True, color="#e5e5e5", linewidth=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95, fontsize=9)

    mtu_counts = simple["MTU"].value_counts().sort_index()
    mtu_note = "Curve semplici: %d offerte MTU15 + %d MTU60; i MW MTU60 non sono divisi per 4." % (
        int(mtu_counts.get(15, 0)), int(mtu_counts.get(60, 0))
    )
    fig.text(0.08, 0.035,
             "Ora di consegna GME: CET (UTC+1).\n" + mtu_note + "\n" + format_block_summary(blocks),
             fontsize=8, color="#444444", va="bottom")
    fig.tight_layout(rect=[0.04, 0.105, 0.99, 0.97])
    fig.savefig(OUT_PNG, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print("Grafico:", OUT_PNG)
    print("Dati curva:", OUT_CSV)
    print("Macrozona:", zones[0])
    print("Settlement:", "%.2f €/MWh" % settlement)
    print("Domanda BID con prezzo >= settlement:", "%.3f MW" % clearing_mw)
    print("Gradino supply al settlement:", "%.3f–%.3f MW" % (supply_below, supply_at_or_below))
    if not curves_meet_at_settlement:
        print("Nota: le curve aggregate non si intersecano esattamente al settlement; non viene disegnato un punto di clearing fittizio.")
    print("Offerte semplici incluse:", simple["MTU"].value_counts().sort_index().to_dict())
    print("" + format_block_summary(blocks))


if __name__ == "__main__":
    main()
