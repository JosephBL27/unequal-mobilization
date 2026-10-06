#!/usr/bin/env python3
"""
Map the full DS2 enlistment file (8,293,187 records) to 1940 counties using the
NARA state/county crosswalk decoded from NARA 100.1CL_SD, then aggregate to
county level with the composition variables DS2 uniquely provides.

The NARA county code is the county FIPS code; the NARA state code is not the
FIPS state code and must be translated (Alabama 41, Arizona 98, Arkansas 87,
California 91, ...). 99.8% of the derived FIPS codes fall in the 1940 census
county universe.
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
x=pd.read_excel(ROOT/'data/raw/crosswalks/nara/NARA_DS2_Research_Crosswalk_Parsed.xlsx',
                sheet_name='NARA_State_County')
x.columns=[c.strip() for c in x.columns]
x['fips']=pd.to_numeric(x['State FIPS'],errors='coerce')*1000+pd.to_numeric(x['NARA County'],errors='coerce')
cw=(x.dropna(subset=['fips'])[['NARA State','NARA County','fips','Confidence']]
      .drop_duplicates(['NARA State','NARA County']))
cw.columns=['ns','nc','fips','conf']

IC=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
IC_MAP=dict(zip(IC.city_fips.astype(int),IC.parent_fips.astype(int)))

d=pd.read_parquet(ROOT/'data/interim/ds2_enlistment.parquet',
                  columns=['ENL_STATE','ENL_COUNTY','KILLED','RACE','EDUC','OCC','YOB','AGCT','GRADE','SOURCE'])
d['ns']=pd.to_numeric(d.ENL_STATE,errors='coerce'); d['nc']=pd.to_numeric(d.ENL_COUNTY,errors='coerce')
d=d.merge(cw,on=['ns','nc'],how='left')
d=d[d.fips.notna()].copy()
d['fips']=d.fips.astype(int).map(lambda f: IC_MAP.get(f,f))
d['killed']=pd.to_numeric(d.KILLED,errors='coerce').fillna(0)
d['race']=pd.to_numeric(d.RACE,errors='coerce')
d['educ']=pd.to_numeric(d.EDUC,errors='coerce')
d['yob']=pd.to_numeric(d.YOB,errors='coerce')
d['agct']=pd.to_numeric(d.AGCT,errors='coerce')          # non-numeric codes -> NaN
d['black']=(d.race==2).astype(float)
d['white']=(d.race==1).astype(float)
# NARA education: 0 grammar school ... higher codes = more schooling
d['hs_plus']=(d.educ>=4).astype(float)
# SOURCE distinguishes draftees from volunteers in the NARA scheme
d['volunteer']=pd.to_numeric(d.SOURCE,errors='coerce').isin([1,2,3]).astype(float)

g=(d.groupby('fips')
     .agg(ds2_enlist=('killed','size'), ds2_killed=('killed','sum'),
          ds2_black=('black','sum'), ds2_white=('white','sum'),
          ds2_hs_plus=('hs_plus','sum'), ds2_volunteer=('volunteer','sum'),
          ds2_mean_yob=('yob','mean'), ds2_mean_agct=('agct','mean'))
     .reset_index())
g['ds2_black_share']=g.ds2_black/g.ds2_enlist
g['ds2_hs_share']=g.ds2_hs_plus/g.ds2_enlist
g['ds2_vol_share']=g.ds2_volunteer/g.ds2_enlist
g['ds2_fatality_rate']=1000*g.ds2_killed/g.ds2_enlist

print(f'DS2 records mapped : {len(d):,} of 8,293,187 ({len(d)/8293187:.1%})')
print(f'counties           : {len(g):,}')
print(f'total enlistments  : {g.ds2_enlist.sum():,}')
print(f'total killed flag  : {g.ds2_killed.sum():,.0f}')
print(f'national rate      : {1000*g.ds2_killed.sum()/g.ds2_enlist.sum():.1f} per 1,000 enlisted')
g.to_parquet(AN/'ds2_county.parquet',index=False)

# ---- validate against DS1 and against the Garin-Rothbaum tabulation ----
dea=pd.read_parquet(AN/'casualties_county.parquet')
dea['fips']=dea.fips.map(lambda f: IC_MAP.get(int(f),int(f)))
dea=dea.groupby('fips',as_index=False).sum()
ex=pd.read_parquet(AN/'exposure_county.parquet')[['fips','E_A']]
ex['fips']=ex.fips.map(lambda f: IC_MAP.get(int(f),int(f)))
ex=ex.groupby('fips',as_index=False).sum()
j=g.merge(dea,on='fips',how='inner').merge(ex,on='fips',how='left')
print(f'\n=== VALIDATION (n={len(j):,} counties) ===')
print(f'  corr(DS2 killed, DS1 deaths)      {j.ds2_killed.corr(j.deaths_all):.4f}')
print(f'  corr(DS2 enlist, G&R enlistment)  {j.ds2_enlist.corr(j.E_A):.4f}')
print(f'  DS2 killed total {j.ds2_killed.sum():,.0f} vs DS1 deaths {j.deaths_all.sum():,.0f}')
print(f'  DS2 enlist total {j.ds2_enlist.sum():,.0f} vs G&R {j.E_A.sum():,.0f}')
j.to_parquet(AN/'ds2_validation.parquet',index=False)
