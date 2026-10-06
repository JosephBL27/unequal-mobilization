#!/usr/bin/env python3
"""
Build the prewar instrument set from the 1938 Industrial Mobilization Plan.

In 1938 the Joint Army and Navy Munitions Board surveyed American industry and
allocated named establishments to specific procurement branches in the event of
mobilisation -- the Directory of Facilities, Allocated and Reserved. The
allocation was made before the war and on the basis of a plant's technical fit
with a branch's requirements, not on the basis of anything that happened after
1940. It therefore predicts where wartime contracts would later be placed while
being plausibly unrelated to postwar county outcomes except through wartime
production itself.

The same source records prewar Army and Navy establishments and bases, which
instrument military-installation investment separately.

Merge key: ICPSR state code and NDMTCODE, converted to 1940 county FIPS.
"""
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
V=['state','ndmtcode','name','navyestb','navybases','armyestb','armybases','imp_fac',
   'imp_anmb','imp_oasw','imp_q','imp_n','imp_m','imp_c','imp_s','imp_o','imp_a',
   'imp_e','imp_tool','imp_aero','imp_optic','imp_steel','pop40','area40']
d,_=pyreadstat.read_dta(str(ROOT/'data/raw/jaworski_imp/data-controls-raw.dta'),usecols=V)
xw,_=pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/crosswalk_statefip_stateicp_1910.dta'))
d=d.merge(xw,left_on='state',right_on='stateicp',how='left')
d['fips']=(d.statefip*1000+(pd.to_numeric(d.ndmtcode,errors='coerce')/10).round())
d=d[d.fips.notna()].copy(); d['fips']=d.fips.astype(int)

IC=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
IC_MAP=dict(zip(IC.city_fips.astype(int),IC.parent_fips.astype(int)))
d['fips']=d.fips.map(lambda f: IC_MAP.get(f,f))

IMP=[c for c in V if c.startswith('imp_')]+['navyestb','navybases','armyestb','armybases']
for c in IMP: d[c]=pd.to_numeric(d[c],errors='coerce').fillna(0)
g=d.groupby('fips',as_index=False)[IMP].sum()

# composite instruments
g['imp_total']    = g[[c for c in IMP if c.startswith('imp_')]].sum(axis=1)
g['imp_industrial']= g.imp_fac + g.imp_tool + g.imp_aero + g.imp_optic + g.imp_steel
g['mil_prewar']   = g.armybases + g.navybases + g.armyestb + g.navyestb
g['any_imp']      = (g.imp_fac>0).astype(int)
g['any_mil_prewar']=(g.mil_prewar>0).astype(int)

m=pd.read_parquet(AN/'master_panel_v3.parquet')
j=m.merge(g,on='fips',how='left')
for c in list(g.columns[1:]): j[c]=j[c].fillna(0)
print(f'panel {len(m):,} counties; IMP merged for {(j.imp_fac>0).sum():,} with any allocated facility')
print(f'  IMP facilities total   {j.imp_fac.sum():,.0f}')
print(f'  prewar military sites  {j.mil_prewar.sum():,.0f} across {(j.mil_prewar>0).sum():,} counties')
print(f'  counties with any IMP  {(j.any_imp==1).sum():,} ({(j.any_imp==1).mean():.1%})')
j.to_parquet(AN/'master_panel_iv.parquet',index=False)

print('\n=== raw correlations with the endogenous regressors ===')
P=j.pop1940
j['W_C']=np.arcsinh(1000*j.contract_k/P); j['W_F']=np.arcsinh(1000*j.fac_public_k/P)
j['W_M']=np.arcsinh(1000*j.cdb_fac_military/P)
for iv in ['imp_fac','imp_industrial','imp_total','mil_prewar']:
    z=np.arcsinh(j[iv])
    print(f'  {iv:15s} W_C {z.corr(j.W_C):+.3f}   W_F {z.corr(j.W_F):+.3f}   W_M {z.corr(j.W_M):+.3f}')
