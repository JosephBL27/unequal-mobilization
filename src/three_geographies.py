#!/usr/bin/env python3
"""
The war state did not make one allocation. It made three, and they do not
coincide:
    W^C  procurement contracts      - temporary demand, no asset left behind
    W^F  industrial war plant       - durable productive capital
    W^M  military installations     - camps, bases, depots; payroll, not plant

This computes the pairwise geography of all three against Army/AAF fatal loss,
and asks the question the paper has not yet asked: conditional on receiving
ANY federal war investment, did casualty-heavy counties receive plant or base?
"""
import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
m=pd.read_parquet(AN/'master_panel.parquet')
# The industrial/military split comes from the panel itself, which carries the
# 1947 County Data Book series folded across independent cities on the same
# geography as every other variable. It used to be merged in from a separate
# unfolded file, which lost Baltimore, St. Louis, and the Virginia cities.
d=m.copy()
d['cdb_fac_military']=d.cdb_fac_military.fillna(0)
d['cdb_fac_industrial']=d.cdb_fac_industrial.fillna(0)
d=d[d.pop1940>0].copy()
res={}

EXPO={'W_C  contracts':'contract_k',
      'W_F  industrial plant':'fac_public_k',
      'W_M  military installations':'cdb_fac_military',
      'D    Army/AAF deaths':'deaths_all'}

def overlap(a,b):
    pa,pb=a/a.sum(), b/b.sum()
    A=float(np.minimum(pa,pb).sum())
    mm=0.5*(pa+pb)
    kl=lambda x: float(np.sum(x[x>0]*np.log2(x[x>0]/mm[x>0])))
    return A, 0.5*kl(pa)+0.5*kl(pb)

print('='*72); print('PAIRWISE GEOGRAPHY OF THE FOUR WARTIME ALLOCATIONS'); print('='*72)
print(f'{"":30s} {"overlap A":>10s} {"JS bits":>9s} {"Spearman":>9s}')
keys=list(EXPO)
pw={}
for i in range(len(keys)):
    for j in range(i+1,len(keys)):
        a,b=d[EXPO[keys[i]]],d[EXPO[keys[j]]]
        A,JS=overlap(a,b); rho=spearmanr(a,b).statistic
        lab=f'{keys[i].split()[0]} x {keys[j].split()[0]}'
        pw[lab]={'A':round(A,4),'JS':round(JS,4),'spearman':round(float(rho),4)}
        print(f'{lab:30s} {A:10.3f} {JS:9.3f} {rho:9.3f}')
res['pairwise']=pw

# per-capita: net out county size
print('\n'+'='*72); print('PER CAPITA (county size netted out)'); print('='*72)
P=d.pop1940
pc={k:(d[v]/P) for k,v in EXPO.items()}
pc['D    Army/AAF deaths']=1000*d.deaths_all/P
print(f'{"":30s} {"Spearman vs fatal burden":>26s}')
res['percapita_vs_burden']={}
for k in keys[:3]:
    rho=spearmanr(pc[k],pc['D    Army/AAF deaths']).statistic
    res['percapita_vs_burden'][k.split()[0]]=round(float(rho),4)
    print(f'{k:30s} {rho:26.3f}')

# ---- THE CONDITIONAL QUESTION -------------------------------------------
print('\n'+'='*72)
print('CONDITIONAL ON RECEIVING FEDERAL WAR INVESTMENT: PLANT OR BASE?')
print('='*72)
d['has_plant']=d.fac_public_k>0
d['has_base'] =d.cdb_fac_military>0
d['burden']   =1000*d.deaths_all/P
inv=d[d.has_plant|d.has_base].copy()
inv['type']=np.where(inv.has_plant&inv.has_base,'both',
             np.where(inv.has_plant,'plant only','base only'))
print(f'counties receiving any war facility: {len(inv):,} of {len(d):,}\n')
g=inv.groupby('type').agg(counties=('burden','size'), med_burden=('burden','median'),
        mean_burden=('burden','mean'), med_pop=('pop1940','median'),
        med_urban=('urbrate1940','median'), med_mfg=('mfgshare1940','median'))
print(g.round(3).to_string())
res['conditional']=g.round(4).to_dict()

# among investment-receiving counties, does burden predict getting plant vs base?
sub=inv[inv.type!='both']
y=(sub.type=='plant only').astype(int)
rho=spearmanr(sub.burden,y).statistic
print(f'\nSpearman(fatal burden, receives PLANT rather than BASE) = {rho:.3f}  n={len(sub):,}')
res['burden_predicts_plant_vs_base']=round(float(rho),4)

lo,hi=sub.burden.quantile(.25),sub.burden.quantile(.75)
print(f'  low-burden quartile  (<{lo:.1f}/1000): {(sub[sub.burden<=lo].type=="plant only").mean():.1%} got a plant')
print(f'  high-burden quartile (>{hi:.1f}/1000): {(sub[sub.burden>=hi].type=="plant only").mean():.1%} got a plant')
res['plant_share_low_burden_q']=round(float((sub[sub.burden<=lo].type=='plant only').mean()),4)
res['plant_share_high_burden_q']=round(float((sub[sub.burden>=hi].type=='plant only').mean()),4)

# The raw quartile gap is suggestive, so it has to be run down rather than
# reported. Regress the plant-rather-than-base indicator on fatal burden with
# the full prewar vector and state effects: the gap is a composition artifact
# of where plants and bases went, not a response to loss.
import statsmodels.api as sm
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3']
q=sub.copy()
for c in CTRL: q[c]=pd.to_numeric(q[c],errors='coerce')
q['mfg_suppressed']=q.mfgshare1940.isna().astype(float)
for c in CTRL: q[c]=q[c].fillna(0)
q['statefip']=(q.fips//1000).astype(int)
q['y']=(q.type=='plant only').astype(float)
SFE=pd.get_dummies(q.statefip,prefix='s',drop_first=True).astype(float)
X=pd.concat([q[['burden']+CTRL+['mfg_suppressed']].astype(float),SFE],axis=1)
Z=pd.concat([q[['y']],X],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
Xz=Z.iloc[:,1:]
# a handful of state dummies are collinear on this 736-county subsample; drop
# them by rank rather than letting the fit come back rank-deficient
keep=[c for c in Xz.columns if Xz[c].std()>1e-12]
Xz=Xz[keep]
_,rcols=np.linalg.qr(Xz.values.astype(float))
indep=[keep[i] for i in range(len(keep)) if abs(rcols[i,i])>1e-8]
r=sm.OLS(Z.y,sm.add_constant(Xz[indep])).fit(
    cov_type='cluster',cov_kwds={'groups':q.loc[Z.index,'statefip']})
print(f'  conditional on prewar X and state FE: coef {r.params["burden"]:+.4f} '
      f'(se {r.bse["burden"]:.4f})  p = {r.pvalues["burden"]:.3f}   n={len(Z):,}')
res['plant_vs_base_controlled']={'coef':round(float(r.params['burden']),4),
                                 'se':round(float(r.bse['burden']),4),
                                 'p':round(float(r.pvalues['burden']),4),
                                 'n':int(len(Z))}

(AN/'three_geographies.json').write_text(json.dumps(res,indent=2,default=str))
d.to_parquet(AN/'master_panel_v2.parquet',index=False)
print(f'\n-> {AN/"three_geographies.json"}')
