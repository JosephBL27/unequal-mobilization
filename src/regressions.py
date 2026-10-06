#!/usr/bin/env python3
"""
Main estimation. Two questions, kept separate.

(A) ALLOCATION. Conditional on prewar characteristics and state, did fatal
    burden predict receiving war investment? Answer with three dependent
    variables, since the war state made three distinct allocations.

(B) OUTCOMES. Did the three exposures predict 1940->1970 development?

Inference: heteroskedasticity-robust, clustered on state. State fixed effects
throughout, so identification is within-state.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_v2.parquet')
d['statefip']=(d.fips//1000).astype(int)
P=d.pop1940

# exposures (all per-capita, arsinh-transformed to keep true zeros)
d['W_C']=np.arcsinh(1000*d.contract_k/P)
d['W_F']=np.arcsinh(1000*d.fac_public_k/P)
d['W_M']=np.arcsinh(1000*d.cdb_fac_military/P)
d['B']  =1000*d.deaths_all/P                       # deaths per 1,000 residents

# Missing controls are NOT missing at random. The Census of Manufactures
# suppresses county wage-earner counts where there is little or no
# manufacturing, so listwise deletion drops 370 small rural counties -- 10.3%
# of 1940 population and 9.5% of Army/AAF deaths -- and biases the sample
# toward exactly the industrial places that received war investment.
# Recode to zero (the substantive meaning) and carry an indicator; impute the
# two 1930 controls at their state median with an indicator.
for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940',
          'popgrowth_3040','PCTILL3','PCTFRM3']:
    d[c]=pd.to_numeric(d[c],errors='coerce')
d['mfg_suppressed']=d.mfgshare1940.isna().astype(float)
d['mfgshare1940']=d.mfgshare1940.fillna(0.0)
d['blackshare1940']=d.blackshare1940.fillna(0.0)
d['prewar_imputed']=d.PCTILL3.isna().astype(float)
for c in ['PCTILL3','PCTFRM3']:
    d[c]=d[c].fillna(d.groupby(d.fips//1000)[c].transform('median'))
    d[c]=d[c].fillna(d[c].median())

CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940',
      'popgrowth_3040','PCTILL3','PCTFRM3','mfg_suppressed','prewar_imputed']

def fit(df, y, X, label, cluster='statefip'):
    cols=[y]+X+[cluster]
    s=df[cols].replace([np.inf,-np.inf],np.nan).dropna()
    if len(s)<50: return None
    # state fixed effects via demeaning-by-dummies (few enough states to be explicit)
    D=pd.get_dummies(s[cluster],prefix='st',drop_first=True).astype(float)
    XX=sm.add_constant(pd.concat([s[X],D],axis=1))
    r=sm.OLS(s[y],XX).fit(cov_type='cluster',cov_kwds={'groups':s[cluster]})
    return {'label':label,'y':y,'n':int(r.nobs),'r2':round(float(r.rsquared),4),
            'coef':{k:round(float(r.params[k]),5) for k in X},
            'se':{k:round(float(r.bse[k]),5) for k in X},
            'p':{k:round(float(r.pvalues[k]),5) for k in X},
            'nclust':int(s[cluster].nunique())}

out={'allocation':[],'outcomes':[],'plant_vs_base':[]}

print('='*78)
print('(A) DID FATAL BURDEN PREDICT WAR INVESTMENT?  [state FE, SE clustered on state]')
print('='*78)
print(f'{"dependent variable":32s} {"coef on B":>11s} {"se":>9s} {"p":>8s} {"n":>7s} {"R2":>6s}')
for y,lab in [('W_C','contracts per capita (arsinh)'),
              ('W_F','industrial plant per cap (arsinh)'),
              ('W_M','military installations (arsinh)')]:
    for spec,X in [('raw',['B']),('+controls',['B']+CTRL)]:
        r=fit(d,y,X,f'{lab} [{spec}]')
        if r:
            out['allocation'].append(r)
            print(f'{lab[:30]:30s} {spec:>9s} {r["coef"]["B"]:11.4f} {r["se"]["B"]:9.4f} '
                  f'{r["p"]["B"]:8.3f} {r["n"]:7,} {r["r2"]:6.3f}')

print('\n'+'='*78)
print('(B) DID WAR EXPOSURE PREDICT POSTWAR OUTCOMES?  [1940 controls, state FE]')
print('='*78)
# The manufacturing share has total employment in its denominator, so a county
# adding non-manufacturing jobs shows a falling share with its manufacturing
# employment unchanged. The two levels below decompose it; without them the
# share coefficients cannot be read as statements about manufacturing.
d['_lemp70']=np.log(pd.to_numeric(d.emp1970,errors='coerce').replace(0,np.nan))
d['_lmfgemp70']=np.log((pd.to_numeric(d.mfgshare1970,errors='coerce')/100
                        *pd.to_numeric(d.emp1970,errors='coerce')).replace(0,np.nan))
OUT=[('logpop1950','log population 1950'),('logpop1960','log population 1960'),
     ('logpop1970','log population 1970'),
     ('mfgshare1960','manufacturing share 1960'),('mfgshare1970','manufacturing share 1970'),
     ('_lemp70','log total employment 1970'),
     ('_lmfgemp70','log manufacturing employment 1970'),
     ('medfaminc1950','median family income 1950'),('medfaminc1960','median family income 1960'),
     ('medfaminc1970','median family income 1970'),
     ('ownrate1960','homeownership rate 1960'),('ownrate1970','homeownership rate 1970')]
X=['W_C','W_F','W_M','B']+CTRL
hdr=f'{"outcome":30s}'+''.join(f'{k:>12s}' for k in ['W_C','W_F','W_M','B'])+f'{"n":>7s}{"R2":>7s}'
print(hdr); print('-'*len(hdr))
for y,lab in OUT:
    yy=y
    if y.startswith('medfaminc'):
        d['_ly']=np.log(pd.to_numeric(d[y],errors='coerce').replace(0,np.nan)); yy='_ly'
    r=fit(d,yy,X,lab)
    if r:
        r['label']=lab; out['outcomes'].append(r)
        stars=lambda k:('***' if r['p'][k]<.01 else '**' if r['p'][k]<.05 else '*' if r['p'][k]<.1 else '')
        print(f'{lab:30s}'+''.join(f'{r["coef"][k]:>9.4f}{stars(k):<3s}' for k in ['W_C','W_F','W_M','B'])
              +f'{r["n"]:>7,}{r["r2"]:>7.3f}')

# ---- (B2) THE INTERACTIONS OF EQUATION (8) --------------------------------
# Section 4 calls theta_C and theta_F "the paper's distinctive parameters" and
# no table ever reported them. They are estimated here on the four headline 1970
# outcomes. A null is a perfectly good answer and is what finding (2) predicts.
print('\n'+'='*78)
print('(B2) INTERACTIONS: does the postwar association of investment vary with')
print('     fatal exposure?   theta_C on W_C x B_A, theta_F on W_F x B_A')
print('='*78)
# B_A and valid_BA are added downstream in analysis_exposure, so the
# per-enlistee burden comes from v3 rather than the v2 panel this script reads.
_v3=pd.read_parquet(AN/'master_panel_v3.parquet',columns=['fips','B_A','valid_BA'])
dI=d.merge(_v3,on='fips',how='left')
dI['B_A']=pd.to_numeric(dI.B_A,errors='coerce').where(dI.valid_BA.fillna(False))
dI['WCxBA']=dI.W_C*dI.B_A; dI['WFxBA']=dI.W_F*dI.B_A
XI=['W_C','W_F','W_M','B_A','WCxBA','WFxBA']+CTRL
res_i=[]
print(f'{"outcome":30s}{"theta_C":>12s}{"p":>8s}{"theta_F":>12s}{"p":>8s}{"n":>7s}')
for y,lab in [('logpop1970','log population 1970'),('mfgshare1970','manufacturing share 1970'),
              ('medfaminc1970','log family income 1970'),('ownrate1970','homeownership rate 1970')]:
    yy=y
    if y.startswith('medfaminc'):
        dI['_lyi']=np.log(pd.to_numeric(dI[y],errors='coerce').replace(0,np.nan)); yy='_lyi'
    r=fit(dI,yy,XI,lab)
    if not r: continue
    st=lambda k:('***' if r['p'][k]<.01 else '**' if r['p'][k]<.05 else '*' if r['p'][k]<.1 else '')
    print(f'{lab:30s}{r["coef"]["WCxBA"]:>9.5f}{st("WCxBA"):<3s}{r["p"]["WCxBA"]:>8.3f}'
          f'{r["coef"]["WFxBA"]:>9.5f}{st("WFxBA"):<3s}{r["p"]["WFxBA"]:>8.3f}{r["n"]:>7,}')
    res_i.append({'outcome':lab,'n':r['n'],
                  'theta_C':round(r['coef']['WCxBA'],6),'p_C':round(r['p']['WCxBA'],4),
                  'se_C':round(r['se']['WCxBA'],6),
                  'theta_F':round(r['coef']['WFxBA'],6),'p_F':round(r['p']['WFxBA'],4),
                  'se_F':round(r['se']['WFxBA'],6)})
out['interactions']=res_i

print('\n'+'='*78)
print('(C) AMONG INVESTED COUNTIES: PLANT RATHER THAN BASE?')
print('='*78)
inv=d[(d.fac_public_k>0)|(d.cdb_fac_military>0)].copy()
sub=inv[~((inv.fac_public_k>0)&(inv.cdb_fac_military>0))].copy()
sub['plant']=(sub.fac_public_k>0).astype(float)
for spec,X2 in [('raw',['B']),('+controls',['B']+CTRL)]:
    r=fit(sub,'plant',X2,f'P(plant not base) [{spec}]')
    if r:
        out['plant_vs_base'].append(r)
        print(f'  {spec:10s} coef(B)={r["coef"]["B"]:+.4f}  se={r["se"]["B"]:.4f}  '
              f'p={r["p"]["B"]:.3f}  n={r["n"]:,}')

(AN/'regression_results.json').write_text(json.dumps(out,indent=2))
print(f'\n-> {AN/"regression_results.json"}')
