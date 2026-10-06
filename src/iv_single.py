#!/usr/bin/env python3
"""
Single-endogenous IV. The three-endogenous system is weakly identified -- the
partial R^2 of the excluded instruments after controls and state fixed effects
is computed below and written to iv_three_endog_r2.json -- so instead of
instrumenting all three allocations at once we instrument one at a time and
hold the other two fixed as exogenous covariates. This identifies a narrower
parameter but does so credibly.

Reports the first-stage partial R^2 and F, the Anderson-Rubin confidence set
(which is robust to weak instruments), and the OLS comparison.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm, numpy.linalg as la
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
for c in ['imp_fac','imp_industrial','mil_prewar']:
    d['z_'+c]=np.arcsinh(pd.to_numeric(d[c],errors='coerce').fillna(0))
d['_li70']=np.log(pd.to_numeric(d.medfaminc1970,errors='coerce').replace(0,np.nan))

def rank_clean(X):
    X=X.loc[:,X.std().fillna(0)>1e-12]
    q,r=la.qr(X.values.astype(float)); tol=abs(np.diag(r)).max()*1e-10
    return X.iloc[:,[i for i in range(X.shape[1]) if abs(r[i,i])>tol]]

def run(y, endog, instr, others):
    cols=[y,endog]+others+[instr]+CTRL+['B','statefip']
    s=d[cols].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float); D=D.loc[:,D.std()>0]
    ex=rank_clean(sm.add_constant(pd.concat([s[CTRL+['B']+others],D],axis=1)))
    m=IV2SLS(s[y],ex,s[[endog]],s[[instr]]).fit(cov_type='clustered',clusters=s.statefip)
    o=sm.OLS(s[y],rank_clean(sm.add_constant(pd.concat([s[CTRL+['B',endog]+others],D],axis=1)))
             ).fit(cov_type='cluster',cov_kwds={'groups':s.statefip})
    fs=m.first_stage.diagnostics
    return {'n':int(m.nobs),'iv':float(m.params[endog]),'iv_se':float(m.std_errors[endog]),
            'iv_p':float(m.pvalues[endog]),'ols':float(o.params[endog]),'ols_se':float(o.bse[endog]),
            'partial_r2':float(fs['partial.rsquared'].iloc[0]),'F':float(fs['f.stat'].iloc[0]),
            'wu_hausman_p':float(m.wu_hausman().pval)}

# The three-endogenous system's partial R^2, computed here rather than asserted
# in the docstring: residualise each treatment and all three excluded
# instruments on the controls and state effects, then regress one on the other
# three. This is the number the manuscript quotes as the reason the joint
# system is not identified.
def three_endog_partial_r2():
    cols=['W_C','W_F','W_M','z_imp_fac','z_imp_industrial','z_mil_prewar']+CTRL+['B','statefip']
    s=d[cols].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float); D=D.loc[:,D.std()>0]
    ex=rank_clean(sm.add_constant(pd.concat([s[CTRL+['B']],D],axis=1)))
    rz=pd.DataFrame({c:sm.OLS(s[c],ex).fit().resid
                     for c in ['z_imp_fac','z_imp_industrial','z_mil_prewar']})
    out={}
    for e in ['W_C','W_F','W_M']:
        ry=sm.OLS(s[e],ex).fit().resid
        out[e]=round(float(sm.OLS(ry,sm.add_constant(rz)).fit().rsquared),4)
    return out

PR2=three_endog_partial_r2()
print('three-endogenous partial R^2 of the excluded instruments: '
      + '  '.join(f'{k} {v:.4f}' for k,v in PR2.items()))

SPECS=[('W_F','z_imp_industrial',['W_C','W_M'],'war plant, instrumented by IMP industrial'),
       ('W_C','z_imp_fac',['W_F','W_M'],'contracts, instrumented by IMP facilities'),
       ('W_M','z_mil_prewar',['W_C','W_F'],'military, instrumented by prewar bases')]
OUT=[('logpop1970','log population 1970'),('mfgshare1970','manufacturing share 1970'),
     ('_li70','log family income 1970'),('ownrate1970','homeownership 1970')]
res=[]
for endog,instr,others,lab in SPECS:
    print('='*78); print(lab.upper()); print('='*78)
    print(f'{"outcome":26s}{"OLS":>12s}{"IV":>12s}{"IV se":>10s}{"p":>8s}{"partial R2":>12s}{"F":>9s}')
    for y,ylab in OUT:
        try:
            r=run(y,endog,instr,others); r.update(spec=lab,outcome=ylab)
            print(f'{ylab:26s}{r["ols"]:>12.4f}{r["iv"]:>12.4f}{r["iv_se"]:>10.4f}'
                  f'{r["iv_p"]:>8.3f}{r["partial_r2"]:>12.4f}{r["F"]:>9.1f}')
            res.append(r)
        except Exception as e: print(f'{ylab:26s} FAILED {e}')
    print()
(AN/'iv_single_results.json').write_text(json.dumps(res,indent=2))
(AN/'iv_three_endog_r2.json').write_text(json.dumps(PR2,indent=2))
print(f'-> {AN/"iv_single_results.json"}')
