#!/usr/bin/env python3
"""
Is there ANY specification of the 1938 Industrial Mobilization Plan that
satisfies the exclusion restriction?

The paper's baseline instrument -- the count of allocated facilities -- has a
strong first stage and fails its placebo, because the Munitions Board allocated
plants that were already industrially capable in places that were already
urban. That is one specification. A referee is entitled to ask whether the
failure is a property of that construction or of the source.

This script answers systematically. It sweeps seven constructions of the
instrument, from the broadest (every allocated establishment across all
procurement branches) to the narrowest (the aeronautical and optical branches
alone, which allocate to a technically specific capability rather than to
general manufacturing capacity), and for each reports:

  RELEVANCE   first-stage F on the excluded instrument, and its partial R^2
              after the full prewar control vector and state fixed effects
  EXCLUSION   placebo regressions of four PRE-1940 outcomes on the instrument
              with the same controls, and the smallest p-value across them
  VERDICT     an instrument is usable only if F >= 10, partial R^2 >= 0.05, and
              no placebo rejects at the five percent level

The narrow-branch instruments are the interesting case. If prewar industrial
LEVEL is what breaks the broad instrument, an instrument that allocates on a
capability orthogonal to county size and manufacturing share might survive.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_iv.parquet')
d['statefip']=(d.fips//1000).astype(int)
P=d.pop1940.replace(0,np.nan)

for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940',
          'popgrowth_3040','PCTILL3','PCTFRM3']:
    d[c]=pd.to_numeric(d[c],errors='coerce')
d['mfg_suppressed']=d.mfgshare1940.isna().astype(float)
d['prewar_imputed']=d.PCTILL3.isna().astype(float)
for c in ['mfgshare1940','blackshare1940','PCTILL3','PCTFRM3','popgrowth_3040']:
    d[c]=d[c].fillna(0)

# endogenous regressors, arsinh of dollars per resident
d['W_C']=np.arcsinh(1000*d.contract_k/P)
d['W_F']=np.arcsinh(1000*d.fac_public_k/P)
d['W_M']=np.arcsinh(1000*d.cdb_fac_military/P)

CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','mfg_suppressed','prewar_imputed']
SFE=pd.get_dummies(d.statefip,prefix='s',drop_first=True).astype(float)

# The instrument sweep. imp_* are counts of establishments allocated to a
# procurement branch in 1938; the branch codes are Jaworski's.
SPECS=[
 ('imp_total',      'All allocated establishments, every branch',      'W_C'),
 ('imp_fac',        'Allocated facilities (baseline)',                 'W_C'),
 ('imp_industrial', 'Facilities, machine tool, aero, optics, steel',   'W_C'),
 ('any_imp',        'Any allocated facility (extensive margin)',       'W_C'),
 ('imp_tool',       'Machine-tool branch only',                        'W_C'),
 ('imp_aero',       'Aeronautical branch only',                        'W_F'),
 ('imp_narrow',     'Aeronautical and optical branches only',          'W_F'),
 ('mil_prewar',     'Prewar Army and Navy sites',                      'W_M'),
 ('any_mil_prewar', 'Any prewar Army or Navy site',                    'W_M'),
]
d['imp_narrow']=d.imp_aero+d.imp_optic

# Pre-1940 outcomes. A prewar allocation must not predict these once the
# control vector is in: if it does, it carries prewar structure into the
# second stage by a route that does not pass through wartime production.
PLACEBO=[('mfgshare1940','1940 manufacturing share'),
         ('urbrate1940','1940 urban share'),
         ('logpop1940','1940 log population'),
         ('popgrowth_3040','1930--40 population growth')]

def fit(y,Xcols,extra=None,frame=None):
    f=frame if frame is not None else d
    X=pd.concat([f[Xcols].astype(float)]+([extra] if extra is not None else [])+[SFE],axis=1)
    q=pd.concat([f[[y]].astype(float),X],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    return sm.OLS(q[y],sm.add_constant(q.iloc[:,1:])).fit(
        cov_type='cluster',cov_kwds={'groups':f.loc[q.index,'statefip']}), q

def partial_r2(y,z,Xcols):
    """R^2 of the excluded instrument after residualising both on controls+FE."""
    X=pd.concat([d[Xcols].astype(float),SFE],axis=1)
    q=pd.concat([d[[y,z]].astype(float),X],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    Xq=sm.add_constant(q.iloc[:,2:])
    ry=sm.OLS(q[y],Xq).fit().resid
    rz=sm.OLS(q[z],Xq).fit().resid
    return float(np.corrcoef(ry,rz)[0,1]**2)

rows=[]
print('='*100)
print('IMP INSTRUMENT SPECIFICATION SWEEP')
print('='*100)
print(f'{"instrument":34s}{"endog":>7s}{"F":>9s}{"partial R2":>12s}{"min placebo p":>15s}{"  verdict"}')
print('-'*100)
for z,label,endog in SPECS:
    d[f'_z_{z}']=np.arcsinh(d[z].astype(float))
    zz=d[f'_z_{z}']
    r,_=fit(endog,CTRL,extra=zz.rename('Z'))
    F=float(r.f_test(np.eye(len(r.params))[list(r.params.index).index('Z')]).fvalue)
    pr2=partial_r2(endog,f'_z_{z}',CTRL)
    pl={}
    for y,ylab in PLACEBO:
        ctrl=[c for c in CTRL if c!=y]
        rp,_=fit(y,ctrl,extra=zz.rename('Z'))
        pl[ylab]=float(rp.pvalues['Z'])
    pmin=min(pl.values())
    ok = (F>=10) and (pr2>=0.05) and (pmin>=0.05)
    verdict='USABLE' if ok else ('weak' if pr2<0.05 else 'fails exclusion')
    print(f'{label[:33]:34s}{endog:>7s}{F:>9.1f}{pr2:>12.3f}{pmin:>15.3f}  {verdict}')
    rows.append({'instrument':label,'var':z,'endogenous':endog,
                 'F':round(F,1),'partial_r2':round(pr2,4),
                 'placebo':{k:round(v,4) for k,v in pl.items()},
                 'min_placebo_p':round(pmin,4),'usable':bool(ok)})

print('-'*100)
n_ok=sum(r['usable'] for r in rows)
print(f'{n_ok} of {len(rows)} specifications satisfy F>=10, partial R2>=0.05 and no placebo rejection.')

# Which placebo does the damage, and how badly?
print('\n' + '='*100)
print('WHICH PRE-WAR OUTCOME DOES EACH INSTRUMENT PREDICT?  (p-values, controls and state FE throughout)')
print('='*100)
hdr=f'{"instrument":34s}' + ''.join(f'{l.replace("1940 ","").replace("1930--40 ",""):>22s}' for _,l in PLACEBO)
print(hdr); print('-'*100)
for r in rows:
    print(f'{r["instrument"][:33]:34s}' + ''.join(f'{r["placebo"][l]:>22.3f}' for _,l in PLACEBO))

# The narrowest instrument is the one with a chance. Report its first stage in
# full so the reader can see exactly how little residual variation it moves.
best=min(rows,key=lambda r:(not r['usable'], -r['partial_r2']))
print(f'\nStrongest partial R^2 among all specifications: {best["instrument"]} '
      f'at {best["partial_r2"]:.3f} (F={best["F"]:.1f}, min placebo p={best["min_placebo_p"]:.3f})')

out={'specifications':rows,'n_usable':n_ok,'n_specs':len(rows),
     'thresholds':{'F':10,'partial_r2':0.05,'placebo_p':0.05}}
(AN/'imp_specifications.json').write_text(json.dumps(out,indent=2))
print(f'\n-> {AN/"imp_specifications.json"}')
