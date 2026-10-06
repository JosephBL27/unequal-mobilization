#!/usr/bin/env python3
"""Balance, matching, and treatment-effect estimates for the large-public-plant design."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.spatial import cKDTree
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
s=pd.read_parquet(AN/'matched_sample_raw.parquet')
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
X=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']
res={}

# ---- propensity score ---------------------------------------------------
# standardise: latitude/longitude and squared terms are on wildly different
# scales, which makes the Hessian numerically singular
Zr=s[X].astype(float)
Zr=Zr.loc[:, Zr.std()>1e-10]
Zs=(Zr-Zr.mean())/Zr.std()
X=[c for c in X if c in Zs.columns]
Z=sm.add_constant(Zs)
ps=sm.Logit(s.treat,Z).fit(disp=0, method='bfgs', maxiter=500)
s['pscore']=ps.predict(Z)
for c in X: s[c]=Zs[c]        # keep the standardised versions for the outcome models
print(f'propensity model: pseudo-R2 {ps.prsquared:.3f}, n={int(ps.nobs):,}')
# common support
lo,hi=s.loc[s.treat==1,'pscore'].min(), s.loc[s.treat==1,'pscore'].max()
s['on_support']=(s.pscore>=lo)&(s.pscore<=hi)
print(f'common support [{lo:.4f}, {hi:.4f}] retains '
      f'{int(s.on_support.sum()):,} counties ({int(s[s.on_support].treat.sum())} treated)')

# ---- nearest-neighbour matching, 3:1 with replacement, caliper 0.2 sd ----
sup=s[s.on_support].copy()
cal=0.2*sup.pscore.std()
tr=sup[sup.treat==1]; ct=sup[sup.treat==0]
tree=cKDTree(ct[['pscore']].values)
dist,idx=tree.query(tr[['pscore']].values,k=min(3,len(ct)))
rows=[]
for i,(dd,ii) in enumerate(zip(np.atleast_2d(dist),np.atleast_2d(idx))):
    keep=[j for dj,j in zip(dd,ii) if dj<=cal]
    if not keep: continue
    rows.append({'t_fips':tr.iloc[i].fips,'controls':[int(ct.iloc[j].fips) for j in keep]})
matched_t=[r['t_fips'] for r in rows]
w=pd.Series(0.0,index=sup.fips)
for r in rows:
    for c in r['controls']: w[c]+=1.0/len(r['controls'])
sup['mweight']=np.where(sup.treat==1, sup.fips.isin(matched_t).astype(float),
                        sup.fips.map(w).fillna(0))
print(f'matched: {len(matched_t)} treated to {int((sup.mweight>0).sum())-len(matched_t)} distinct controls '
      f'(caliper {cal:.4f})')
res['setup']={'pseudo_r2':round(float(ps.prsquared),4),'n_support':int(s.on_support.sum()),
              'n_matched_treated':len(matched_t),'caliper':round(float(cal),5)}

# ---- balance ------------------------------------------------------------
def smd(df,v,wcol=None):
    a=df[df.treat==1]; b=df[df.treat==0]
    if wcol is None: ma,mb,va,vb=a[v].mean(),b[v].mean(),a[v].var(),b[v].var()
    else:
        wa,wb=a[wcol],b[wcol]
        ma=np.average(a[v],weights=wa) if wa.sum()>0 else np.nan
        mb=np.average(b[v],weights=wb) if wb.sum()>0 else np.nan
        va,vb=a[v].var(),b[v].var()
    sd=np.sqrt((va+vb)/2)
    return (ma-mb)/sd if sd>0 else np.nan
print('\n=== BALANCE (standardised mean difference) ===')
print(f'{"covariate":22s}{"raw":>10s}{"matched":>12s}')
res['balance']=[]
for v in CTRL:
    r0=smd(s,v); r1=smd(sup,v,'mweight')
    print(f'{v:22s}{r0:>10.3f}{r1:>12.3f}')
    res['balance'].append({'var':v,'smd_raw':round(float(r0),4),'smd_matched':round(float(r1),4)})
bad0=sum(1 for b in res['balance'] if abs(b['smd_raw'])>0.10)
bad1=sum(1 for b in res['balance'] if abs(b['smd_matched'])>0.10)
print(f'\ncovariates imbalanced (|SMD|>0.10): raw {bad0}/{len(CTRL)}  matched {bad1}/{len(CTRL)}')
res['imbalanced_raw']=bad0; res['imbalanced_matched']=bad1

# ---- estimates ----------------------------------------------------------
sup['_li70']=np.log(pd.to_numeric(sup.medfaminc1970,errors='coerce').replace(0,np.nan))
sup['_li50']=np.log(pd.to_numeric(sup.medfaminc1950,errors='coerce').replace(0,np.nan))
# The manufacturing SHARE has total employment in its denominator, so a county
# that adds non-manufacturing jobs shows a falling share with manufacturing
# employment unchanged. The two levels below separate those cases; without them
# a share result cannot be read as a statement about manufacturing at all.
sup['_lemp70']=np.log(pd.to_numeric(sup.emp1970,errors='coerce').replace(0,np.nan))
sup['_lmfgemp70']=np.log((pd.to_numeric(sup.mfgshare1970,errors='coerce')/100
                          *pd.to_numeric(sup.emp1970,errors='coerce')).replace(0,np.nan))
OUT=[('logpop1970','log population 1970'),('mfgshare1970','manufacturing share 1970'),
     ('_li70','log family income 1970'),('ownrate1970','homeownership 1970'),
     ('_li50','log family income 1950'),('mfgshare1960','manufacturing share 1960'),
     ('_lemp70','log total employment 1970'),
     ('_lmfgemp70','log manufacturing employment 1970')]
print('\n=== TREATMENT EFFECTS (large new public plant, >$10M) ===')
print(f'{"outcome":28s}{"raw diff":>11s}{"matched":>11s}{"(SE)":>10s}{"p":>8s}{"IPW":>11s}{"n":>7s}')
res['effects']=[]
for y,lab in OUT:
    q=sup[[y,'treat','mweight','pscore','statefip']+X].replace([np.inf,-np.inf],np.nan).dropna()
    raw=q[q.treat==1][y].mean()-q[q.treat==0][y].mean()
    m=q[q.mweight>0]
    r=sm.WLS(m[y],sm.add_constant(m[['treat']+X].astype(float)),weights=m.mweight
             ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
    ipw=np.where(q.treat==1,1/q.pscore,1/(1-q.pscore)); ipw=np.clip(ipw,0,20)
    ri=sm.WLS(q[y],sm.add_constant(q[['treat']+X].astype(float)),weights=ipw
              ).fit(cov_type='cluster',cov_kwds={'groups':q.statefip})
    b,se,p=float(r.params.treat),float(r.bse.treat),float(r.pvalues.treat)
    st='***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f'{lab:28s}{raw:>11.4f}{b:>11.4f}{st:<3s}({se:.4f}){p:>8.3f}{float(ri.params.treat):>11.4f}{int(r.nobs):>7,}')
    res['effects'].append({'outcome':lab,'raw':round(raw,5),'matched':round(b,5),'se':round(se,5),
                           'p':round(p,4),'ipw':round(float(ri.params.treat),5),'n':int(r.nobs)})
# ---- placebo on pre-treatment outcomes ---------------------------------
print('\n=== PLACEBO: pre-treatment outcomes ===')
res['placebo']=[]
for y,lab in [('popgrowth_3040','log pop growth 1930-40'),('mfgshare1940','mfg share 1940'),
              ('ownrate1940','homeownership 1940')]:
    Xp=[v for v in X if v!=y and v!='sq_'+y]
    q=sup[[y,'treat','mweight','statefip']+Xp].replace([np.inf,-np.inf],np.nan).dropna()
    m=q[q.mweight>0]
    r=sm.WLS(m[y],sm.add_constant(m[['treat']+Xp].astype(float)),weights=m.mweight
             ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
    b,p=float(r.params.treat),float(r.pvalues.treat)
    st='***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f'  {lab:28s}{b:>11.4f}{st:<3s} p={p:.3f}  n={int(r.nobs):,}')
    res['placebo'].append({'outcome':lab,'coef':round(b,5),'p':round(p,4),'n':int(r.nobs)})
# Cluster counts, quoted in the Table 7 note and previously stored nowhere: the
# note said "over 40 state clusters" for a design that clusters on 44.
_m=sup[sup.mweight>0].copy(); _m["_st"]=(_m.fips//1000).astype(int)
res['n_state_clusters']=int(_m._st.nunique())
res['n_states_with_treated']=int(_m[_m.treat==1]._st.nunique())
print(f"  state clusters {res['n_state_clusters']}, "
      f"{res['n_states_with_treated']} carrying a treated county")
(AN/'matched_results.json').write_text(json.dumps(res,indent=2))
sup.to_parquet(AN/'matched_sample.parquet',index=False)
print(f'\n-> {AN/"matched_results.json"}')
