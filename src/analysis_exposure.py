#!/usr/bin/env python3
"""
Re-run the central results using B_i^A (equation 2), the paper's preferred
exposure measure, alongside B_i^civic. Also compute the overlap statistic
against every wartime allocation.

Exclusion rule, applied once and reported. B_i^A is defined for 2,976 of 3,107
counties. 91 counties are absent from the enlistment source; 40 record more
deaths than enlistments or a mobilisation rate above one (four Michigan counties
with a systematic enlistment undercount, the rest Dakota counties under 3,000
population where small-number noise dominates). The 131 excluded counties hold
4.0% of 1940 population (3.5 points of that from the 91 missing-source counties). They are dropped from B_i^A specifications only and
retained everywhere else.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'

d=pd.read_parquet(AN/'master_panel_v2.parquet')
x=pd.read_parquet(AN/'exposure_county.parquet')
d=d.merge(x[['fips','E_A','E_A_white','E_A_black','volunteer_share','age1445',
             'B_A','B_A_battle','B_milage','mobilization_rate']],on='fips',how='left')
d['statefip']=(d.fips//1000).astype(int); P=d.pop1940
d['W_C']=np.arcsinh(1000*d.contract_k/P); d['W_F']=np.arcsinh(1000*d.fac_public_k/P)
d['W_M']=np.arcsinh(1000*d.cdb_fac_military/P); d['B_civic']=1000*d.deaths_all/P
d['valid_BA']=~((d.mobilization_rate>1)|(d.B_A>300)|d.B_A.isna())
for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040','PCTILL3','PCTFRM3']:
    d[c]=pd.to_numeric(d[c],errors='coerce')
d['mfg_suppressed']=d.mfgshare1940.isna().astype(float)
d['mfgshare1940']=d.mfgshare1940.fillna(0); d['blackshare1940']=d.blackshare1940.fillna(0)
d['prewar_imputed']=d.PCTILL3.isna().astype(float)
for c in ['PCTILL3','PCTFRM3']:
    d[c]=d[c].fillna(d.groupby('statefip')[c].transform('median')).fillna(d[c].median())
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','mfg_suppressed','prewar_imputed']
v=d[d.valid_BA].copy()
res={'n_total':int(len(d)),'n_valid_BA':int(len(v)),
     'excluded':int((~d.valid_BA).sum()),
     'excluded_pop_share':round(float(d.loc[~d.valid_BA,'pop1940'].sum()/d.pop1940.sum()),6)}

print('='*76); print('MOBILISATION AND EXPOSURE — DESCRIPTIVE'); print('='*76)
print(f'  national enlistment E^A      : {d.E_A.sum():,.0f}')
print(f'  national Army/AAF deaths D^A : {d.deaths_all.sum():,.0f}')
print(f'  national fatality rate       : {1000*d.deaths_all.sum()/d.E_A.sum():.1f} per 1,000 enlisted')
print(f'  median county B^A            : {v.B_A.median():.1f} per 1,000 enlisted')
print(f'  IQR                          : {v.B_A.quantile(.25):.1f} – {v.B_A.quantile(.75):.1f}')
print(f'  90/10 ratio                  : {v.B_A.quantile(.9)/v.B_A.quantile(.1):.2f}x')
res['fatality_rate_national']=round(float(1000*d.deaths_all.sum()/d.E_A.sum()),2)
res['BA_p90_p10_ratio']=round(float(v.B_A.quantile(.9)/v.B_A.quantile(.1)),3)

print('\n  B^A separates two things the community measure conflates:')
print(f'    Spearman(B^A, B^civic)              {spearmanr(v.B_A,v.B_civic,nan_policy="omit").statistic:+.3f}')
print(f'    Spearman(mobilisation rate, B^A)    {spearmanr(v.mobilization_rate,v.B_A,nan_policy="omit").statistic:+.3f}')
print(f'    Spearman(mobilisation rate, B^civic){spearmanr(v.mobilization_rate,v.B_civic,nan_policy="omit").statistic:+.3f}')
res['spearman_BA_Bcivic']=round(float(spearmanr(v.B_A,v.B_civic,nan_policy="omit").statistic),4)
res['spearman_mob_BA']=round(float(spearmanr(v.mobilization_rate,v.B_A,nan_policy="omit").statistic),4)
# Its sibling was printed and never stored, so the manuscript drifted to +0.101
# against a true +0.094 and nothing could catch it. Both are on the valid-B^A
# sample so the pair the paper quotes describes one set of counties.
res['spearman_mob_Bcivic']=round(float(spearmanr(v.mobilization_rate,v.B_civic,nan_policy="omit").statistic),4)

print('\n'+'='*76); print('OVERLAP OF EACH ALLOCATION WITH FATAL LOSS'); print('='*76)
def ov(a,b):
    pa,pb=a/a.sum(),b/b.sum(); A=float(np.minimum(pa,pb).sum())
    mm=0.5*(pa+pb); kl=lambda x: float(np.sum(x[x>0]*np.log2(x[x>0]/mm[x>0])))
    return A,0.5*kl(pa)+0.5*kl(pb)
print(f'{"":34s}{"A":>8s}{"JS":>8s}{"rho(levels)":>13s}{"rho(per cap)":>14s}')
res['overlap']={}
for lab,col in [('contracts W^C','contract_k'),('war plant W^F','fac_public_k'),
                ('military installations W^M','cdb_fac_military')]:
    A,JS=ov(d[col],d.deaths_all)
    r1=spearmanr(d[col],d.deaths_all).statistic
    r2=spearmanr(v[col]/v.E_A.replace(0,np.nan),v.B_A,nan_policy='omit').statistic
    print(f'{lab:34s}{A:8.3f}{JS:8.3f}{r1:13.3f}{r2:14.3f}')
    res['overlap'][lab]={'A':round(A,4),'JS':round(JS,4),
                         'rho_levels':round(float(r1),4),'rho_per_enlistee':round(float(r2),4)}

print('\n'+'='*76); print('DID EXPOSURE-CONDITIONED FATALITY PREDICT INVESTMENT?'); print('='*76)
def fit(df,y,X):
    s=df[[y]+X+['statefip']].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float)
    XX=sm.add_constant(pd.concat([s[X],D],axis=1))
    return sm.OLS(s[y],XX).fit(cov_type='cluster',cov_kwds={'groups':s.statefip})
res['allocation_BA']=[]
for y,lab in [('W_C','contracts'),('W_F','war plant'),('W_M','military')]:
    r=fit(v,y,['B_A']+CTRL)
    print(f'  {lab:22s} coef(B^A)={r.params["B_A"]:+.5f}  se={r.bse["B_A"]:.5f}  '
          f'p={r.pvalues["B_A"]:.3f}  n={int(r.nobs):,}')
    res['allocation_BA'].append({'dv':lab,'coef':round(float(r.params['B_A']),6),
                                 'p':round(float(r.pvalues['B_A']),4),'n':int(r.nobs)})

print('\n'+'='*76); print('OUTCOMES WITH B^A REPLACING B^civic'); print('='*76)
d['_li70']=np.log(pd.to_numeric(d.medfaminc1970,errors='coerce').replace(0,np.nan))
v=d[d.valid_BA].copy()
X=['W_C','W_F','W_M','B_A']+CTRL
print(f'{"outcome":28s}'+''.join(f'{k:>13s}' for k in ['W_C','W_F','W_M','B_A']))
res['outcomes_BA']=[]
for y,lab in [('logpop1970','log population 1970'),('mfgshare1970','mfg share 1970'),
              ('_li70','log family income 1970'),('ownrate1970','homeownership 1970')]:
    r=fit(v,y,X)
    st=lambda k:('***' if r.pvalues[k]<.01 else '**' if r.pvalues[k]<.05 else '*' if r.pvalues[k]<.1 else '')
    print(f'{lab:28s}'+''.join(f'{r.params[k]:>10.4f}{st(k):<3s}' for k in ['W_C','W_F','W_M','B_A']))
    res['outcomes_BA'].append({'outcome':lab,'n':int(r.nobs),
        'coef':{k:round(float(r.params[k]),5) for k in ['W_C','W_F','W_M','B_A']},
        'p':{k:round(float(r.pvalues[k]),4) for k in ['W_C','W_F','W_M','B_A']}})
d.to_parquet(AN/'master_panel_v3.parquet',index=False)
(AN/'exposure_results.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"exposure_results.json"}')
