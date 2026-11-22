#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Saldo fisico residuo per Sud, Calabria e Sicilia dopo gli scambi A11 (slide 12).

Confronta il carico A65 con la produzione al netto degli assorbimenti A75
più le importazioni nette fisiche. Tutte le serie sono su base oraria.

Uso:
  python slide_5_mappa_transiti/nuovo/plot_surplus_adj.py
"""

import argparse
from pathlib import Path
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
PRODUCTION_DIR = HERE.parents[1] / "slide_4_carico_production"
sys.path.insert(0, str(PRODUCTION_DIR))

from plot_produzione import DEFAULT_CSV, NET_LABEL, read_production_and_load
from plot_surplus import COMPARISON_Y_TICKS, ZERO_PRICE_ZONES, plot_zonal_balance

TRANSITI_CSV = HERE.parent / "dati" / "transiti_48h.csv"
GRAFICI = HERE / "grafici"


def main():
    ap = argparse.ArgumentParser(description="Saldo fisico residuo dopo gli scambi A11")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso CSV carico/produzione")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--transiti", type=Path, default=TRANSITI_CSV, help="percorso CSV transiti")
    ap.add_argument("--out", type=Path, default=GRAFICI / "04_surplus_adj_3zone.png",
                    help="percorso PNG di output")
    args = ap.parse_args()

    if not args.transiti.is_file():
        raise SystemExit(f"CSV dei transiti A11 non trovato: {args.transiti}")

    load, _, production = read_production_and_load(args.csv, args.a75_dir)
    hourly_load = load.resample("h").mean()
    hourly_production = production.resample("h").mean()

    flows = pd.read_csv(args.transiti)
    flows["ts"] = pd.to_datetime(flows["timestamp_utc"], utc=True)
    imports = flows.groupby(["ts", "in_zone"])["flow_physical_mw"].sum(min_count=1).unstack()
    exports = flows.groupby(["ts", "out_zone"])["flow_physical_mw"].sum(min_count=1).unstack()
    net_import = (imports - exports).reindex(index=hourly_load.index, columns=ZERO_PRICE_ZONES)
    supply = hourly_production.reindex(columns=ZERO_PRICE_ZONES) + net_import

    plot_zonal_balance(
        hourly_load, supply, zones=ZERO_PRICE_ZONES, output=args.out,
        title="Saldo fisico residuo dopo gli scambi",
        supply_label=f"{NET_LABEL}\n+ import netto A11",
        datasets="A65, A75, A11",
        balance_caption="Saldo residuo = linea viola − carico (medie orarie)",
        y_ticks=COMPARISON_Y_TICKS, x_limits=(load.index.min(), load.index.max()),
    )


if __name__ == "__main__":
    main()
