#!/usr/bin/env python3
"""
Composition-adjusted fatality exposure.

DS2 records race, education, birth year, enlistment source, and Army General
Classification Test score for the 5.4 percent of enlistees that carry one. A county's raw fatality
rate per enlistee therefore confounds two things: the risk faced by men of a
given profile, and the profile of the men the county sent. Regressing the
county fatality rate on soldier composition and taking the residual isolates
the first.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_v3.parquet')
d['statefip']=(d.fips//1000).astype(int)
COMP=['ds2_black_share','ds2_hs_share','ds2_vol_share','ds2_mean_yob','ds2_mean_agct']
for c in COMP+['ds2_enlist','deaths_all']: d[c]=pd.to_numeric(d[c],errors='coerce')
d['B_ds2']=1000*d.deaths_all/d.ds2_enlist.replace(0,np.nan)
v=d[(d.ds2_enlist>=100)&d.B_ds2.notna()&(d.B_ds2<300)].copy()
print(f'counties with >=100 enlistees and a usable rate: {len(v):,} of {len(d):,}')
print(f'  they cover {v.ds2_enlist.sum():,.0f} enlistees and {v.deaths_all.sum():,.0f} deaths')

X=v[COMP].copy()
for c in COMP: X[c]=X[c].fillna(X[c].median())
Xc=sm.add_constant(X)
r=sm.OLS(v.B_ds2,Xc).fit(cov_type='HC1')
print(f'\n=== does soldier composition explain county fatality rates? ===')
print(f'  R^2 = {r.rsquared:.4f}   n = {int(r.nobs):,}')
for c in COMP:
    print(f'    {c:20s} {r.params[c]:+10.4f}  p={r.pvalues[c]:.4f}')
v['B_resid']=r.resid + v.B_ds2.mean()
print(f'\n  raw rate  sd = {v.B_ds2.std():.2f}')
print(f'  residual  sd = {v.B_resid.std():.2f}  '
      f'({1-v.B_resid.std()/v.B_ds2.std():.1%} of the s.d. is composition)')

P=v.pop1940
print(f'\n=== does composition-adjusted risk track investment? ===')
res={'n':int(len(v)),'composition_R2':round(float(r.rsquared),4)}
for lab,col in [('contracts','contract_k'),('war plant','fac_public_k'),
                ('military','cdb_fac_military')]:
    rho=spearmanr(v[col]/P,v.B_resid,nan_policy='omit').statistic
    raw=spearmanr(v[col]/P,v.B_ds2,nan_policy='omit').statistic
    print(f'  {lab:12s} raw rho {raw:+.3f}   composition-adjusted rho {rho:+.3f}')
    res[lab]={'rho_raw':round(float(raw),4),'rho_adjusted':round(float(rho),4)}
# AGCT is the one DS2 field that is not universal, and the manuscript said for a
# year that the file carries it "for every soldier". Store the coverage so the
# claim has a producer and the caveat cannot quietly drop out again.
_ds2 = pd.read_parquet(AN/'ds2_county.parquet')
_raw = pd.read_parquet(ROOT/'data/interim/ds2_enlistment.parquet', columns=['AGCT'])
_n_agct = int(pd.to_numeric(_raw.AGCT, errors='coerce').notna().sum())
res['agct_coverage'] = {
    'records_with_agct': _n_agct,
    'records_total': int(len(_raw)),
    'share': round(_n_agct/len(_raw), 4),
    'counties_no_agct': int(_ds2.ds2_mean_agct.isna().sum()),
    'counties_total': int(len(_ds2))}
print(f"  AGCT present on {_n_agct:,} of {len(_raw):,} records "
      f"({100*_n_agct/len(_raw):.1f}%); {res['agct_coverage']['counties_no_agct']} "
      f"counties have none")
(AN/'composition_results.json').write_text(json.dumps(res,indent=2))
v[['fips','name','B_ds2','B_resid']+COMP].to_parquet(AN/'composition_county.parquet',index=False)
print(f'\n-> {AN/"composition_results.json"}')
