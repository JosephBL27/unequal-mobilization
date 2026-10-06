#!/usr/bin/env python3
"""
What did the wartime allocation function actually load on?

The overlap coefficient answers "did the two distributions occupy the same
space" and the answer is mostly a restatement of a fact already known: war
contracts were geographically concentrated and deaths were not. This script
decomposes that, and then reports the statistic that carries the paper's real
content.

Part 1 decomposes A(deaths, contracts) = 0.466 against two counterfactuals --
deaths exactly proportional to population, and contracts exactly proportional
to population -- to show how much of the misalignment is contract
concentration rather than anything about sacrifice.

Part 2 is the comparison the paper is actually making. On the same 3,073
counties, in the same units, it puts the rank correlation between each
allocation and fatal burden next to the rank correlation between that
allocation and the characteristics the procurement agencies were in fact
selecting on. If the allocation function loads 0.69 on prewar manufacturing
and 0.00 on human loss, that is a statement about what the war state was
optimising, and it does not depend on any identification assumption.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
d=pd.read_parquet(AN/'master_panel_v3.parquet')
P=d.pop1940.replace(0,np.nan)
res={}

# ---------------- Part 1: decomposing the overlap ------------------------
def A(x,y):
    x=np.nan_to_num(np.asarray(x,dtype=float)).clip(0)
    y=np.nan_to_num(np.asarray(y,dtype=float)).clip(0)
    return float(np.minimum(x/x.sum(), y/y.sum()).sum())

D=d.deaths_all.fillna(0); C=d.contract_k.fillna(0); POP=d.pop1940
D_prop=POP*D.sum()/POP.sum()          # deaths spread exactly in proportion to people
C_prop=POP*C.sum()/POP.sum()          # contracts spread exactly in proportion to people
obs, dp, cp = A(D,C), A(D_prop,C), A(D,C_prop)
both = A(D_prop, C_prop)          # both shifted: overlap is one by construction

print('='*78); print('PART 1  WHAT IS IN THE OVERLAP COEFFICIENT'); print('='*78)
print(f'  observed        A(deaths, contracts)            {obs:.4f}')
print(f'  counterfactual  deaths proportional to pop      {dp:.4f}')
print(f'  counterfactual  contracts proportional to pop   {cp:.4f}')
print(f'  counterfactual  both proportional to pop        {both:.4f}')
print(f'\n  total shortfall from perfect overlap           {1-obs:.4f}')
# One-at-a-time shifts are marginal effects, not a decomposition: they sum to
# 82.4% of the gap and leave an interaction term the text used to ignore. The
# Shapley value averages each factor's contribution over both orderings and is
# exactly additive, so the two pieces sum to the gap by construction.
sh_c = 0.5*((cp-obs) + (both-dp))     # contract concentration
sh_d = 0.5*((dp-obs) + (both-cp))     # deaths deviating from population
print(f'    one-at-a-time, contract concentration        {cp-obs:.4f}  '
      f'({100*(cp-obs)/(1-obs):.1f}% of it)')
print(f'    one-at-a-time, deaths deviating from pop     {dp-obs:.4f}  '
      f'({100*(dp-obs)/(1-obs):.1f}% of it)')
print(f'    unattributed interaction                     {(1-obs)-(cp-obs)-(dp-obs):.4f}  '
      f'({100*((1-obs)-(cp-obs)-(dp-obs))/(1-obs):.1f}% of it)')
print(f'    SHAPLEY, contract concentration              {sh_c:.4f}  '
      f'({100*sh_c/(1-obs):.1f}% of it)')
print(f'    SHAPLEY, deaths deviating from pop           {sh_d:.4f}  '
      f'({100*sh_d/(1-obs):.1f}% of it)')
assert abs(sh_c+sh_d-(1-obs))<1e-9, 'Shapley shares must sum to the gap'
res['overlap_decomposition']={'observed':round(obs,4),'deaths_prop_to_pop':round(dp,4),
    'contracts_prop_to_pop':round(cp,4),'both_prop_to_pop':round(both,4),
    'share_from_contract_concentration':round((cp-obs)/(1-obs),4),
    'share_from_death_deviation':round((dp-obs)/(1-obs),4),
    'interaction_share':round(((1-obs)-(cp-obs)-(dp-obs))/(1-obs),4),
    'shapley_contract_level':round(sh_c,4),
    'shapley_death_level':round(sh_d,4),
    'shapley_contract_share':round(sh_c/(1-obs),4),
    'shapley_death_share':round(sh_d/(1-obs),4)}

# a Poisson null: deaths drawn as if per-resident risk were uniform nationally
rng=np.random.default_rng(20260831)
# 2,000 draws is ample for the null mean but not for its s.d.: z moved from
# 35.7 to 37.1 across seeds, so the reported digits were a seed artifact.
draws=np.array([A(rng.poisson(D_prop).astype(float),C) for _ in range(20000)])
print(f'\n  Poisson null (uniform per-resident risk): A = {draws.mean():.4f} '
      f'(sd {draws.std():.4f}); observed sits {(draws.mean()-obs)/draws.std():.0f} s.d. below it.')
print('  The deviation is real but small: the headline number is dominated by')
print('  the concentration of contracts, which is not this paper\'s finding.')
res['poisson_null']={'mean':round(float(draws.mean()),4),'sd':round(float(draws.std()),4),
                     'z_of_observed':round(float((draws.mean()-obs)/draws.std()),1)}

# ---------------- Part 2: what the allocation loaded on ------------------
pc={'W_C':d.contract_k.fillna(0)/P, 'W_F':d.fac_public_k.fillna(0)/P,
    'W_M':d.cdb_fac_military.fillna(0)/P}
b_civic = 1000*d.deaths_all.fillna(0)/P
b_enl   = pd.to_numeric(d.B_A,errors='coerce').where(d.valid_BA.fillna(False))
X={'1940 manufacturing share':pd.to_numeric(d.mfgshare1940,errors='coerce'),
   '1940 urban share':        pd.to_numeric(d.urbrate1940,errors='coerce'),
   '1940 log population':     pd.to_numeric(d.logpop1940,errors='coerce'),
   'fatal burden, per resident': b_civic,
   'fatal burden, per enlistee': b_enl}

print('\n'+'='*78); print('PART 2  RANK CORRELATION OF EACH ALLOCATION (PER RESIDENT) WITH')
print('='*78)
hdr=f'{"":30s}' + ''.join(f'{k:>14s}' for k in pc)
print(hdr); print('-'*78)
rows={}
for lab,x in X.items():
    cells=[]
    rows[lab]={}
    for k,v in pc.items():
        ok=x.notna()&v.notna()
        r=float(spearmanr(x[ok],v[ok]).statistic)
        n=int(ok.sum()); se=1/np.sqrt(n-3)
        rows[lab][k]={'rho':round(r,4),'n':n,'ci':[round(r-1.96*se,3),round(r+1.96*se,3)]}
        cells.append(f'{r:>+14.3f}')
    print(f'{lab:30s}'+''.join(cells))
print('-'*78)
n=int((X['1940 log population'].notna()&pc['W_C'].notna()).sum())
print(f'  s.e. of a rank correlation at n={n:,} is {1/np.sqrt(n-3):.3f}; a true rho of 0.20')
print('  would be detected with near certainty. The zeros are precise, not underpowered.')
res['criteria']=rows

(AN/'allocation_criteria.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"allocation_criteria.json"}')

# ---------------- the exhibit -------------------------------------------
T=ROOT/'paper/tables'
L=['\\begin{tabular}{lccc}','\\toprule',
   '& Contracts $W^C$ & War plant $W^F$ & Military $W^M$ \\\\',
   '& (1) & (2) & (3) \\\\','\\midrule',
   '\\multicolumn{4}{l}{\\emph{Characteristics the procurement agencies selected on}} \\\\']
ORDER=[('1940 manufacturing share','\\quad 1940 manufacturing share'),
       ('1940 urban share','\\quad 1940 urban share'),
       ('1940 log population','\\quad 1940 log population'),
       (None,'\\multicolumn{4}{l}{\\emph{Military sacrifice}} \\\\'),
       ('fatal burden, per resident','\\quad Fatal burden, per resident'),
       ('fatal burden, per enlistee','\\quad Fatal burden, per enlistee')]
for key,lab in ORDER:
    if key is None: L.append(lab); continue
    L.append(f'{lab} & '+' & '.join(f'{rows[key][k]["rho"]:+.3f}' for k in ('W_C','W_F','W_M'))+' \\\\')
L+=['\\midrule',
    '$N$, first four rows & '+' & '.join(f'{rows["1940 log population"][k]["n"]:,}' for k in ('W_C','W_F','W_M'))+' \\\\',
    '$N$, per-enlistee row & '+' & '.join(f'{rows["fatal burden, per enlistee"][k]["n"]:,}' for k in ('W_C','W_F','W_M'))+' \\\\',
    '\\bottomrule','\\end{tabular}']
(T/'tab_criteria.tex').write_text('\n'.join(L))
print(f'-> {T/"tab_criteria.tex"}')
