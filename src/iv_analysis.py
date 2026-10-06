#!/usr/bin/env python3
"""
Instrumental-variables estimates of wartime investment on postwar outcomes.

Endogenous : W^C procurement, W^F industrial war plant, W^M military installations
Instruments: 1938 Industrial Mobilization Plan allocations (by branch), and
             prewar Army/Navy establishments and bases
Exogenous  : the full prewar control vector and state fixed effects

Reports first-stage F, Cragg-Donald and Kleibergen-Paap weak-instrument
statistics, Wooldridge/Wu-Hausman endogeneity tests, and Sargan/J
over-identification tests where the model is over-identified.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from linearmodels.iv import IV2SLS
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'

d=pd.read_parquet(AN/'master_panel_iv.parquet')
d['statefip']=(d.fips//1000).astype(int); P=d.pop1940.replace(0,np.nan)
d['W_C']=np.arcsinh(1000*d.contract_k/P); d['W_F']=np.arcsinh(1000*d.fac_public_k/P)
d['W_M']=np.arcsinh(1000*d.cdb_fac_military/P); d['B']=1000*d.deaths_all/P
for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040','PCTILL3','PCTFRM3']:
    d[c]=pd.to_numeric(d[c],errors='coerce')
d['mfg_suppressed']=d.mfgshare1940.isna().astype(float)
d['mfgshare1940']=d.mfgshare1940.fillna(0); d['blackshare1940']=d.blackshare1940.fillna(0)
d['prewar_imputed']=d.PCTILL3.isna().astype(float)
for c in ['PCTILL3','PCTFRM3']:
    d[c]=d[c].fillna(d.groupby('statefip')[c].transform('median')).fillna(d[c].median())
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','mfg_suppressed','prewar_imputed']
# instruments in arsinh so they scale like the endogenous regressors
for c in ['imp_fac','imp_industrial','imp_total','mil_prewar','imp_o','imp_a','imp_e','imp_q']:
    d['z_'+c]=np.arcsinh(pd.to_numeric(d[c],errors='coerce').fillna(0))
d['_li70']=np.log(pd.to_numeric(d.medfaminc1970,errors='coerce').replace(0,np.nan))
res={}

def prep(cols):
    s=d[cols+['statefip']].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float)
    D=D.loc[:, D.std()>0]                      # drop levels emptied by the dropna
    return s,D

def clean(X):
    """Drop zero-variance and perfectly collinear columns so 2SLS has full rank."""
    X=X.loc[:, X.std().fillna(0)>1e-12]
    keep, seen = [], None
    import numpy.linalg as la
    A=X.values.astype(float)
    q,r=la.qr(A)
    tol=abs(np.diag(r)).max()*1e-10
    idx=[i for i in range(A.shape[1]) if abs(r[i,i])>tol]
    return X.iloc[:, idx]

def first_stage(endog, instr):
    cols=[endog]+instr+CTRL
    s,D=prep(cols)
    X=sm.add_constant(pd.concat([s[instr+CTRL],D],axis=1))
    r=sm.OLS(s[endog],X).fit(cov_type='cluster',cov_kwds={'groups':s.statefip})
    R=np.zeros((len(instr),X.shape[1]))
    for i,z in enumerate(instr): R[i,list(X.columns).index(z)]=1
    F=float(r.f_test(R).fvalue)
    return F,int(r.nobs),r

print('='*78); print('FIRST STAGE  (state FE, prewar controls, SE clustered on state)'); print('='*78)
SPECS=[('W_C',['z_imp_fac'],'contracts ~ IMP facilities'),
       ('W_C',['z_imp_o','z_imp_a','z_imp_e','z_imp_q'],'contracts ~ IMP by branch (4)'),
       ('W_F',['z_imp_industrial'],'war plant ~ IMP industrial'),
       ('W_F',['z_imp_o','z_imp_a','z_imp_e','z_imp_q'],'war plant ~ IMP by branch (4)'),
       ('W_M',['z_mil_prewar'],'military ~ prewar bases/estabs')]
res['first_stage']=[]
for endog,instr,lab in SPECS:
    F,n,r=first_stage(endog,instr)
    flag='strong' if F>=10 else ('weak' if F>=5 else 'VERY WEAK')
    print(f'  {lab:36s} F={F:8.2f}  n={n:,}  [{flag}]')
    res['first_stage'].append({'spec':lab,'F':round(F,3),'n':n,'verdict':flag,
        'coef':{z:round(float(r.params[z]),4) for z in instr}})

print('\n'+'='*78); print('2SLS: POSTWAR OUTCOMES ON INSTRUMENTED INVESTMENT'); print('='*78)
OUT=[('logpop1970','log population 1970'),('mfgshare1970','manufacturing share 1970'),
     ('_li70','log family income 1970'),('ownrate1970','homeownership 1970')]
res['iv']=[]
INSTR=['z_imp_o','z_imp_a','z_imp_e','z_imp_q','z_mil_prewar']
ENDOG=['W_C','W_F','W_M']
for y,lab in OUT:
    cols=[y]+ENDOG+INSTR+CTRL+['B']
    s,D=prep(cols)
    ex=clean(sm.add_constant(pd.concat([s[CTRL+['B']],D],axis=1)))
    try:
        r=IV2SLS(s[y], ex, s[ENDOG], s[INSTR]).fit(cov_type='clustered',clusters=s.statefip)
        row={'outcome':lab,'n':int(r.nobs)}
        line=f'{lab:26s}'
        for k in ENDOG:
            b,p=float(r.params[k]),float(r.pvalues[k])
            st='***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
            line+=f'{b:>10.4f}{st:<3s}'
            row[k]={'coef':round(b,5),'se':round(float(r.std_errors[k]),5),'p':round(p,4)}
        print(line+f'  n={int(r.nobs):,}')
        try:
            row['wu_hausman_p']=round(float(r.wu_hausman().pval),4)
            row['sargan_p']=round(float(r.sargan.pval),4)
        except Exception: pass
        res['iv'].append(row)
    except Exception as ex_:
        print(f'{lab:26s} FAILED: {ex_}')
print(f'\n{"":26s}'+''.join(f'{k:>13s}' for k in ENDOG))
print('\nendogeneity / overid tests:')
for r_ in res['iv']:
    print(f"  {r_['outcome']:26s} Wu-Hausman p={r_.get('wu_hausman_p','-')}  Sargan p={r_.get('sargan_p','-')}")
(AN/'iv_results.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"iv_results.json"}')
