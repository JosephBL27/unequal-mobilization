#!/usr/bin/env python3
"""Appendix exhibits for the shift-share instrument and the year-by-year allocation."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
T = ROOT / 'paper/tables'
R = json.loads((ROOT / 'data/analysis/shiftshare.json').read_text())

def w(name, header, rows, ncol, align='r'):
    (T / name).write_text('\n'.join(
        ['\\begin{tabular}{l' + align * ncol + '}', '\\toprule', header, '\\midrule']
        + rows + ['\\bottomrule', '\\end{tabular}']))

def star(p): return '$^{***}$' if p < .01 else '$^{**}$' if p < .05 else '$^{*}$' if p < .1 else ''

# --- relevance and exclusion, shift-share against the Munitions Board -------
PL = ['1940 mfg share', '1940 urban share', '1940 log population', '1930-40 pop growth']
rows = []
for r in R['shiftshare'] + [R['imp_benchmark']]:
    rows.append(r['instrument'].replace('&', '\\&') + ' & '
                + f'{r["F"]:.1f} & {r["partial_r2"]:.4f} & '
                + ' & '.join(f'{r["placebo"][p]:.3f}' + star(r['placebo'][p]) for p in PL)
                + ' \\\\')
w('tabA_shiftshare.tex',
  'Instrument & $F$ & Partial $R^2$ & Mfg.\\ share & Urban share & Log pop. & Pop.\\ growth \\\\',
  rows, 6)

# --- per class: where the weight sits, and why -----------------------------
GF = {g['class']: g for g in R['greenfield']}
NAME = {'aircraft': 'Aircraft', 'ammunition': 'Ammunition', 'ships': 'Ships',
        'firearms': 'Small arms and ordnance', 'electrical': 'Electrical and radio',
        'motorveh': 'Motor vehicles', 'textiles': 'Textiles and clothing',
        'machinetool': 'Machine tools and machinery', 'petroleum': 'Petroleum',
        'tanks': 'Tanks and combat vehicles', 'ironsteel': 'Iron and steel',
        'instruments': 'Instruments and optics', 'explosives': 'Explosives',
        'chemicals': 'Chemicals', 'lumber': 'Lumber and paper', 'rubber': 'Rubber',
        'leather': 'Leather and footwear', 'railroad': 'Railroad equipment',
        'nonferrous': 'Nonferrous metals', 'stoneclay': 'Stone, clay and glass',
        'food': 'Food'}
rows = []
for r in sorted(R['rotemberg'], key=lambda x: -x['national_bn']):
    k = r['class']; g = GF.get(k)
    if not g: continue
    # The dollars column is the geocoded base, which is the base the greenfield
    # share is computed on; the national total including unassigned records is
    # in the note. Mixing the two inside one row is what the project's own rule
    # against unnamed bases exists to prevent.
    dag = '$^{\\dagger}$' if g['basis'] == '1930 employment' else ''
    rows.append(f'{NAME.get(k,k)}{dag} & {g["bn"]:.1f} & {g["prewar_counties"]:,} & '
                f'{g["counties_receiving"]:,} & {100*g["greenfield_dollar_share"]:.1f} & '
                f'{r["partial_r2"]:.4f} \\\\')
w('tabA_ssclasses.tex',
  'Product class & \\$bn & Counties with & Counties & \\% of \\$ to & Partial $R^2$ \\\\\n'
  ' & & prewar capacity & receiving & a county with none & of this class alone \\\\',
  rows, 5)

# --- the allocation function, year by year ---------------------------------
Y = R['by_year']; yrs = Y['years']
hdr = 'Award year & ' + ' & '.join(str(y) for y in yrs) + ' \\\\'
rows = [
 'Dollars placed (\\$bn) & ' + ' & '.join(f'{v:.1f}' for v in Y['dollars_bn']) + ' \\\\',
 'Counties receiving (\\%) & ' + ' & '.join(f'{100*v:.1f}' for v in Y['coverage']) + ' \\\\',
 '\\addlinespace',
 '$\\rho$(1940 mfg.\\ share) & ' + ' & '.join(f'{v:.3f}' for v in Y['rho_mfg_fixed_sample']) + ' \\\\',
 '\\addlinespace',
 '$B_i$ per resident & ' + ' & '.join(
     f'{c:.5f}{star(p)}' for c, p in zip(Y['b_civic']['coef'], Y['b_civic']['p'])) + ' \\\\',
 '\\quad $p$ & ' + ' & '.join(f'{p:.3f}' for p in Y['b_civic']['p']) + ' \\\\',
 '$B_i^{A}$ per enlistee & ' + ' & '.join(
     f'{c:.5f}{star(p)}' for c, p in zip(Y['b_enlistee']['coef'], Y['b_enlistee']['p'])) + ' \\\\',
 '\\quad $p$ & ' + ' & '.join(f'{p:.3f}' for p in Y['b_enlistee']['p']) + ' \\\\',
]
w('tabA_byyear.tex', hdr, rows, len(yrs))
print('wrote tabA_shiftshare.tex, tabA_ssclasses.tex, tabA_byyear.tex')
