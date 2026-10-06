#!/usr/bin/env python3
"""DS2 enlistment TSV (8.29M rows) -> partitioned parquet. Chunked, low memory."""
import pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT/'data/raw/casualties_icpsr38927/38927-0002-Data.tsv'
OUT  = ROOT/'data/interim/ds2_enlistment.parquet'
OUT.parent.mkdir(parents=True, exist_ok=True)

DTYPES = {'SERIAL':'string','ENL_NAME':'string','ENL_STATE':'string','ENL_COUNTY':'string',
          'DATE_ENLIST':'string','GRADE':'string','BRANCH':'string','TERM_ENLIST':'string',
          'SOURCE':'string','NATIVITY':'string','YOB':'string','RACE':'string','EDUC':'string',
          'OCC':'string','MARST':'string','HEIGHT':'string','WEIGHT':'string','KILLED':'string',
          'DATE_ENLIST2':'string','ENLDATE':'string','AGE':'string','AGCT':'string',
          'ACTUALHEIGHT':'float32','ACTUALWEIGHT':'float32'}

writer, n = None, 0
for chunk in pd.read_csv(SRC, sep='\t', dtype=DTYPES, chunksize=500_000,
                         na_values=['','.',' '], low_memory=False):
    tbl = pa.Table.from_pandas(chunk, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(OUT, tbl.schema, compression='zstd', compression_level=6)
    writer.write_table(tbl); n += len(chunk)
    print(f'  {n:,} rows', flush=True)
writer.close()
print(f'DONE {n:,} rows -> {OUT} ({OUT.stat().st_size/1e6:.1f} MB)')
