#!/usr/bin/env python3
"""Generate booktabs LaTeX tables into paper/tables/ from the saved results."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'; T=ROOT/'paper/tables'
T.mkdir(parents=True,exist_ok=True)

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

def ols(df,y,X):
    s=df[[y]+X+['statefip']].replace([np.inf,-np.inf],np.nan).dropna()
    D=pd.get_dummies(s.statefip,prefix='st',drop_first=True).astype(float)
    XX=sm.add_constant(pd.concat([s[X],D],axis=1))
    return sm.OLS(s[y],XX).fit(cov_type='cluster',cov_kwds={'groups':s.statefip})
def st(p): return '$^{***}$' if p<.01 else '$^{**}$' if p<.05 else '$^{*}$' if p<.1 else ''
def cell(r,k): return f'{r.params[k]:.4f}{st(r.pvalues[k])}', f'({r.bse[k]:.4f})'

# ---------------- T1 summary statistics ----------------------------------
rows=[('\\emph{Wartime exposure}',None,None,None,None,None),
 ('Army/AAF deaths','deaths_all',0,None,None,'count'),
 ('Fatal burden $B_i$ (per 1{,}000 residents)','B',2,None,None,'rate'),
 ('War supply contracts (\\$000s)','contract_k',0,None,None,'count'),
 ('Publicly financed war plant (\\$000s)','fac_public_k',0,None,None,'count'),
 ('Military installations (\\$000s)','cdb_fac_military',0,None,None,'count'),
 ('\\emph{Prewar characteristics, 1940}',None,None,None,None,None),
 ('Population','pop1940',0,None,None,'count'),
 ('Urban share','urbrate1940',3,None,None,'rate'),
 ('Black population share','blackshare1940',3,None,None,'rate'),
 ('Manufacturing employment share','mfgshare1940',3,None,None,'rate'),
 ('Log population growth 1930--40','popgrowth_3040',3,None,None,'rate'),
 ('\\emph{Postwar outcomes}',None,None,None,None,None),
 ('Population 1950','pop1950',0,None,None,'count'),
 ('Population 1970','pop1970',0,None,None,'count'),
 ('Manufacturing share 1960','mfgshare1960',2,None,None,'rate'),
 ('Manufacturing share 1970','mfgshare1970',2,None,None,'rate'),
 ('Median family income 1950 (\\$)','medfaminc1950',0,None,None,'count'),
 ('Median family income 1970 (\\$)','medfaminc1970',0,None,None,'count'),
 ('Homeownership rate 1970 (\\%)','ownrate1970',1,None,None,'rate')]
L=['\\begin{tabular}{lrrrrrr}','\\toprule',
   'Variable & Mean & SD & p10 & Median & p90 & $N$ \\\\','\\midrule']
for lab,v,dp,_,_,_ in rows:
    if v is None: L.append(f'\\multicolumn{{7}}{{l}}{{{lab}}} \\\\'); continue
    s=pd.to_numeric(d[v],errors='coerce').dropna(); f=f'{{:,.{dp}f}}'
    L.append(f'\\quad {lab} & '+' & '.join(f.format(x) for x in
             [s.mean(),s.std(),s.quantile(.1),s.median(),s.quantile(.9)])+f' & {len(s):,} \\\\')
L+=['\\bottomrule','\\end{tabular}']
(T/'tab_summary.tex').write_text('\n'.join(L))

# ---------------- T2 validation against the 1947 County Data Book --------
from scipy.stats import pearsonr, spearmanr
cd=d.dropna(subset=['cdb_contracts_k'])
pairs=[('Major war supply contracts','contract_k','cdb_contracts_k'),
       ('War plant, publicly financed','fac_public_k','cdb_fac_industrial')]
L=['\\begin{tabular}{lrrrrr}','\\toprule',
   'Series & Reconstructed & County Data Book & Pearson & Pearson & Spearman \\\\',
   ' & (\\$bn) & (\\$bn) & (levels) & (log$1{+}x$) & (rank) \\\\','\\midrule']
for lab,a,b in pairs:
    if b not in cd.columns: continue
    x=pd.to_numeric(cd[a],errors='coerce'); y=pd.to_numeric(cd[b],errors='coerce')
    ok=x.notna()&y.notna(); x,y=x[ok],y[ok]
    L.append(f'{lab} & {x.sum()/1e6:.1f} & {y.sum()/1e6:.1f} & {pearsonr(x,y)[0]:.3f} & '
             f'{pearsonr(np.log1p(x),np.log1p(y))[0]:.3f} & {spearmanr(x,y).statistic:.3f} \\\\')
L+=['\\bottomrule','\\end{tabular}']
(T/'tab_validation.tex').write_text('\n'.join(L))

# ---------------- T3 allocation ------------------------------------------
# Both burden measures belong in this table. The civic rate and the per-enlistee
# rate answer different questions and give different answers once the prewar
# vector is in, and printing only one of them next to prose that quotes the
# other is how a table came to contradict the sentence pointing at it.
# v2 carries no enlistment denominator; v3 does, and its validity screen is
# already computed there by analysis_exposure.py
_v3=pd.read_parquet(AN/'master_panel_v3.parquet')[['fips','B_A','valid_BA']]
d=d.merge(_v3,on='fips',how='left')
d['B_A']=pd.to_numeric(d.B_A,errors='coerce')
valid_BA=d.valid_BA.fillna(False).astype(bool)
INV=[('W_C','Contracts $W^C$'),('W_F','War plant $W^F$'),('W_M','Military $W^M$')]
BLOCKS=[('$B_i$, state effects only','B',[],       d),
        ('$B_i$, plus prewar controls','B',CTRL,   d),
        ('$B_i^{A}$, plus prewar controls','B_A',CTRL, d[valid_BA])]
L=['\\begin{tabular}{lccc}','\\toprule',
   '& '+' & '.join(lab for _,lab in INV)+' \\\\',
   '& (1) & (2) & (3) \\\\','\\midrule']
NS=[]
for rowlab,bvar,ctrl,frame in BLOCKS:
    rs=[ols(frame,y,[bvar]+ctrl) for y,_ in INV]
    L.append(f'{rowlab} & '+' & '.join(cell(r,bvar)[0] for r in rs)+' \\\\')
    L.append(' & '+' & '.join(cell(r,bvar)[1] for r in rs)+' \\\\')
    NS.append(int(rs[0].nobs))
L+=['\\midrule',
    'State fixed effects & Yes & Yes & Yes \\\\',
    f'$N$ (rows 1--2; row 3) & \\multicolumn{{3}}{{c}}{{{NS[0]:,}; {NS[2]:,}}} \\\\',
    '\\bottomrule','\\end{tabular}']
(T/'tab_allocation.tex').write_text('\n'.join(L))

# ---------------- T4 main outcomes ---------------------------------------
X=['W_C','W_F','W_M','B']+CTRL
# The header cells set the column widths here, not the coefficients, so putting
# the year on its own row is what makes this table legible: it renders at about
# 10pt instead of 7.5 after \resizebox, with nothing dropped.
OUT=[('logpop1950','Log pop.','1950'),('logpop1970','Log pop.','1970'),
     ('mfgshare1960','Mfg.\\ share','1960'),('mfgshare1970','Mfg.\\ share','1970'),
     ('_li50','Log income','1950'),('_li70','Log income','1970'),
     ('ownrate1970','Own rate','1970')]
d['_li50']=np.log(pd.to_numeric(d.medfaminc1950,errors='coerce').replace(0,np.nan))
d['_li70']=np.log(pd.to_numeric(d.medfaminc1970,errors='coerce').replace(0,np.nan))
rs=[ols(d,y,X) for y,_,_ in OUT]
L=['\\begin{tabular}{l'+'c'*len(OUT)+'}','\\toprule',
   '& '+' & '.join(f'({i+1})' for i in range(len(OUT)))+' \\\\',
   '& '+' & '.join(lab for _,lab,_ in OUT)+' \\\\',
   '& '+' & '.join(yr for _,_,yr in OUT)+' \\\\','\\midrule']
NAMES={'W_C':'Contracts $W^C_i$','W_F':'War plant $W^F_i$',
       'W_M':'Military $W^M_i$','B':'Fatal burden $B_i$'}
for k,nm in NAMES.items():
    L.append(f'{nm} & '+' & '.join(cell(r,k)[0] for r in rs)+' \\\\')
    L.append(' & '+' & '.join(cell(r,k)[1] for r in rs)+' \\\\')
L+=['\\midrule','Prewar controls & '+' & '.join(['Yes']*len(OUT))+' \\\\',
    'State fixed effects & '+' & '.join(['Yes']*len(OUT))+' \\\\',
    '$N$ & '+' & '.join(f'{int(r.nobs):,}' for r in rs)+' \\\\',
    '$R^2$ & '+' & '.join(f'{r.rsquared:.3f}' for r in rs)+' \\\\','\\bottomrule','\\end{tabular}']
(T/'tab_main.tex').write_text('\n'.join(L))
print('wrote:', ', '.join(sorted(p.name for p in T.glob('*.tex'))))
