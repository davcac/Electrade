#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Saldo prima degli scambi (slide 10), con la stessa scala Y della slide 12."""

import argparse
from pathlib import Path

from plot_produzione import DEFAULT_CSV, GRAFICI, read_production_and_load
from plot_surplus import COMPARISON_Y_TICKS, ZERO_PRICE_ZONES, plot_zonal_balance


def main():
    ap = argparse.ArgumentParser(description="Saldo prima degli scambi per Sud, Calabria e Sicilia")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="percorso del CSV tidy")
    ap.add_argument("--a75-dir", help="cartella degli XML A75, di default accanto al CSV")
    ap.add_argument("--out", type=Path, default=Path(GRAFICI) / "02_surplus_3zone.png",
                    help="percorso del PNG di output")
    args = ap.parse_args()

    load, _, production = read_production_and_load(args.csv, args.a75_dir)
    plot_zonal_balance(
        load, production, zones=ZERO_PRICE_ZONES, output=args.out,
        y_ticks=COMPARISON_Y_TICKS, x_limits=(load.index.min(), load.index.max()),
    )


if __name__ == "__main__":
    main()
