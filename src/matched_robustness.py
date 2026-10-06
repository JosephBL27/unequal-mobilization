#!/usr/bin/env python3
"""Robustness for the matched large-public-plant design."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm, pyreadstat
from scipy.spatial import cKDTree
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
base=pd.read_parquet(AN/'matched_sample_raw.parquet')
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
X0=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']
OUT=[('logpop1970','log pop 1970'),('mfgshare1970','mfg share 1970'),
     ('_li70','log income 1970'),('ownrate1970','homeownership 1970')]
res={}

def pipeline(s, k=3, cal_mult=0.2, tvar='treat'):
    s=s.copy()
    s['_li70']=np.log(pd.to_numeric(s.medfaminc1970,errors='coerce').replace(0,np.nan))
    Zr=s[X0].astype(float); Zr=Zr.loc[:,Zr.std()>1e-10]
    Zs=(Zr-Zr.mean())/Zr.std(); Xs=list(Zs.columns)
    for c in Xs: s[c]=Zs[c]
    ps=sm.Logit(s[tvar],sm.add_constant(Zs)).fit(disp=0,method='bfgs',maxiter=500)
    s['pscore']=ps.predict(sm.add_constant(Zs))
    lo,hi=s.loc[s[tvar]==1,'pscore'].min(),s.loc[s[tvar]==1,'pscore'].max()
    sup=s[(s.pscore>=lo)&(s.pscore<=hi)].copy()
    cal=cal_mult*sup.pscore.std()
    tr=sup[sup[tvar]==1]; ct=sup[sup[tvar]==0]
    if len(ct)<1 or len(tr)<5: return None
    dist,idx=cKDTree(ct[['pscore']].values).query(tr[['pscore']].values,k=min(k,len(ct)))
    # cKDTree returns 1-D arrays when k==1; np.atleast_2d would then fold every
    # treated unit into a single row, so the 1:1 specification matched one
    # county and called the result unstable. Reshape on the treated axis.
    dist=np.asarray(dist).reshape(len(tr),-1); idx=np.asarray(idx).reshape(len(tr),-1)
    w=pd.Series(0.0,index=sup.fips); mt=[]
    for i,(dd,ii) in enumerate(zip(dist,idx)):
        keep=[j for dj,j in zip(dd,ii) if dj<=cal]
        if not keep: continue
        mt.append(tr.iloc[i].fips)
        for j in keep: w[ct.iloc[j].fips]+=1.0/len(keep)
    sup['mweight']=np.where(sup[tvar]==1,sup.fips.isin(mt).astype(float),sup.fips.map(w).fillna(0))
    out={}
    for y,lab in OUT:
        q=sup[[y,tvar,'mweight','statefip']+Xs].replace([np.inf,-np.inf],np.nan).dropna()
        m=q[q.mweight>0]
        if len(m)<40: continue
        r=sm.WLS(m[y],sm.add_constant(m[[tvar]+Xs].astype(float)),weights=m.mweight
                 ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
        out[lab]={'coef':round(float(r.params[tvar]),4),'se':round(float(r.bse[tvar]),4),
                  'p':round(float(r.pvalues[tvar]),4),'n':int(r.nobs),'n_treated':len(mt)}
    return out

print('='*70); print('R1  MATCHING PARAMETERS'); print('='*70)
res['params']=[]
for k,cm,lab in [(1,0.2,'1:1, caliper 0.2sd'),(3,0.2,'3:1, caliper 0.2sd (baseline)'),
                 (5,0.2,'5:1, caliper 0.2sd'),(3,0.1,'3:1, caliper 0.1sd'),
                 (3,0.5,'3:1, caliper 0.5sd')]:
    o=pipeline(base,k,cm)
    if o:
        print(f'  {lab:32s} ' + '  '.join(f'{v["coef"]:+.3f}' for v in o.values()))
        res['params'].append({'spec':lab,**{kk:vv for kk,vv in o.items()}})
print(f'  {"":32s} ' + '  '.join(f'{l:>7s}' for _,l in OUT))

print('\n'+'='*70); print('R2  SAMPLE RESTRICTIONS'); print('='*70)
res['samples']=[]
# NOTE: a fourth restriction on 1940 metropolitan status used to sit here. The
# IPUMS metro extract is keyed on statefip/countyicp and carries no fips column,
# so the guard in matched_plant_design.py skipped the merge and in_metro1940 was
# all zeros -- the row silently reproduced the baseline. It is dropped rather
# than reported. The estimation sample already excludes the hundred largest
# manufacturing counties, which is the restriction that row was meant to proxy.
for cond,lab in [(base.pop1940>=10000,'pop $\\geq$ 10,000'),
                 (base.mfgemp1940>0,'any 1940 manufacturing')]:
    sub=base[cond]
    o=pipeline(sub)
    if o:
        print(f'  {lab:32s} n={len(sub):,}  ' + '  '.join(f'{v["coef"]:+.3f}' for v in o.values()))
        res['samples'].append({'spec':lab,'n':int(len(sub)),**o})

print('\n'+'='*70); print('R3  ADJACENCY: treated vs their untreated neighbours'); print('='*70)
adj,_=pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/NBER_county_adjacency2010.dta'))
adj['fipscounty']=pd.to_numeric(adj.fipscounty,errors='coerce')
adj['fipsneighbor']=pd.to_numeric(adj.fipsneighbor,errors='coerce')
tre=set(base.loc[base.treat==1,'fips'])
nb=adj[adj.fipscounty.isin(tre)&~adj.fipsneighbor.isin(tre)].fipsneighbor.dropna().astype(int).unique()
sub=base[(base.treat==1)|(base.fips.isin(nb))].copy()
print(f'  treated {int(sub.treat.sum())} vs {int((1-sub.treat).sum())} untreated neighbours')
# The neighbour-pool size is quoted twice in the manuscript and was printed here
# and stored nowhere, so it drifted to 481 and no re-run could correct it.
res['n_neighbour_pool']=int((1-sub.treat).sum())
res['n_treated_adjacency']=int(sub.treat.sum())
o=pipeline(sub)
if o:
    for lab,v in o.items():
        st='***' if v['p']<.01 else '**' if v['p']<.05 else '*' if v['p']<.1 else ''
        print(f'    {lab:26s}{v["coef"]:+9.4f}{st:<3s} p={v["p"]:.3f}  n={v["n"]}')
    res['adjacency']=o
(AN/'matched_robustness.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"matched_robustness.json"}')
