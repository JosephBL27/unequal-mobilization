#!/usr/bin/env python3
"""Run the whole pipeline in dependency order.

There was no ordering guard before this file, and running the scripts in
alphabetical or remembered order silently produced a panel whose downstream
consumers had been built from the previous version of it. The chain below is
the actual dependency order, derived from what each script reads and writes:

  build_contracts_geocoded -> contracts_geocoded.parquet
  parse_facilities     -> facilities_geocoded.parquet
  build_master_panel   -> master_panel.parquet   (reads both of the above)
  three_geographies    -> master_panel_v2.parquet   (reads master_panel)
  build_exposure       -> exposure_county.parquet
  analysis_exposure    -> master_panel_v3.parquet   (reads v2 + exposure_county)
  build_instruments    -> master_panel_iv.parquet   (reads v3)
  matched_plant_design -> matched_sample_raw.parquet(reads iv)
  matched_estimates    -> matched_sample.parquet    (reads raw)

Everything after that consumes one of those and is order-independent among
itself. Run this, then `git diff data/analysis paper/tables`: anything that
moves was stale.

Every artifact this pipeline reads is written by a stage above, with one
deliberate exception: `data/interim/ds2_enlistment.parquet` is produced by
`ds2_to_parquet.py`, a one-time conversion of an 873 MB tab-separated NARA
extract that takes minutes and never changes. Run it once before the first
build; `build_ds2_county` reads its output.
"""
import subprocess, sys, time
from pathlib import Path
SRC = Path(__file__).resolve().parent

ORDER = [
    # --- build, strictly ordered -----------------------------------------
    'build_contracts_geocoded', 'parse_facilities', 'build_county_panel',
    'merge_independent_cities',
    'build_master_panel', 'three_geographies', 'build_exposure',
    'analysis_exposure', 'build_instruments', 'build_ds2_county',
    # --- analysis ---------------------------------------------------------
    'overlap_analysis', 'allocation_criteria', 'composition', 'regressions', 'robustness',
    'matched_plant_design', 'matched_estimates', 'matched_robustness',
    'matched_military', 'audit_military_robustness', 'oster_bounds', 'gi_bill_channel',
    'iv_analysis', 'iv_single', 'iv_validity', 'imp_specifications',
    'build_shiftshare', 'illinois_robustness',
    # --- exhibits ---------------------------------------------------------
    'make_tables', 'make_matched_tables', 'make_iv_tables', 'make_appendix',
    'make_shiftshare_tables',
    'make_maps',
    # --- verification -----------------------------------------------------
    # Last, and it exits nonzero. Until this stage existed the pipeline could
    # come back green while the manuscript quoted a number no artifact
    # produced: run_all only ever checked that each script ran.
    'audit_paper_vs_data',
]

fail = []
for name in ORDER:
    t0 = time.time()
    r = subprocess.run([sys.executable, str(SRC / f'{name}.py')],
                       capture_output=True, text=True)
    ok = r.returncode == 0
    print(f'{name:28s} {"ok" if ok else "FAIL":>6s}  {time.time()-t0:5.1f}s')
    if name == 'audit_paper_vs_data':
        print(r.stdout[-2000:])
    if not ok:
        fail.append(name)
        print(r.stderr[-1500:])
print()
print('all stages completed' if not fail else f'FAILED: {", ".join(fail)}')
sys.exit(1 if fail else 0)
