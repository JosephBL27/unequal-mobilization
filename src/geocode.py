#!/usr/bin/env python3
"""One place->county resolver, used by both CPA volumes.

Four stages, each strictly narrower than the last, so that every assignment is
attributable to a named rule:
  1. exact   normalized city + state against the 25,131-row crosswalk
  2. alias   curated historical identifications (see geo_aliases.py)
  3. fuzzy   within-state edit distance >= 0.88, with an explicit blocklist
  4. unmatched, reported not dropped
"""
import difflib
import pandas as pd, pyreadstat
from pathlib import Path
from geo_aliases import norm_city, alias_frame, FUZZY_BLOCK

ROOT = Path(__file__).resolve().parent.parent
CW   = ROOT/'data/raw/garin_rothbaum/Data/RawData/cw-city-county.dta'
CUTOFF = 0.88

def _crosswalk():
    cw, _ = pyreadstat.read_dta(str(CW))
    cw['cn'] = cw.city.map(norm_city)
    cw['st'] = cw.state.str.upper()
    return cw.drop_duplicates(['cn','st'])[['cn','st','cty_fips']]

def resolve(df, city_col, state_col, weight_col=None):
    """Adds fips + match_stage. Returns (df, diagnostics dict)."""
    cwu = _crosswalk()
    d = df.copy()
    d['cn'] = d[city_col].map(norm_city)
    d['st'] = d[state_col].astype(str).str.strip().str.upper().replace({'NAN': None})

    d = d.merge(cwu, on=['cn','st'], how='left')
    d['fips'] = d.cty_fips
    d['match_stage'] = d.fips.notna().map({True:'exact', False:None})

    # Curated aliases OVERRIDE the crosswalk rather than only filling gaps.
    # The crosswalk resolves some place names to the wrong county -- most
    # consequentially 'new york, NY' to Kings rather than New York County --
    # and a curated historical identification should win over a lookup.
    al = alias_frame()
    d = d.merge(al, on=['cn','st'], how='left')
    take = d.alias_fips.notna()
    d.loc[take,'fips'] = d.loc[take,'alias_fips']
    d.loc[take,'match_stage'] = 'alias'

    by_state = {s: g.cn.tolist() for s, g in cwu.groupby('st')}
    lut = {(r.st, r.cn): r.cty_fips for r in cwu.itertuples()}
    need = d[d.fips.isna() & d.cn.notna() & d.st.notna()][['cn','st']].drop_duplicates()
    rows = []
    for r in need.itertuples():
        cand = by_state.get(r.st)
        if not cand: continue
        hit = difflib.get_close_matches(r.cn, cand, n=1, cutoff=CUTOFF)
        if hit and (r.cn, r.st, hit[0]) not in FUZZY_BLOCK:
            rows.append((r.cn, r.st, hit[0], lut[(r.st, hit[0])]))
    if rows:
        fz = pd.DataFrame(rows, columns=['cn','st','fuzzy_to','fuzzy_fips'])
        d = d.merge(fz, on=['cn','st'], how='left')
        take = d.fips.isna() & d.fuzzy_fips.notna()
        d.loc[take,'fips'] = d.loc[take,'fuzzy_fips']
        d.loc[take,'match_stage'] = 'fuzzy'
    else:
        d['fuzzy_to'] = None

    ok = d.fips.notna()
    diag = {'rows': int(len(d)), 'matched': int(ok.sum()),
            'row_rate': round(float(ok.mean()), 4),
            'by_stage': {k: int(v) for k, v in d.match_stage.value_counts().items()},
            'counties': int(d.loc[ok,'fips'].nunique())}
    if weight_col:
        w = pd.to_numeric(d[weight_col], errors='coerce').fillna(0)
        diag['weight_total']   = float(w.sum())
        diag['weight_matched'] = float(w[ok].sum())
        diag['weight_rate']    = round(float(w[ok].sum()/w.sum()), 4)
        diag['weight_by_stage']= {k: round(float(w[d.match_stage==k].sum()/w.sum()),4)
                                  for k in d.match_stage.dropna().unique()}
    return d, diag
