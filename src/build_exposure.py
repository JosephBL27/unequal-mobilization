#!/usr/bin/env python3
"""
Build B_i^A, the enlistment-conditioned fatality exposure of equation (2).

    B_i^A = 1000 * D_i^A / E_i^A

DS2 could not supply E_i^A: its ENL_STATE/ENL_COUNTY are NARA administrative
codes with no published crosswalk to FIPS (checked: the ICPSR codebook lists
the codes without labels; the NARA and CenSoc technical documents do not
publish the mapping). Instead E_i^A comes from the Garin-Rothbaum county file,
which tabulates volunteer and drafted counts from the same NARA universe and
carries ICPSR state/county codes. Those map to FIPS through the Haines 1940
file, which holds both, at 99.9%.

This also yields race-specific enlistment and military-age denominators.
"""
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
h,_=pyreadstat.read_dta(str(ROOT/'data/raw/haines_icpsr2896/02896-0032-Data.dta'),
                        usecols=['state','county','name','fips'])
for c in ['state','county','fips']: h[c]=pd.to_numeric(h[c],errors='coerce')
cw=h[(h.county>0)&h.fips.notna()][['state','county','fips']].assign(fips=lambda d:d.fips.astype(int))

g,_=pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/'
                            'WWII_draft_volunteer_casualties_Army_AirForce.dta'))
NUM=['casualties','volunteer','drafted','volunteer_w','drafted_w','volunteer_b','drafted_b',
     'volunteer_o','drafted_o','age1440','age1445','age1440_white','age1445_white',
     'age1440_black','age1445_black']
for c in NUM: g[c]=pd.to_numeric(g[c],errors='coerce')
g['E_A']       = g.volunteer.fillna(0)+g.drafted.fillna(0)
g['E_A_white'] = g.volunteer_w.fillna(0)+g.drafted_w.fillna(0)
g['E_A_black'] = g.volunteer_b.fillna(0)+g.drafted_b.fillna(0)
g['volunteer_share'] = np.where(g.E_A>0, g.volunteer/g.E_A, np.nan)

m=g.merge(cw,left_on=['stateicp','county'],right_on=['state','county'],how='inner')
out=m[['fips','E_A','E_A_white','E_A_black','volunteer_share','casualties',
       'age1440','age1445','age1440_white','age1445_white','age1440_black','age1445_black']]
out=out.groupby('fips',as_index=False).sum(min_count=1)

dea=pd.read_parquet(AN/'casualties_county.parquet')
j=out.merge(dea,on='fips',how='outer')
j['B_A']       = 1000*j.deaths_all/j.E_A.replace(0,np.nan)          # deaths per 1,000 enlisted
j['B_A_battle']= 1000*j.deaths_battle/j.E_A.replace(0,np.nan)
j['B_milage']  = 1000*j.deaths_all/j.age1445.replace(0,np.nan)      # per 1,000 men aged 14-45
j['mobilization_rate'] = j.E_A/j.age1445.replace(0,np.nan)          # share of military-age men serving

print(f'counties with E_A       : {j.E_A.notna().sum():,}')
print(f'national enlistment E_A : {j.E_A.sum():,.0f}')
print(f'national deaths D_A     : {j.deaths_all.sum():,.0f}')
print(f'implied national rate   : {1000*j.deaths_all.sum()/j.E_A.sum():.1f} deaths per 1,000 enlisted')
print(f'\nG&R own casualty count  : {j.casualties.sum():,.0f}  (vs DS1 {j.deaths_all.sum():,.0f})')
print(f'  correlation DS1 vs G&R: {j[["deaths_all","casualties"]].dropna().corr().iloc[0,1]:.4f}')
print('\nB_A distribution (deaths per 1,000 enlisted):')
print(j.B_A.describe(percentiles=[.05,.25,.5,.75,.95]).round(2).to_string())
print(f'\nmobilization rate (share of men 14-45 who served):')
print(j.mobilization_rate.describe(percentiles=[.05,.5,.95]).round(3).to_string())
j.to_parquet(AN/'exposure_county.parquet',index=False)
print(f'\n-> {AN/"exposure_county.parquet"}')
