#!/usr/bin/env python3
"""
Does the 1938 Industrial Mobilization Plan satisfy the exclusion restriction?

The allocation was made before the war, so it cannot be caused by wartime
investment. That secures no-reverse-causality. It does not secure exclusion.
The Munitions Board allocated plants that were already industrially capable, so
the instrument may predict postwar outcomes through prewar industrial structure
rather than through wartime production.

Two tests:
  (a) PLACEBO. Does the instrument predict PRE-1940 outcomes, conditional on the
      same controls? It should not.
  (b) OVER-CONTROL. Does the second-stage estimate survive adding richer prewar
      industrial controls? If the effect is an artefact of industrial structure
      it will move sharply.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm, numpy.linalg as la
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_iv.parquet')
d['statefip']=(d.fips//1000).astype(int); P=d.pop1940.replace(0,np.nan)
for c in ['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
          'PCTILL3','PCTFRM3','pop1930','mfgemp1940','mfgwage1940','MANEMP3A']:
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

def ols(y,X,df):
    s=df[[y]+X+['statefip']].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float); D=D.loc[:,D.std()>0]
    M=sm.add_constant(pd.concat([s[X],D],axis=1))
    M=M.loc[:,M.std().fillna(0)>1e-12]
    q,r=la.qr(M.values.astype(float)); tol=abs(np.diag(r)).max()*1e-10
    M=M.iloc[:,[i for i in range(M.shape[1]) if abs(r[i,i])>tol]]
    return sm.OLS(s[y],M).fit(cov_type='cluster',cov_kwds={'groups':s.statefip})

res={}
print('='*76)
print('(a) PLACEBO: does the instrument predict PRE-WAR outcomes?')
print('='*76)
d['pregrowth']=np.log(d.pop1940/d.pop1930.replace(0,np.nan))
d['pre_mfgwage']=np.log(pd.to_numeric(d.mfgwage1940,errors='coerce').replace(0,np.nan))
PLA=[('pregrowth','log population growth 1930-40'),
     ('mfgshare1940','manufacturing share 1940'),
     ('pre_mfgwage','log manufacturing payroll 1940'),
     ('urbrate1940','urban share 1940')]
res['placebo']=[]
print(f'{"pre-war outcome":34s}{"IMP industrial":>18s}{"p":>8s}{"prewar bases":>16s}{"p":>8s}')
for y,lab in PLA:
    C=[c for c in CTRL if c!=y]
    r1=ols(y,['z_imp_industrial']+C,d); r2=ols(y,['z_mil_prewar']+C,d)
    b1,p1=r1.params['z_imp_industrial'],r1.pvalues['z_imp_industrial']
    b2,p2=r2.params['z_mil_prewar'],r2.pvalues['z_mil_prewar']
    st=lambda p:'***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f'{lab:34s}{b1:>15.4f}{st(p1):<3s}{p1:>8.3f}{b2:>13.4f}{st(p2):<3s}{p2:>8.3f}')
    res['placebo'].append({'outcome':lab,'imp_coef':round(float(b1),5),'imp_p':round(float(p1),4),
                           'mil_coef':round(float(b2),5),'mil_p':round(float(p2),4)})

print('\n'+'='*76)
print('(b) REDUCED FORM: instrument -> 1970 outcomes, adding prewar industry controls')
print('='*76)
RICH=CTRL+['MANEMP3A']
d['_li70']=np.log(pd.to_numeric(d.medfaminc1970,errors='coerce').replace(0,np.nan))
res['reduced_form']=[]
print(f'{"1970 outcome":30s}{"baseline":>12s}{"p":>8s}{"+prewar mfg":>14s}{"p":>8s}{"change":>10s}')
for y,lab in [('logpop1970','log population'),('mfgshare1970','mfg share'),
              ('_li70','log income'),('ownrate1970','homeownership')]:
    a=ols(y,['z_imp_industrial']+CTRL,d); b=ols(y,['z_imp_industrial']+RICH,d)
    ba,pa=a.params['z_imp_industrial'],a.pvalues['z_imp_industrial']
    bb,pb=b.params['z_imp_industrial'],b.pvalues['z_imp_industrial']
    ch=(bb-ba)/abs(ba) if ba else np.nan
    print(f'{lab:30s}{ba:>12.4f}{pa:>8.3f}{bb:>14.4f}{pb:>8.3f}{ch:>9.0%}')
    res['reduced_form'].append({'outcome':lab,'baseline':round(float(ba),5),'p_base':round(float(pa),4),
                                'rich':round(float(bb),5),'p_rich':round(float(pb),4),
                                'pct_change':None if np.isnan(ch) else round(float(ch),3)})
(AN/'iv_validity.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"iv_validity.json"}')
