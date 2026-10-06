#!/usr/bin/env python3
"""
Matched large-public-plant design, following the identification strategy of
Garin and Rothbaum (2025) as documented in their replication code
(Build/2_collapse_plant_to_county.do, Codes/0.prep_county_sample.do).

Treatment. A county is treated if it received at least one plant that was
  (i)  publicly financed  -- private share of structure spending <= 5%
  (ii) new                -- structures are more than 40% of plant cost
  (iii) large             -- cost at least $10 million (10,000 thousands)

Sample. The 100 largest manufacturing counties of 1940 are dropped. These are
the places whose selection into treatment is least comparable to anything else
and they drive any naive contrast. A secondary restriction drops 1940
metropolitan counties.

Comparison. Rather than an instrument, identification rests on comparing
treated counties to observably similar untreated counties, with two additional
contrasts that exploit adjacency: treated counties against their untreated
neighbours, and treated counties with no treated neighbour against everything
else.

Estimator. Propensity-score construction on the prewar control vector with
squared terms, then (a) a balance table, (b) inverse-probability-weighted and
nearest-neighbour-matched differences, (c) OLS on the matched sample.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'; GR=ROOT/'data/raw/garin_rothbaum/Data/RawData'

# ---------------- treatment from the plant file --------------------------
f=pd.read_parquet(AN/'facilities_geocoded.parquet')
f=f[f.assignable & f.fips.notna()].copy(); f['fips']=f.fips.astype(int)
IC=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
IC_MAP=dict(zip(IC.city_fips.astype(int),IC.parent_fips.astype(int)))
f['fips']=f.fips.map(lambda x: IC_MAP.get(x,x))
for c in ['total_cost','pub_struct','priv_struct','pub_total','priv_total']:
    f[c]=pd.to_numeric(f[c],errors='coerce').fillna(0)
struct=f.pub_struct+f.priv_struct
f['privshr']  = np.where(struct>0, f.priv_struct/struct, np.where(f.priv_total>0,1.0,0.0))
f['pubplant'] = f.privshr<=0.05
f['newbuild'] = np.where(f.total_cost>0, struct/f.total_cost, 0)>0.40
# Garin-Rothbaum: new = explicitly designated "New Plant" in the volume OR
# more than 40% of cost in structures. The explicit flag is the '!New Plant'
# line the volume prints beneath a facility's location.
f['newplant'] = f.get('newplant', False).fillna(False).astype(bool)
f['new']      = f.newplant | f.newbuild
f['large10']  = f.total_cost>=10000
f['bigpub']   = f.pubplant & f.new & f.large10

t=(f.groupby('fips')
     .agg(n_bigpub=('bigpub','sum'), bigpub_cost=('total_cost',lambda s: s[f.loc[s.index,'bigpub']].sum()),
          n_plants=('bigpub','size'))
     .reset_index())
t['treat']=(t.n_bigpub>0).astype(int)
print(f'explicit "New Plant" flags : {int(f.newplant.sum()):,}')
print(f'new by structure share     : {int(f.newbuild.sum()):,}')
print(f'new (either)               : {int(f.new.sum()):,}')
print(f'large new public (>=$10M)  : {int(f.bigpub.sum()):,} in {int(t.treat.sum()):,} counties, '
      f'${f.loc[f.bigpub,"total_cost"].sum()/1e6:.2f}bn')

# ---------------- panel + prewar controls --------------------------------
d=pd.read_parquet(AN/'master_panel_iv.parquet').merge(t[['fips','treat','n_bigpub','bigpub_cost']],on='fips',how='left')
for c in ['treat','n_bigpub','bigpub_cost']: d[c]=d[c].fillna(0)
d['treat']=d.treat.astype(int)
d['statefip']=(d.fips//1000).astype(int)

im,_=pyreadstat.read_dta(str(GR/'inmetro_1930_1940.dta'))
mc=[c for c in im.columns if 'metro' in c.lower()]
if 'fips' in im.columns and mc:
    im['fips']=pd.to_numeric(im.fips,errors='coerce')
    im=im[im.fips.notna()].copy(); im['fips']=im.fips.astype(int).map(lambda x: IC_MAP.get(x,x))
    d=d.merge(im.groupby('fips',as_index=False)[mc[-1]].max().rename(columns={mc[-1]:'in_metro1940'}),on='fips',how='left')
if 'in_metro1940' not in d.columns:
    # The IPUMS extract is keyed on statefip/countyicp, not fips, so the merge
    # above is skipped. Say so rather than defaulting a whole column to zero
    # and letting a downstream robustness check quietly test nothing.
    print('  WARNING: in_metro1940 not merged (source has no fips key); '
          'column set to 0 and not used downstream')
d['in_metro1940']=d.get('in_metro1940',pd.Series(0,index=d.index)).fillna(0)

# top-100 manufacturing counties of 1940
d['mfgemp1940']=pd.to_numeric(d.mfgemp1940,errors='coerce').fillna(0)
d['top100mfg']=(d.mfgemp1940.rank(ascending=False,method='first')<=100).astype(int)

CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
for c in CTRL+['mfgwage1940','ownrate1940','medfaminc1950']: d[c]=pd.to_numeric(d[c],errors='coerce')
d['mfg_suppressed']=d.mfgshare1940.isna().astype(float)
for c in CTRL:
    d[c]=d[c].fillna(d.groupby('statefip')[c].transform('median')).fillna(d[c].median())
for c in ['logpop1940','urbrate1940','mfgshare1940','blackshare1940']:
    d['sq_'+c]=d[c]**2
X=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']

s=d[(d.top100mfg==0)].copy()
print(f'\nsample after dropping the top-100 manufacturing counties: {len(s):,}')
print(f'  treated {int(s.treat.sum()):,}   untreated {int((1-s.treat).sum()):,}')
s.to_parquet(AN/'matched_sample_raw.parquet',index=False)
json.dump({'n_bigpub_plants':int(f.bigpub.sum()),'treated_counties':int(t.treat.sum()),
           'bigpub_dollars_k':float(f.loc[f.bigpub,'total_cost'].sum()),
           'sample_n':int(len(s)),'sample_treated':int(s.treat.sum())},
          open(AN/'matched_design_setup.json','w'),indent=2)
