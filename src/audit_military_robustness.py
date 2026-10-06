#!/usr/bin/env python3
"""Adversarial audit of the military-installation design: is it an artefact of the threshold?"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.spatial import cKDTree
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
base=pd.read_parquet(AN/'matched_sample_raw.parquet')
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
X0=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']
OUT=[('logpop1970','log pop'),('mfgshare1970','mfg share'),('ownrate1970','own rate')]

def design(df,tcol,seed_perm=None,k=3,cal_mult=0.2):
    d=df.copy()
    Zr=d[X0].astype(float); Zr=Zr.loc[:,Zr.std()>1e-10]
    Zs=(Zr-Zr.mean())/Zr.std(); X=list(Zs.columns)
    for c in X: d[c]=Zs[c]
    y=d[tcol] if seed_perm is None else pd.Series(
        np.random.default_rng(seed_perm).permutation(d[tcol].values),index=d.index)
    d['_t']=y.values
    if d._t.sum()<10: return None
    try: ps=sm.Logit(d._t,sm.add_constant(Zs)).fit(disp=0,method='bfgs',maxiter=400)
    except Exception: return None
    d['pscore']=ps.predict(sm.add_constant(Zs))
    lo,hi=d.loc[d._t==1,'pscore'].min(),d.loc[d._t==1,'pscore'].max()
    sup=d[(d.pscore>=lo)&(d.pscore<=hi)].copy()
    cal=cal_mult*sup.pscore.std()
    tr=sup[sup._t==1]; ct=sup[sup._t==0]
    if len(ct)<3 or len(tr)<10: return None
    dist,idx=cKDTree(ct[['pscore']].values).query(tr[['pscore']].values,k=min(k,len(ct)))
    w=pd.Series(0.0,index=sup.fips); mt=[]
    for i,(dd,ii) in enumerate(zip(np.atleast_2d(dist),np.atleast_2d(idx))):
        keep=[j for dj,j in zip(dd,ii) if dj<=cal]
        if not keep: continue
        mt.append(tr.iloc[i].fips)
        for j in keep: w[ct.iloc[j].fips]+=1.0/len(keep)
    sup['mweight']=np.where(sup._t==1,sup.fips.isin(mt).astype(float),sup.fips.map(w).fillna(0))
    out={'n_treated':len(mt)}
    for yv,lab in OUT:
        q=sup[[yv,'_t','mweight','statefip']+X].replace([np.inf,-np.inf],np.nan).dropna()
        m=q[q.mweight>0]
        if len(m)<40: continue
        r=sm.WLS(m[yv],sm.add_constant(m[['_t']+X].astype(float)),weights=m.mweight
                 ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
        out[lab]={'coef':round(float(r.params._t),4),'p':round(float(r.pvalues._t),4)}
    return out

base['mil_pc']=pd.to_numeric(base.cdb_fac_military,errors='coerce').fillna(0)/base.pop1940.replace(0,np.nan)
res={}
print('='*74); print('A. THRESHOLD SENSITIVITY — is the top decile doing the work?'); print('='*74)
print(f'{"definition":34s}{"treated":>9s}' + ''.join(f'{l:>13s}' for _,l in OUT))
res['thresholds']=[]
for q,lab in [(0.95,'top 5% of per-capita military $'),(0.90,'top 10% (baseline)'),
              (0.80,'top 20%'),(0.70,'top 30%')]:
    b=base.copy()
    cut=b.loc[b.mil_pc>0,'mil_pc'].quantile(q)
    b['_tm']=((b.mil_pc>=cut)&(b.mil_pc>0)).astype(int)
    b=b[~((b.treat==1)&(b._tm==1))]
    o=design(b,'_tm')
    if o:
        print(f'  {lab:32s}{o["n_treated"]:>9}' + ''.join(
            f'{o[l]["coef"]:>10.3f}{"***" if o[l]["p"]<.01 else "**" if o[l]["p"]<.05 else "*" if o[l]["p"]<.1 else "":<3s}'
            if l in o else f'{"---":>13s}' for _,l in OUT))
        res['thresholds'].append({'spec':lab,**o})
# absolute-dollar alternative
b=base.copy(); b['_tm']=(pd.to_numeric(b.cdb_fac_military,errors='coerce').fillna(0)>=10000).astype(int)
b=b[~((b.treat==1)&(b._tm==1))]
o=design(b,'_tm')
if o:
    print(f'  {"military $ >= $10M (absolute)":32s}{o["n_treated"]:>9}' + ''.join(
        f'{o[l]["coef"]:>10.3f}{"***" if o[l]["p"]<.01 else "**" if o[l]["p"]<.05 else "*" if o[l]["p"]<.1 else "":<3s}'
        if l in o else f'{"---":>13s}' for _,l in OUT))
    res['absolute']=o

print('\n'+'='*74); print('B. RANDOMIZATION INFERENCE — 500 permutations of the treatment'); print('='*74)
b=base.copy()
cut=b.loc[b.mil_pc>0,'mil_pc'].quantile(0.90)
b['_tm']=((b.mil_pc>=cut)&(b.mil_pc>0)).astype(int)
b=b[~((b.treat==1)&(b._tm==1))]
obs=design(b,'_tm')
null={l:[] for _,l in OUT}
for s in range(500):
    o=design(b,'_tm',seed_perm=s)
    if o:
        for _,l in OUT:
            if l in o: null[l].append(o[l]['coef'])
res['randomization']=[]
print(f'{"outcome":14s}{"observed":>11s}{"perm p":>9s}{"null sd":>10s}{"draws":>8s}')
for _,l in OUT:
    if l not in obs or not null[l]: continue
    arr=np.array(null[l]); o_=obs[l]['coef']
    pv=float((np.abs(arr)>=abs(o_)).mean())
    print(f'{l:14s}{o_:>11.4f}{pv:>9.3f}{arr.std():>10.4f}{len(arr):>8}')
    res['randomization'].append({'outcome':l,'observed':round(o_,4),'perm_p':round(pv,4),
                                 'null_sd':round(float(arr.std()),4),'n_draws':len(arr)})
(AN/'audit_military.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"audit_military.json"}')
