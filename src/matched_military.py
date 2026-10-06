#!/usr/bin/env python3
"""
The same matched design, applied to military installations.

Garin and Rothbaum establish the long-run effect of large publicly financed
industrial plants. No comparable estimate exists for the other large federal
capital allocation of the war: camps, airfields, depots, and proving grounds.
Section 5 shows the two are close to orthogonal in space and associated with
opposite postwar structures. That association is what this design tests.

Treatment: a county in the top decile of 1947 County Data Book military
facility spending per capita. Comparison and estimator as in the plant design.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm, pyreadstat
from scipy.spatial import cKDTree
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
s=pd.read_parquet(AN/'matched_sample_raw.parquet')
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
X0=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']
s['mil_pc']=pd.to_numeric(s.cdb_fac_military,errors='coerce').fillna(0)/s.pop1940.replace(0,np.nan)
cut=s.loc[s.mil_pc>0,'mil_pc'].quantile(0.90)
s['treat_mil']=((s.mil_pc>=cut)&(s.mil_pc>0)).astype(int)
print(f'military treatment: top decile of per-capita military facility spending')
print(f'  threshold ${cut*1000:.1f} per 1,000 residents')
print(f'  treated {int(s.treat_mil.sum()):,}  untreated {int((1-s.treat_mil).sum()):,}')
_td=s.loc[s.treat_mil==1,'cdb_fac_military'].sum()
_nat=pd.to_numeric(pd.read_parquet(AN/'master_panel_v3.parquet',
                                   columns=['cdb_fac_military']).cdb_fac_military,
                   errors='coerce').fillna(0).sum()
SHARES={'treated_dollars_bn': float(_td/1e6),
        'treated_share_sample': float(_td/s.cdb_fac_military.sum()),
        'treated_share_national': float(_td/_nat),
        'n_treated_predrop': int(s.treat_mil.sum())}
print(f'  their military dollars: ${_td/1e6:.2f}bn '
      f'({SHARES["treated_share_sample"]:.0%} of the estimation sample, '
      f'{SHARES["treated_share_national"]:.0%} of the national total)')
# drop plant-treated counties so the two treatments do not contaminate each other
s=s[~((s.treat==1)&(s.treat_mil==1))].copy()
print(f'  dropped counties receiving BOTH: sample now {len(s):,}')
# The dollar shares above are computed before this drop, which is the wrong base
# for describing the design: the counties the design actually studies are the
# post-drop ones. Recompute and store both, and let the prose quote the design's.
_td2=s.loc[s.treat_mil==1,'cdb_fac_military'].sum()
SHARES.update({
    'n_treated_design': int(s.treat_mil.sum()),
    'treated_dollars_bn_design': float(_td2/1e6),
    'treated_share_sample_design': float(_td2/s.cdb_fac_military.sum()),
    'treated_share_national_design': float(_td2/_nat)})
print(f'  design treated {SHARES["n_treated_design"]}: '
      f'${SHARES["treated_dollars_bn_design"]:.2f}bn '
      f'({SHARES["treated_share_sample_design"]:.1%} of sample, '
      f'{SHARES["treated_share_national_design"]:.1%} of national)')

s['_li70']=np.log(pd.to_numeric(s.medfaminc1970,errors='coerce').replace(0,np.nan))
s['_li50']=np.log(pd.to_numeric(s.medfaminc1950,errors='coerce').replace(0,np.nan))
# Employment levels behind the share. See the note in matched_estimates.py: the
# share falling is consistent with manufacturing shrinking and with everything
# else growing around it, and only the level distinguishes them.
s['_lemp70']=np.log(pd.to_numeric(s.emp1970,errors='coerce').replace(0,np.nan))
s['_lmfgemp70']=np.log((pd.to_numeric(s.mfgshare1970,errors='coerce')/100
                        *pd.to_numeric(s.emp1970,errors='coerce')).replace(0,np.nan))
# Tenure across the whole postwar window, plus house value. A base puts service
# families into rented quarters, so part of any ownership gap is composition;
# the timing and the price response are what bound that reading.
s['_lhv70']=np.log(pd.to_numeric(s.medhomeval1970,errors='coerce').replace(0,np.nan))
Zr=s[X0].astype(float); Zr=Zr.loc[:,Zr.std()>1e-10]
Zs=(Zr-Zr.mean())/Zr.std(); X=list(Zs.columns)
for c in X: s[c]=Zs[c]
ps=sm.Logit(s.treat_mil,sm.add_constant(Zs)).fit(disp=0,method='bfgs',maxiter=500)
s['pscore']=ps.predict(sm.add_constant(Zs))
lo,hi=s.loc[s.treat_mil==1,'pscore'].min(),s.loc[s.treat_mil==1,'pscore'].max()
sup=s[(s.pscore>=lo)&(s.pscore<=hi)].copy()
cal=0.2*sup.pscore.std()
tr=sup[sup.treat_mil==1]; ct=sup[sup.treat_mil==0]
dist,idx=cKDTree(ct[['pscore']].values).query(tr[['pscore']].values,k=min(3,len(ct)))
w=pd.Series(0.0,index=sup.fips); mt=[]
for i,(dd,ii) in enumerate(zip(np.atleast_2d(dist),np.atleast_2d(idx))):
    keep=[j for dj,j in zip(dd,ii) if dj<=cal]
    if not keep: continue
    mt.append(tr.iloc[i].fips)
    for j in keep: w[ct.iloc[j].fips]+=1.0/len(keep)
sup['mweight']=np.where(sup.treat_mil==1,sup.fips.isin(mt).astype(float),sup.fips.map(w).fillna(0))
print(f'  matched {len(mt)} treated to {int((sup.mweight>0).sum())-len(mt)} controls')

def smd(df,v,wcol=None):
    a=df[df.treat_mil==1]; b=df[df.treat_mil==0]
    if wcol is None: ma,mb=a[v].mean(),b[v].mean()
    else:
        ma=np.average(a[v],weights=a[wcol]) if a[wcol].sum()>0 else np.nan
        mb=np.average(b[v],weights=b[wcol]) if b[wcol].sum()>0 else np.nan
    sd=np.sqrt((a[v].var()+b[v].var())/2)
    return (ma-mb)/sd if sd>0 else np.nan
res={'threshold_per1000':round(float(cut*1000),3),'n_treated':int(len(mt))}
print('\n=== BALANCE ===')
res['balance']=[]
for v in CTRL:
    r0,r1=smd(s,v),smd(sup,v,'mweight')
    print(f'  {v:20s} raw {r0:+.3f}   matched {r1:+.3f}')
    res['balance'].append({'var':v,'raw':round(float(r0),4),'matched':round(float(r1),4)})
print(f'  imbalanced: raw {sum(1 for b in res["balance"] if abs(b["raw"])>.1)}/9  '
      f'matched {sum(1 for b in res["balance"] if abs(b["matched"])>.1)}/9')

OUT=[('logpop1970','log population 1970'),('mfgshare1970','manufacturing share 1970'),
     ('_li70','log family income 1970'),('ownrate1970','homeownership 1970'),
     ('mfgshare1960','manufacturing share 1960'),
     ('_lemp70','log total employment 1970'),
     ('_lmfgemp70','log manufacturing employment 1970'),
     ('ownrate1950','homeownership 1950'),('ownrate1960','homeownership 1960'),
     ('_lhv70','log median house value 1970')]
print('\n=== EFFECT OF A MILITARY INSTALLATION ===')
print(f'{"outcome":28s}{"matched":>11s}{"(SE)":>10s}{"p":>8s}{"n":>7s}')
res['effects']=[]
for y,lab in OUT:
    q=sup[[y,'treat_mil','mweight','statefip']+X].replace([np.inf,-np.inf],np.nan).dropna()
    m=q[q.mweight>0]
    r=sm.WLS(m[y],sm.add_constant(m[['treat_mil']+X].astype(float)),weights=m.mweight
             ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
    b,se,p=float(r.params.treat_mil),float(r.bse.treat_mil),float(r.pvalues.treat_mil)
    st='***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f'{lab:28s}{b:>11.4f}{st:<3s}({se:.4f}){p:>8.3f}{int(r.nobs):>7,}')
    res['effects'].append({'outcome':lab,'coef':round(b,5),'se':round(se,5),'p':round(p,4),'n':int(r.nobs)})
print('\n=== PLACEBO ===')
res['placebo']=[]
for y,lab in [('popgrowth_3040','log pop growth 1930-40'),('mfgshare1940','mfg share 1940'),
              ('ownrate1940','homeownership 1940')]:
    Xp=[v for v in X if v!=y and v!='sq_'+y]
    q=sup[[y,'treat_mil','mweight','statefip']+Xp].replace([np.inf,-np.inf],np.nan).dropna()
    m=q[q.mweight>0]
    r=sm.WLS(m[y],sm.add_constant(m[['treat_mil']+Xp].astype(float)),weights=m.mweight
             ).fit(cov_type='cluster',cov_kwds={'groups':m.statefip})
    b,p=float(r.params.treat_mil),float(r.pvalues.treat_mil)
    st='***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f'  {lab:26s}{b:>11.4f}{st:<3s} p={p:.3f}')
    res['placebo'].append({'outcome':lab,'coef':round(b,5),'p':round(p,4)})
res.update(SHARES)

# Four figures the manuscript quotes were printed here and stored nowhere: the
# control count, the state spread, and the two cluster counts. Same shape as the
# orphan-artifact bug my project notes record three times -- a pipeline re-run cannot
# correct a number no artifact holds.
_w = sup[sup.mweight > 0].copy(); _w['_st'] = (_w.fips // 1000).astype(int)
_tr = _w[_w.treat_mil == 1]
res['n_matched_controls']   = int((_w.treat_mil == 0).sum())
res['states_treated']       = int(_tr._st.nunique())
res['max_treated_per_state']= int(_tr._st.value_counts().max())
res['n_state_clusters']     = int(_w._st.nunique())
res['n_clusters_with_treated'] = int(_tr._st.nunique())

# The independence cross-tabulation, stated three times in the manuscript and
# computed by no script until now.
from scipy.stats import fisher_exact
# re-read the pre-drop frame: `s` has had the both-treated counties removed by
# this point, which is exactly the cell the test is about.
_b = pd.read_parquet(AN/'matched_sample_raw.parquet')
_b['mil_pc'] = pd.to_numeric(_b.cdb_fac_military, errors='coerce').fillna(0)/_b.pop1940.replace(0, np.nan)
_cut = _b.loc[_b.mil_pc > 0, 'mil_pc'].quantile(0.90)
_b['treat_mil'] = ((_b.mil_pc >= _cut) & (_b.mil_pc > 0)).astype(int)
_p, _m2 = (_b.treat == 1), (_b.treat_mil == 1)
_n11 = int((_p & _m2).sum()); _n10 = int((_p & ~_m2).sum())
_n01 = int((~_p & _m2).sum()); _n00 = int((~_p & ~_m2).sum())
res['independence'] = {
    'n_sample': int(len(_b)), 'n_plant': int(_p.sum()), 'n_mil': int(_m2.sum()),
    'n_both': _n11,
    'expected_both': round(float(_p.sum()) * float(_m2.sum()) / len(_b), 4),
    'fisher_p': round(float(fisher_exact([[_n11, _n10], [_n01, _n00]])[1]), 4)}
print(f"  independence: {res['independence']['n_plant']} plant, "
      f"{res['independence']['n_mil']} installation, {_n11} both against "
      f"{res['independence']['expected_both']:.2f} expected "
      f"(Fisher p = {res['independence']['fisher_p']:.3f})")
print(f"  matched controls {res['n_matched_controls']}, {res['states_treated']} states, "
      f"max {res['max_treated_per_state']} in one")

(AN/'matched_military.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"matched_military.json"}')
