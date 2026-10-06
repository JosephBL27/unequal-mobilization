#!/usr/bin/env python3
"""LaTeX tables for the instrumental-variables section."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; T=ROOT/'paper/tables'
iv=json.loads((ROOT/'data/analysis/iv_results.json').read_text())
sg=json.loads((ROOT/'data/analysis/iv_single_results.json').read_text())
vl=json.loads((ROOT/'data/analysis/iv_validity.json').read_text())

def st(p): return '$^{***}$' if p<.01 else '$^{**}$' if p<.05 else '$^{*}$' if p<.1 else ''
def w(name,head,rows,ncol):
    (T/name).write_text('\n'.join(['\\begin{tabular}{l'+'r'*ncol+'}','\\toprule',head,
                                   '\\midrule']+rows+['\\bottomrule','\\end{tabular}']))

# A. first stage
rows=[f'{r["spec"]} & {r["F"]:.1f} & {r["n"]:,} & {r["verdict"]} \\\\' for r in iv['first_stage']]
w('tabA_firststage.tex','Specification & $F$ & $N$ & Verdict \\\\',rows,3)

# B. single-endogenous IV vs OLS
rows=[]; cur=None
for r in sg:
    if r['spec']!=cur:
        cur=r['spec']
        rows.append(f'\\multicolumn{{6}}{{l}}{{\\emph{{{cur}}}}} \\\\')
    rows.append(f'\\quad {r["outcome"]} & {r["ols"]:.4f} & {r["iv"]:.4f}{st(r["iv_p"])} & '
                f'({r["iv_se"]:.4f}) & {r["partial_r2"]:.4f} & {r["F"]:.1f} \\\\')
w('tabA_iv.tex','Outcome & OLS & IV & (SE) & Partial $R^2$ & $F$ \\\\',rows,5)

# C. exclusion-restriction placebo
rows=[f'{r["outcome"]} & {r["imp_coef"]:.4f}{st(r["imp_p"])} & {r["imp_p"]:.3f} & '
      f'{r["mil_coef"]:.4f}{st(r["mil_p"])} & {r["mil_p"]:.3f} \\\\' for r in vl['placebo']]
w('tabA_ivplacebo.tex',
  'Pre-war outcome & IMP industrial & $p$ & Prewar bases & $p$ \\\\',rows,4)
print('wrote:', ', '.join(sorted(p.name for p in T.glob('tabA_iv*.tex')+list(T.glob('tabA_firststage*.tex')))
                          if False else ['tabA_firststage.tex','tabA_iv.tex','tabA_ivplacebo.tex']))

# ---- IMP specification sweep -------------------------------------------
sp=json.loads((ROOT/'data/analysis/imp_specifications.json').read_text())
L=['1940 manufacturing share','1940 urban share','1940 log population',
   '1930--40 population growth']
ENDOG={'W_C':'$W^{C}$','W_F':'$W^{F}$','W_M':'$W^{M}$'}
def pstar(p): return f'{p:.3f}'+('$^{***}$' if p<.01 else '$^{**}$' if p<.05 else '$^{*}$' if p<.1 else '')
rows=[]
for r in sp['specifications']:
    rows.append(f"{r['instrument']} & {ENDOG[r['endogenous']]} & {r['F']:.1f} & "
                f"{r['partial_r2']:.3f} & " + ' & '.join(pstar(r['placebo'][l]) for l in L) + r' \\')
(T/'tabA_impspecs.tex').write_text(
 '\\begin{tabular}{lcrrcccc}\n\\toprule\n'
 '& & \\multicolumn{2}{c}{Relevance} & \\multicolumn{4}{c}{Placebo $p$: instrument against a pre-war outcome} \\\\\n'
 '\\cmidrule(lr){3-4}\\cmidrule(lr){5-8}\n'
 'Construction of the instrument & Endog. & $F$ & Partial $R^2$ & Mfg.\\ share & Urban share & Log pop. & Pop.\\ growth \\\\\n'
 '\\midrule\n'+'\n'.join(rows)+'\n\\bottomrule\n\\end{tabular}\n')
print('wrote tabA_impspecs.tex')
