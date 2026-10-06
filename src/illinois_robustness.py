#!/usr/bin/env python3
"""
Does the Illinois gap in the Army/AAF honor list drive anything?

Fifty-six counties carry no recorded death and 22 of the 102 Illinois counties
are among them. If the honor list's county coding is unreliable there, every
statistic built on deaths is suspect. The test is to drop the state and see what
moves.

This file exists because the claim it supports had no producer. `illinois_robustness.json`
was carried in the repository, read by nothing that could regenerate it, and had
drifted: it stored an overlap of 0.4557 against a current 0.4663, so the prose it
sourced was describing a panel that no longer existed. See the 2026-08-30 entry in my project notes
and 2026-08-31, for the two earlier instances of the same bug.

Specification is Table 1's exactly: the seven outcome columns of `regressions.py`
block (B), 1940 controls, state fixed effects, standard errors clustered on state.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parent.parent; AN = ROOT / 'data/analysis'

d = pd.read_parquet(AN / 'master_panel_v2.parquet')
d['statefip'] = (d.fips // 1000).astype(int)
P = d.pop1940
d['W_C'] = np.arcsinh(1000 * d.contract_k / P)
d['W_F'] = np.arcsinh(1000 * d.fac_public_k / P)
d['W_M'] = np.arcsinh(1000 * d.cdb_fac_military / P)
d['B']   = 1000 * d.deaths_all / P

for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940',
          'popgrowth_3040','PCTILL3','PCTFRM3']:
    d[c] = pd.to_numeric(d[c], errors='coerce')
d['mfg_suppressed']  = d.mfgshare1940.isna().astype(float)
d['mfgshare1940']    = d.mfgshare1940.fillna(0.0)
d['blackshare1940']  = d.blackshare1940.fillna(0.0)
d['prewar_imputed']  = d.PCTILL3.isna().astype(float)
for c in ['PCTILL3','PCTFRM3']:
    d[c] = d[c].fillna(d.groupby(d.fips // 1000)[c].transform('median')).fillna(d[c].median())

CTRL = ['logpop1940','urbrate1940','blackshare1940','mfgshare1940',
        'popgrowth_3040','PCTILL3','PCTFRM3','mfg_suppressed','prewar_imputed']
X = ['W_C','W_F','W_M','B'] + CTRL
COLS = [('logpop1950','Log pop. 1950'), ('logpop1970','Log pop. 1970'),
        ('mfgshare1960','Mfg. share 1960'), ('mfgshare1970','Mfg. share 1970'),
        ('medfaminc1950','Log income 1950'), ('medfaminc1970','Log income 1970'),
        ('ownrate1970','Own rate 1970')]
for y in ['medfaminc1950','medfaminc1970']:
    d['_l' + y] = np.log(pd.to_numeric(d[y], errors='coerce').replace(0, np.nan))


def fit(df, y):
    yy = '_l' + y if y.startswith('medfaminc') else y
    s = df[[yy] + X + ['statefip']].replace([np.inf, -np.inf], np.nan).dropna()
    D = pd.get_dummies(s.statefip, prefix='st', drop_first=True).astype(float)
    r = sm.OLS(s[yy], sm.add_constant(pd.concat([s[X], D], axis=1))).fit(
        cov_type='cluster', cov_kwds={'groups': s.statefip})
    return {k: float(r.params[k]) for k in ['W_C','W_F','W_M','B']}, int(r.nobs)


noIL = d[d.statefip != 17]
res = {'dropped_state': 'Illinois (FIPS 17)',
       'n_full': int(len(d)), 'n_noIL': int(len(noIL)), 'table1': {}}
print('=' * 86)
print('TABLE 1 WITH AND WITHOUT ILLINOIS')
print('=' * 86)
print(f'{"column":20s}{"term":>7s}{"full":>11s}{"no IL":>11s}{"change":>11s}')
worst = 0.0; worst_at = None
for y, lab in COLS:
    a, n1 = fit(d, y); b, n2 = fit(noIL, y)
    res['table1'][lab] = {k: {'full': round(a[k], 5), 'no_IL': round(b[k], 5),
                              'change': round(b[k] - a[k], 5)} for k in a}
    res['table1'][lab]['n'] = {'full': n1, 'no_IL': n2}
    for k in ['W_C','W_F','W_M','B']:
        ch = b[k] - a[k]
        if abs(ch) > abs(worst): worst, worst_at = ch, f'{lab} {k}'
        print(f'{lab:20s}{k:>7s}{a[k]:11.4f}{b[k]:11.4f}{ch:+11.4f}')
res['max_abs_change'] = round(abs(worst), 5)
res['max_abs_change_at'] = worst_at

# overlap coefficient, recomputed the way overlap_analysis.py does
def overlap(f):
    D = f.deaths_all.fillna(0); W = f.contract_k.fillna(0)
    return float(np.minimum(D / D.sum(), W / W.sum()).sum())
res['overlap_full']  = round(overlap(d), 4)
res['overlap_noIL']  = round(overlap(noIL), 4)
res['overlap_change'] = round(res['overlap_noIL'] - res['overlap_full'], 4)

print(f'\nlargest coefficient movement: {worst:+.4f} at {worst_at}')
print(f'overlap A: {res["overlap_full"]:.4f} -> {res["overlap_noIL"]:.4f} '
      f'({res["overlap_change"]:+.4f})')
(AN / 'illinois_robustness.json').write_text(json.dumps(res, indent=2))
print(f'\n-> {AN/"illinois_robustness.json"}')
