#!/usr/bin/env python3
"""
Robustness and falsification.

R1 PRE-TRENDS. Wartime exposure is assigned in 1940-45. If it "predicts"
   1920->1940 outcomes, the design is picking up pre-existing trajectory,
   not the war. This is the falsification test that matters most.
R2 Conley spatial standard errors (counties are not independent draws).
R3 Drop the 20 largest recipients (concentration leverage).
R4 Alternative fatal-burden denominators.
R5 Extensive vs intensive margin.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_v2.parquet')
d['statefip']=(d.fips//1000).astype(int); P=d.pop1940
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
res={}

def ols(df,y,X,cl='statefip'):
    s=df[[y]+X+[cl,'LATITUDE','LONGITUD']].replace([np.inf,-np.inf],np.nan).dropna(subset=[y]+X+[cl])
    D=pd.get_dummies(s[cl],prefix='st',drop_first=True).astype(float)
    XX=sm.add_constant(pd.concat([s[X],D],axis=1))
    r=sm.OLS(s[y],XX).fit(cov_type='cluster',cov_kwds={'groups':s[cl]})
    return r,s,XX

def conley(r,s,XX,cutoff_km=200):
    """Conley (1999) spatial HAC with a uniform kernel."""
    lat_raw=pd.to_numeric(s.LATITUDE,errors='coerce').values
    lon_raw=-pd.to_numeric(s.LONGITUD,errors='coerce').values
    ok=~(np.isnan(lat_raw)|np.isnan(lon_raw))
    lat=np.radians(lat_raw[ok]); lon=np.radians(lon_raw[ok])
    X=XX.values[ok].astype(float); u=np.asarray(r.resid)[ok]
    n,k=X.shape; XtX_inv=np.linalg.pinv(X.T@X)
    R=6371.0; meat=np.zeros((k,k)); B=400
    for i0 in range(0,n,B):
        i1=min(i0+B,n)
        dlat=lat[i0:i1,None]-lat[None,:]; dlon=lon[i0:i1,None]-lon[None,:]
        a=np.sin(dlat/2)**2+np.cos(lat[i0:i1,None])*np.cos(lat[None,:])*np.sin(dlon/2)**2
        dist=2*R*np.arcsin(np.sqrt(np.clip(a,0,1)))
        W=(dist<=cutoff_km).astype(float)
        meat+=X[i0:i1].T@(W*np.outer(u[i0:i1],u))@X
    V=XtX_inv@meat@XtX_inv
    return np.sqrt(np.clip(np.diag(V),0,None))

# ---- R1 PRE-TRENDS -------------------------------------------------------
print('='*78); print('R1  PRE-TREND FALSIFICATION: does wartime exposure "predict" 1920-1940?'); print('='*78)
# 1920 county population, for the pre-Depression window. The Haines file carries
# its own fips; 3,042 of 3,073 counties match, totalling 105.7 million against a
# 1920 continental census of 105.7 million. The 31 misses are counties created
# after 1920 (13 Florida, 6 Georgia, 6 Montana), 0.14 percent of 1940 population.
_h,_=pyreadstat.read_dta(str(ROOT/'data/raw/haines_icpsr2896/02896-0024-Data.dta'),
                         usecols=['county','fips','totpop'])
_h['fips']=pd.to_numeric(_h.fips,errors='coerce')
_h=_h[(pd.to_numeric(_h.county,errors='coerce')!=0)&_h.fips.notna()].copy()
_h['fips']=_h.fips.astype(int)
_IC=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
_ICM=dict(zip(_IC.city_fips.astype(int),_IC.parent_fips.astype(int)))
_h['fips']=_h.fips.map(lambda f:_ICM.get(f,f))
_h=_h[~(_h.fips//1000).isin([2,15,60,66,69,72,78])]
_h=_h.groupby('fips',as_index=False).totpop.sum().rename(columns={'totpop':'pop1920'})
d=d.merge(_h,on='fips',how='left')
d['pop1920']=pd.to_numeric(d.pop1920,errors='coerce')
_p30=pd.to_numeric(d.pop1930,errors='coerce')
d['pop_growth_2030']=np.log(_p30.replace(0,np.nan)/d.pop1920.replace(0,np.nan))
d['pop_growth_2040']=np.log(d.pop1940/_p30.replace(0,np.nan))
PRE=[('pop_growth_2030','log pop growth 1920->1930'),
     ('pop_growth_2040','log pop growth 1930->1940'),
     ('mfgshare1940','mfg share 1940 (pre-war level)')]
# Drop only the dependent variable from the control set, not both placebo
# outcomes from both regressions, which is what the earlier version did.
X=['W_C','W_F','W_M','B']+list(CTRL)
print(f'{"placebo outcome":34s}'+''.join(f'{k:>13s}' for k in ['W_C','W_F','W_M','B']))
res['pretrends']=[]
for y,lab in PRE:
    _drop={'pop_growth_2030':'popgrowth_3040','pop_growth_2040':'popgrowth_3040',
           'mfgshare1940':'mfgshare1940'}[y]
    Xu=[v for v in X if v not in (y,_drop)]
    r,s,_=ols(d,y,Xu)
    st=lambda k:('***' if r.pvalues[k]<.01 else '**' if r.pvalues[k]<.05 else '*' if r.pvalues[k]<.1 else '')
    print(f'{lab:34s}'+''.join(f'{r.params[k]:>10.4f}{st(k):<3s}' for k in ['W_C','W_F','W_M','B']))
    res['pretrends'].append({'outcome':lab,'n':int(r.nobs),
        'coef':{k:round(float(r.params[k]),5) for k in ['W_C','W_F','W_M','B']},
        'p':{k:round(float(r.pvalues[k]),4) for k in ['W_C','W_F','W_M','B']}})

# ---- R2 CONLEY -----------------------------------------------------------
print('\n'+'='*78); print('R2  CONLEY SPATIAL SE (200 km) vs STATE-CLUSTERED'); print('='*78)
X=['W_C','W_F','W_M','B']+CTRL
res['conley']=[]
for y,lab in [('logpop1970','log population 1970'),('mfgshare1970','mfg share 1970')]:
    r,s,XX=ols(d,y,X); cse=conley(r,s,XX)
    idx={c:i for i,c in enumerate(XX.columns)}
    print(f'\n{lab}:')
    print(f'  {"var":6s} {"coef":>10s} {"clust SE":>10s} {"Conley SE":>11s} {"t_conley":>9s}')
    row={'outcome':lab}
    for k in ['W_C','W_F','W_M','B']:
        b=r.params[k]; s1=r.bse[k]; s2=cse[idx[k]]
        print(f'  {k:6s} {b:10.4f} {s1:10.4f} {s2:11.4f} {b/s2:9.2f}')
        row[k]={'coef':round(float(b),5),'se_cluster':round(float(s1),5),
                'se_conley':round(float(s2),5),'t_conley':round(float(b/s2),3)}
    res['conley'].append(row)

# ---- R3 DROP TOP 20 ------------------------------------------------------
print('\n'+'='*78); print('R3  DROP THE 20 LARGEST CONTRACT RECIPIENTS'); print('='*78)
keep=d[~d.fips.isin(d.nlargest(20,'contract_k').fips)]
res['drop_top20']=[]
for y,lab in [('logpop1970','log pop 1970'),('mfgshare1970','mfg share 1970')]:
    rf,_,_=ols(d,y,X); rk,_,_=ols(keep,y,X)
    print(f'\n{lab}:  {"var":6s} {"full":>10s} {"drop-top20":>12s}')
    row={'outcome':lab}
    for k in ['W_C','W_F','W_M','B']:
        print(f'         {k:6s} {rf.params[k]:10.4f} {rk.params[k]:12.4f}')
        row[k]={'full':round(float(rf.params[k]),5),'drop20':round(float(rk.params[k]),5)}
    res['drop_top20'].append(row)

# ---- R4 ALTERNATIVE BURDEN DENOMINATORS ---------------------------------
print('\n'+'='*78); print('R4  ALTERNATIVE FATAL-BURDEN DENOMINATORS'); print('='*78)
d['B_male']=1000*d.deaths_all/pd.to_numeric(d.mtot,errors='coerce').replace(0,np.nan)
d['B_mlf'] =1000*d.deaths_all/pd.to_numeric(d.mlf1940,errors='coerce').replace(0,np.nan)
d['B_battle']=1000*d.deaths_battle/P
res['burden_alt']=[]
for bv,lab in [('B','per 1,000 residents'),('B_male','per 1,000 males'),
               ('B_mlf','per 1,000 men in the labor force'),('B_battle','battle deaths only')]:
    Xb=['W_C','W_F','W_M',bv]+CTRL
    r,_,_=ols(d,'logpop1970',Xb)
    print(f'  {lab:36s} coef={r.params[bv]:+.5f}  se={r.bse[bv]:.5f}  p={r.pvalues[bv]:.3f}  n={int(r.nobs):,}')
    res['burden_alt'].append({'denominator':lab,'coef':round(float(r.params[bv]),6),
                              'p':round(float(r.pvalues[bv]),4),'n':int(r.nobs)})

# ---- R5 EXTENSIVE vs INTENSIVE ------------------------------------------
print('\n'+'='*78); print('R5  EXTENSIVE (any) vs INTENSIVE (amount | any)'); print('='*78)
d['any_C']=(d.contract_k>0).astype(float); d['any_F']=(d.fac_public_k>0).astype(float)
d['any_M']=(d.cdb_fac_military>0).astype(float)
r,_,_=ols(d,'mfgshare1970',['any_C','any_F','any_M','B']+CTRL)
print('  extensive margin (mfg share 1970):')
for k in ['any_C','any_F','any_M']:
    print(f'    {k:7s} {r.params[k]:+.4f}  p={r.pvalues[k]:.3f}')
res['extensive']={k:{'coef':round(float(r.params[k]),5),'p':round(float(r.pvalues[k]),4)}
                  for k in ['any_C','any_F','any_M']}
(AN/'robustness.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"robustness.json"}')
