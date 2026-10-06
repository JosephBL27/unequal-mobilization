#!/usr/bin/env python3
"""Appendix tables: construction, coverage, robustness, falsification."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'; T=ROOT/'paper/tables'
rob=json.loads((AN/'robustness.json').read_text())
rob_int=json.loads((ROOT/'data/analysis/regression_results.json').read_text()).get('interactions',[])
tg =json.loads((AN/'three_geographies.json').read_text())
d=pd.read_parquet(AN/'master_panel_v2.parquet')
d['statefip']=(d.fips//1000).astype(int); P=d.pop1940
d['W_C']=np.arcsinh(1000*d.contract_k/P); d['W_F']=np.arcsinh(1000*d.fac_public_k/P)
d['W_M']=np.arcsinh(1000*d.cdb_fac_military/P); d['B']=1000*d.deaths_all/P

def tab(name, header, rows, cols):
    L=['\\begin{tabular}{l'+'r'*cols+'}','\\toprule',header,'\\midrule']+rows+['\\bottomrule','\\end{tabular}']
    (T/name).write_text('\n'.join(L)); return name

# A1 geocoding coverage --------------------------------------------------
con=pd.read_parquet(AN/'contracts_geocoded.parquet')
con['v']=pd.to_numeric(con.ValueThousandsDollars,errors='coerce').fillna(0)
fac=pd.read_parquet(AN/'facilities_geocoded.parquet'); fa=fac[fac.assignable]
rows=[]
for lab,df,w in [('War supply contracts',con,'v'),('War facilities (assignable)',fa,'pub_total')]:
    tot=df[w].sum()
    for stage in ['exact','alias','fuzzy']:
        s=df[df.match_stage==stage]
        rows.append(f'\\quad {stage.capitalize()} & {len(s):,} & {len(s)/len(df)*100:.1f} & '
                    f'{s[w].sum()/tot*100:.1f} \\\\')
    un=df[df.fips.isna()]
    rows.insert(len(rows)-3, f'\\multicolumn{{4}}{{l}}{{\\emph{{{lab}}} ($N={len(df):,}$)}} \\\\')
    rows.append(f'\\quad Unmatched & {len(un):,} & {len(un)/len(df)*100:.1f} & {un[w].sum()/tot*100:.1f} \\\\')
ng=fac[~fac.assignable]
rows.append(f'\\quad Source records no place & {len(ng):,} & --- & '
            f'{ng.pub_total.sum()/fac.pub_total.sum()*100:.1f} \\\\')
tab('tabA_geocoding.tex','Match stage & Records & \\% records & \\% dollars \\\\',rows,3)

# A2 pairwise geography ---------------------------------------------------
def mathify(s):
    for a,b in [('W_C','$W^C$'),('W_F','$W^F$'),('W_M','$W^M$'),(' D ',' $D$ ')]:
        s=s.replace(a,b)
    return s.replace(' x ',' $\\times$ ').strip()
rows=[f'{mathify(k)} & {v["A"]:.3f} & {v["JS"]:.3f} & {v["spearman"]:.3f} \\\\'
      for k,v in tg['pairwise'].items()]
tab('tabA_geography.tex','Pair & Overlap $\\mathcal{A}$ & JS (bits) & Spearman $\\rho$ \\\\',rows,3)

# A3 pre-trend falsification ---------------------------------------------
rows=[]
for r in rob['pretrends']:
    st=lambda k:('$^{***}$' if r['p'][k]<.01 else '$^{**}$' if r['p'][k]<.05 else '$^{*}$' if r['p'][k]<.1 else '')
    rows.append(f'{r["outcome"]} & '+' & '.join(f'{r["coef"][k]:.4f}{st(k)}' for k in ['W_C','W_F','W_M','B'])
                +f' & {r["n"]:,} \\\\')

tab('tabA_pretrends.tex','Placebo outcome & $W^C$ & $W^F$ & $W^M$ & $B$ & $N$ \\\\',rows,5)

# Equation (8)'s interactions. Section 4 named them and no table reported them.
irows=[]
for r in rob_int:
    ist=lambda v:('$^{***}$' if v<.01 else '$^{**}$' if v<.05 else '$^{*}$' if v<.1 else '')
    irows.append(f'{r["outcome"]} & {r["theta_C"]:.5f}{ist(r["p_C"])} & ({r["se_C"]:.5f}) & '
                f'{r["theta_F"]:.5f}{ist(r["p_F"])} & ({r["se_F"]:.5f}) & {r["n"]:,} \\\\')
tab('tabA_interactions.tex',
    'Outcome, 1970 & $\\theta_C$ & (SE) & $\\theta_F$ & (SE) & $N$ \\\\', irows, 5)

# A4 Conley --------------------------------------------------------------
rows=[]
for blk in rob['conley']:
    rows.append(f'\\multicolumn{{5}}{{l}}{{\\emph{{{blk["outcome"]}}}}} \\\\')
    for k in ['W_C','W_F','W_M','B']:
        c=blk[k]
        nm={'W_C':'$W^C$','W_F':'$W^F$','W_M':'$W^M$','B':'$B$'}[k]
        rows.append(f'\\quad {nm} & {c["coef"]:.4f} & '
                    f'{c["se_cluster"]:.4f} & {c["se_conley"]:.4f} & {c["t_conley"]:.2f} \\\\')
tab('tabA_conley.tex','Variable & Coefficient & Clustered SE & Conley SE & $t$ (Conley) \\\\',rows,4)

# A5 burden denominators + drop-top20 ------------------------------------
rows=[f'{r["denominator"]} & {r["coef"]:+.5f} & {r["p"]:.3f} & {r["n"]:,} \\\\' for r in rob['burden_alt']]
tab('tabA_burden.tex','Denominator for $B_i$ & Coefficient & $p$ & $N$ \\\\',rows,3)
rows=[]
for blk in rob['drop_top20']:
    rows.append(f'\\multicolumn{{3}}{{l}}{{\\emph{{{blk["outcome"]}}}}} \\\\')
    for k in ['W_C','W_F','W_M','B']:
        nm={'W_C':'$W^C$','W_F':'$W^F$','W_M':'$W^M$','B':'$B$'}[k]
        rows.append(f'\\quad {nm} & {blk[k]["full"]:.4f} & {blk[k]["drop20"]:.4f} \\\\')
tab('tabA_droptop.tex','Variable & Full sample & Excl.\\ top 20 \\\\',rows,2)

# A6 investment-type composition -----------------------------------------
d['has_plant']=d.fac_public_k>0; d['has_base']=d.cdb_fac_military>0
d['type']=np.where(d.has_plant&d.has_base,'Both',np.where(d.has_plant,'Plant only',
          np.where(d.has_base,'Base only','Neither')))
g=d.groupby('type').agg(n=('B','size'),burden=('B','median'),pop40=("pop1940","median"),
                        urb=('urbrate1940','median'),mfg40=('mfgshare1940','median'),
                        mfg70=('mfgshare1970','median'),inc70=('medfaminc1970','median'))
rows=[f'{i} & {r.n:,} & {r.burden:.2f} & {r.pop40:,.0f} & {r.urb:.3f} & {r.mfg40:.3f} & '
      f'{r.mfg70:.1f} & {r.inc70:,.0f} \\\\' for i,r in g.iterrows()]
tab('tabA_composition.tex',
    'County type & $N$ & Burden & Pop.\\ 1940 & Urban & Mfg.\\ 1940 & Mfg.\\ 1970 & Income 1970 \\\\',rows,7)

# A7 top-20 recipient counties -------------------------------------------
nm=d[['fips','name','contract_k','fac_public_k','cdb_fac_military','deaths_all','pop1940','B']].copy()
top=nm.nlargest(20,'contract_k')
rows=[f'{str(r["name"])[:26]} & {r.contract_k/1e3:,.0f} & {r.fac_public_k/1e3:,.0f} & '
      f'{r.cdb_fac_military/1e3:,.0f} & {int(r.deaths_all):,} & {r.B:.2f} \\\\'
      for _,r in top.iterrows()]
tab('tabA_top20.tex','County & Contracts (\\$m) & Plant (\\$m) & Military (\\$m) & Deaths & $B_i$ \\\\',rows,5)
print('appendix tables:', ', '.join(sorted(p.name for p in T.glob('tabA_*.tex'))))
