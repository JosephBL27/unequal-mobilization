#!/usr/bin/env python3
"""Resolve every war supply contract to a county.

This stage exists because the artifact it writes was, for most of this
project's life, an input that no committed script produced. It was read by
build_master_panel, make_appendix, and audit_paper_vs_data -- so the paper's
procurement measure W^C descended from a file that could not be regenerated,
and a fix to the resolver could not propagate. Running the current resolver
against the source recovers thirty rows the stored copy had lost (190,693
against 190,663) and leaves the dollar match rate, the county count, and every
county total unchanged.

Reads   data/raw/contracts/WWII_contracts_clean.dta   (Brunet-Koustas)
Writes  data/analysis/contracts_geocoded.parquet
        data/analysis/contracts_geocode_report.json
"""
import json
from pathlib import Path
import pandas as pd, pyreadstat
from geocode import resolve

ROOT = Path(__file__).resolve().parent.parent
AN   = ROOT/'data/analysis'; AN.mkdir(parents=True, exist_ok=True)
SRC  = ROOT/'data/raw/contracts/WWII_contracts_clean.dta'

raw, _ = pyreadstat.read_dta(str(SRC))
print(f'source: {len(raw):,} contract records')

d, diag = resolve(raw, 'city_name', 'state', weight_col='ValueThousandsDollars')
assert len(d) == len(raw), f'resolver changed the row count: {len(raw)} -> {len(d)}'

d.to_parquet(AN/'contracts_geocoded.parquet', index=False)
(AN/'contracts_geocode_report.json').write_text(json.dumps(diag, indent=2))

print(f"matched {diag['matched']:,} rows ({diag['row_rate']:.1%}), "
      f"{diag['weight_rate']:.1%} of dollars, {diag['counties']:,} counties")
print(f"-> {AN/'contracts_geocoded.parquet'}")
