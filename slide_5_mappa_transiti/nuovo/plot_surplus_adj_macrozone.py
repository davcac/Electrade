#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Saldo residuo di Sud, Calabria e Sicilia dopo gli scambi esterni A11."""

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PRODUCTION_DIR = HERE.parents[1] / "slide_4_carico_production"
sys.path.insert(0, str(PRODUCTION_DIR))

from plot_macrozone import DEFAULT_CSV as DEFAULT_TRANSITI_CSV
from plot_macrozone import physical_net_import, read_transit_csv
from plot_produzione import DEFAULT_CSV as DEFAULT_SURPLUS_CSV
from plot_produzione import NET_LABEL
from plot_surplus_macrozone import plot_macrozone_balance, read_macrozone_series

GRAFICI = HERE / "grafici"


def main():
    ap = argparse.ArgumentParser(description="Saldo residuo di Sud, Calabria e Sicilia dopo gli scambi A11")
    ap.add_argument("--surplus-csv", default=DEFAULT_SURPLUS_CSV, help="percorso del CSV carico/produzione")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--transiti-csv", default=DEFAULT_TRANSITI_CSV, help="percorso del CSV transiti")
    ap.add_argument("--out", type=Path, default=GRAFICI / "05_surplus_adj_macrozone.png",
                    help="percorso del PNG di output")
    args = ap.parse_args()

    flows = read_transit_csv(args.transiti_csv)
    load, production = read_macrozone_series(args.surplus_csv, args.a75_dir)
    hourly_load = load.resample("h").mean()
    hourly_production = production.resample("h").mean()
    net_import = physical_net_import(flows).reindex(hourly_load.index)

    plot_macrozone_balance(
        hourly_load, hourly_production + net_import, output=args.out,
        title="Saldo fisico residuo dopo gli scambi",
        supply_label=f"{NET_LABEL} + import netto A11",
        area_labels=("Scarto positivo", "Scarto negativo"),
        scale_reference=(load, production),
    )


if __name__ == "__main__":
    main()
