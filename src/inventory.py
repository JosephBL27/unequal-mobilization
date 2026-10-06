#!/usr/bin/env python3
"""Build a hash-based inventory of every data file; flag exact duplicates."""
import hashlib, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_EXT = {'.dta','.csv','.tsv','.txt','.xls','.xlsx','.stc','.parquet','.rda','.sav','.dbf','.shp'}
SKIP_DIRS = {'.venv','.git','_quarantine','__pycache__','logs'}

def sha(p, cap=None):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        n = 0
        while chunk := f.read(1<<22):
            h.update(chunk); n += len(chunk)
            if cap and n >= cap: break
    return h.hexdigest()

rows = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP_DIRS]
    for f in fn:
        p = Path(dp)/f
        if p.suffix.lower() not in DATA_EXT: continue
        try: size = p.stat().st_size
        except OSError: continue
        if size == 0: continue
        rows.append({'path': str(p.relative_to(ROOT)), 'size': size,
                     'sha256': sha(p), 'ext': p.suffix.lower()})

by_hash = {}
for r in rows: by_hash.setdefault(r['sha256'], []).append(r)
dups = {h:v for h,v in by_hash.items() if len(v) > 1}

total = sum(r['size'] for r in rows)
waste = sum(v[0]['size']*(len(v)-1) for v in dups.values())

print(f"files: {len(rows)}   unique: {len(by_hash)}   total: {total/1e9:.2f} GB   reclaimable: {waste/1e9:.3f} GB\n")
if dups:
    print("=== EXACT DUPLICATES ===")
    for h, v in sorted(dups.items(), key=lambda kv: -kv[1][0]['size']):
        print(f"  {v[0]['size']/1e6:9.1f} MB  x{len(v)}")
        for r in v: print(f"      {r['path']}")
else:
    print("no exact duplicates")

(ROOT/'data'/'docs').mkdir(parents=True, exist_ok=True)
(ROOT/'data'/'docs'/'inventory.json').write_text(json.dumps(
    {'files': rows, 'duplicate_groups': list(dups.values()),
     'total_bytes': total, 'reclaimable_bytes': waste}, indent=2))
