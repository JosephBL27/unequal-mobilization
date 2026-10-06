#!/usr/bin/env python3
"""LaTeX tables for the matched large-public-plant design."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; T=ROOT/'paper/tables'
m=json.loads((ROOT/'data/analysis/matched_results.json').read_text())
r=json.loads((ROOT/'data/analysis/matched_robustness.json').read_text())
def st(p): return '$^{***}$' if p<.01 else '$^{**}$' if p<.05 else '$^{*}$' if p<.1 else ''
def w(n,h,rows,k):
    (T/n).write_text('\n'.join(['\\begin{tabular}{l'+'r'*k+'}','\\toprule',h,'\\midrule']
                               +rows+['\\bottomrule','\\end{tabular}']))
NAME={'logpop1940':'Log population 1940','urbrate1940':'Urban share 1940',
      'blackshare1940':'Black population share 1940','mfgshare1940':'Manufacturing share 1940',
      'popgrowth_3040':'Log population growth 1930--40','PCTILL3':'Illiteracy rate 1930',
      'PCTFRM3':'Farm share 1930','LATITUDE':'Latitude','LONGITUD':'Longitude'}
w('tabA_balance.tex','Covariate & Raw SMD & Matched SMD \\\\',
  [f'{NAME.get(b["var"],b["var"])} & {b["smd_raw"]:.3f} & {b["smd_matched"]:.3f} \\\\' for b in m['balance']]
  +['\\midrule',f'Imbalanced ($|$SMD$|>0.10$) & {m["imbalanced_raw"]} of 9 & {m["imbalanced_matched"]} of 9 \\\\'],2)
w('tab_matched.tex','Outcome & Raw difference & Matched & (SE) & IPW & $N$ \\\\',
  [f'{e["outcome"]} & {e["raw"]:.4f} & {e["matched"]:.4f}{st(e["p"])} & ({e["se"]:.4f}) & '
   f'{e["ipw"]:.4f} & {e["n"]:,} \\\\' for e in m['effects']],5)
w('tabA_matchedplacebo.tex','Pre-treatment outcome & Coefficient & $p$ & $N$ \\\\',
  [f'{p["outcome"]} & {p["coef"]:.4f}{st(p["p"])} & {p["p"]:.3f} & {p["n"]:,} \\\\' for p in m['placebo']],3)
KEYS=['log pop 1970','mfg share 1970','log income 1970','homeownership 1970']
rows=['\\multicolumn{5}{l}{\\emph{Matching parameters}} \\\\']
for s in r['params']:
    rows.append('\\quad '+s['spec'].replace('%','\\%')+' & '+' & '.join(
        f'{s[k]["coef"]:.3f}' if k in s else '---' for k in KEYS)+' \\\\')
rows.append('\\multicolumn{5}{l}{\\emph{Sample restrictions}} \\\\')
for s in r['samples']:
    rows.append('\\quad '+s['spec']+' & '+' & '.join(
        f'{s[k]["coef"]:.3f}' if k in s else '---' for k in KEYS)+' \\\\')
if 'adjacency' in r:
    a=r['adjacency']
    rows.append('\\multicolumn{5}{l}{\\emph{Treated against their own untreated neighbors}} \\\\')
    rows.append('\\quad Coefficient & '+' & '.join(
        f'{a[k]["coef"]:.3f}{st(a[k]["p"])}' if k in a else '---' for k in KEYS)+' \\\\')
    rows.append('\\quad $p$-value & '+' & '.join(
        f'{a[k]["p"]:.3f}' if k in a else '---' for k in KEYS)+' \\\\')
w('tabA_matchedrobust.tex',
  'Specification & Log pop.\\ 1970 & Mfg.\\ share 1970 & Log income 1970 & Own rate 1970 \\\\',rows,4)
print('wrote tab_matched.tex, tabA_balance.tex, tabA_matchedplacebo.tex, tabA_matchedrobust.tex')

# --- military design ---
mm=json.loads((ROOT/'data/analysis/matched_military.json').read_text())
mp=json.loads((ROOT/'data/analysis/matched_results.json').read_text())
pe={e['outcome']:e for e in mp['effects']}
me={e['outcome']:e for e in mm['effects']}
# Ordered so the table answers its own question: both treatments grew the
# county, only one of them grew manufacturing, and the share row is therefore
# a statement about the denominator as much as the numerator.
KEY=['log population 1970','log total employment 1970','log manufacturing employment 1970',
     'manufacturing share 1970','log family income 1970','homeownership 1970']
rows=[]
for k in KEY:
    a,b=pe.get(k),me.get(k)
    if k=='manufacturing share 1970': rows.append('\\addlinespace')
    rows.append(f'{k.capitalize()} & '
        +(f'{a["matched"]:.4f}{st(a["p"])} & ({a["se"]:.4f}) & ' if a else '--- & --- & ')
        +(f'{b["coef"]:.4f}{st(b["p"])} & ({b["se"]:.4f}) \\\\' if b else '--- & --- \\\\'))
rows.append('\\midrule')
rows.append(f'Treated counties & {mp["setup"]["n_matched_treated"]} & & {mm["n_treated"]} & \\\\')
rows.append(f'Covariates imbalanced & {mp["imbalanced_matched"]} of 9 & & '
            f'{sum(1 for x in mm["balance"] if abs(x["matched"])>.1)} of 9 & \\\\')
w('tab_twotreatments.tex',
  '& \\multicolumn{2}{c}{Large public plant} & \\multicolumn{2}{c}{Military installation} \\\\\n'
  '\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\nOutcome, 1970 & Effect & (SE) & Effect & (SE) \\\\',rows,4)
rows=[f'{p["outcome"]} & {p["coef"]:.4f}{st(p["p"])} & {p["p"]:.3f} \\\\' for p in mm['placebo']]
w('tabA_milplacebo.tex','Pre-treatment outcome & Coefficient & $p$ \\\\',rows,2)
print('wrote tab_twotreatments.tex, tabA_milplacebo.tex')

# --- military threshold sensitivity and randomization inference ------------
# This exhibit had no producer for a month: tabA_milrobust.tex was carried in
# the repository as a hand-edited file, so re-running the pipeline could not
# correct it and it drifted from audit_military.json by as much as 0.63 points
# on the ownership row. It is generated here so the table and the prose read
# the same artifact.
am=json.loads((ROOT/'data/analysis/audit_military.json').read_text())
OUTK=[('log pop','Log pop.\\ 1970'),('mfg share','Mfg.\\ share 1970'),('own rate','Own rate 1970')]
rows=[]
def _cells(o): return ' & '.join(f'{o[k]["coef"]:.3f}{st(o[k]["p"])}' if k in o else '---'
                                 for k,_ in OUTK)
for t in am['thresholds']:
    rows.append(f'{t["spec"].replace("%","\\%").replace("$","\\$")} & {t["n_treated"]} & {_cells(t)} \\\\')
a=am['absolute']
rows.append(f'Military spending $\\geq$ \\$10M (absolute) & {a["n_treated"]} & {_cells(a)} \\\\')
rows.append('\\midrule')
rows.append('\\multicolumn{5}{l}{\\emph{Randomization inference, 500 permutations of treatment}} \\\\')
LAB={'log pop':'log pop','mfg share':'mfg share','own rate':'own rate'}
for p in am['randomization']:
    rows.append(f'\\quad {LAB[p["outcome"]]}: observed {p["observed"]:.3f} & & '
                f'\\multicolumn{{3}}{{l}}{{permutation $p$ = {p["perm_p"]:.3f}, '
                f'null s.d.\\ {p["null_sd"]:.3f}}} \\\\')
w('tabA_milrobust.tex',
  'Treatment definition & Treated & '+' & '.join(l for _,l in OUTK)+' \\\\',rows,4)
print('wrote tabA_milrobust.tex')


# --- Oster (2019) sensitivity bounds ---------------------------------------
ob=json.loads((ROOT/'data/analysis/oster_bounds.json').read_text())
rows=[]
for grp,lab in [('plant','\\emph{Large public plant}'),('military','\\emph{Top-decile military installation}')]:
    rows.append(f'\\multicolumn{{7}}{{l}}{{{lab}}} \\\\')
    for r in ob[grp]:
        d13='---' if r['delta_13'] is None else f"{r['delta_13']:.2f}"
        d1 ='---' if r['delta_1']  is None else f"{r['delta_1']:.2f}"
        bm ='---' if r.get('beta_matched') is None else f"{r['beta_matched']:.4f}"
        rows.append(f"\\quad {r['outcome']} & {r['beta_uncontrolled']:.4f} & "
                    f"{r['beta_controlled']:.4f} & {bm} & {r['r2_controlled']:.3f} & {d13} & {d1} \\\\")
w('tabA_oster.tex',
  'Outcome & $\\beta$, short & $\\beta$, long & $\\beta$, matched & $R^2$ & $\\delta$ at $1.3R^2$ & $\\delta$ at $R^2=1$ \\\\',
  rows,6)
print('wrote tabA_oster.tex')
