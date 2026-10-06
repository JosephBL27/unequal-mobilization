#!/usr/bin/env python3
"""
How much selection on unobservables would overturn each matched estimate?

Section 5 claims causal identification on three plant outcomes and four military
ones, on the strength of propensity matching plus pre-treatment placebos. Section
5.9 then argues at length that prewar industrial capacity reaches 1970 outcomes by
routes that do not pass through wartime production. Those two arguments sit
uneasily together unless the paper says how much unobserved selection it would
take to remove each effect.

\\citet{oster2019} gives the statistic. Comparing the treatment coefficient and
$R^2$ from a SHORT regression with no controls ($\\beta_0$, $R_0$) and a LONG one
with the full prewar vector ($\\beta_1$, $R_1$), and positing a maximum attainable
$R^2$,

    delta = [beta_1 / (beta_0 - beta_1)] * [(R_1 - R_0) / (Rmax - R_1)]

is the ratio of selection on unobservables to selection on observables that would
drive the effect to zero. delta = 1 means unobservables would have to matter
exactly as much as the prewar vector already in the model; conventional practice
treats |delta| > 1 as robust. Rmax follows Oster's own suggestion of 1.3 R_1,
capped at one, and a stricter Rmax = 1 is reported beside it.

SPECIFICATION -- and why an earlier version of this script was wrong.

Oster's delta measures how far the coefficient travels when the observed controls
are added. That movement is the whole statistic. An earlier version of this file
estimated BOTH regressions on the matched sample using the matching weights, which
destroys it: matching has already removed selection on observables, so beta_0 and
beta_1 differ only by residual imbalance. For plant log population that left a gap
of -0.011 on a coefficient of 0.209, and delta came back as -99.9 -- a near-zero
denominator, not a robustness result. Every delta the old table printed was an
artifact of dividing by noise.

Both regressions are therefore run on the full estimation frame, unweighted, with
no matching. beta_1 is the OLS analogue of the matched estimate rather than the
matched estimate itself; both are reported so the reader can see how close they
are. The frame, the treatment indicators and the control vector X0 are identical
to those the propensity score is built from, so the observables Oster conditions
on are exactly the observables the matching balances.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parent.parent; AN = ROOT / 'data/analysis'

CTRL = ['logpop1940', 'urbrate1940', 'blackshare1940', 'mfgshare1940',
        'popgrowth_3040', 'PCTILL3', 'PCTFRM3', 'LATITUDE', 'LONGITUD']
X0 = CTRL + ['sq_logpop1940', 'sq_urbrate1940', 'sq_mfgshare1940',
             'sq_blackshare1940', 'mfg_suppressed']


def delta(df, y, tcol, Rmax_mult=1.3):
    """Short-vs-long on the full frame, unweighted. See the module docstring."""
    q = df[[y, tcol] + X0].replace([np.inf, -np.inf], np.nan).dropna()
    if len(q) < 40: return None
    r0 = sm.OLS(q[y], sm.add_constant(q[[tcol]].astype(float))).fit()
    r1 = sm.OLS(q[y], sm.add_constant(q[[tcol] + X0].astype(float))).fit()
    b0, b1 = float(r0.params[tcol]), float(r1.params[tcol])
    R0, R1 = float(r0.rsquared), float(r1.rsquared)
    out = {'beta_uncontrolled': round(b0, 5), 'beta_controlled': round(b1, 5),
           'r2_uncontrolled': round(R0, 4), 'r2_controlled': round(R1, 4), 'n': int(len(q))}
    for tag, Rmax in [('delta_13', min(Rmax_mult * R1, 1.0)), ('delta_1', 1.0)]:
        den = (b0 - b1) * (Rmax - R1)
        out[tag] = round(float(b1 * (R1 - R0) / den), 3) if abs(den) > 1e-12 else None
    out['rmax_13'] = round(min(Rmax_mult * R1, 1.0), 4)
    return out


def add_outcomes(d):
    d = d.copy()
    d['_li70'] = np.log(pd.to_numeric(d.medfaminc1970, errors='coerce').replace(0, np.nan))
    d['_lmfgemp70'] = np.log((pd.to_numeric(d.mfgshare1970, errors='coerce') / 100
                              * pd.to_numeric(d.emp1970, errors='coerce')).replace(0, np.nan))
    return d


def matched_betas(path):
    """The matched estimate for each outcome, for side-by-side comparison."""
    e = json.loads((AN / path).read_text())['effects']
    return {r['outcome']: (r['matched'] if 'matched' in r else r['coef']) for r in e}


res = {}
raw = add_outcomes(pd.read_parquet(AN / 'matched_sample_raw.parquet'))

HEAD = (f'{"outcome":34s}{"b(short)":>11s}{"b(long)":>10s}{"b(matched)":>12s}'
        f'{"R2":>7s}{"delta(1.3R)":>13s}{"delta(R=1)":>12s}')


def run(frame, tcol, outcomes, mbet, title, key):
    print('=' * 99); print(title); print('=' * 99); print(HEAD)
    res[key] = []
    for y, lab in outcomes:
        d = delta(frame, y, tcol)
        if not d: continue
        d['outcome'] = lab
        d['beta_matched'] = round(float(mbet[lab]), 5) if lab in mbet else None
        res[key].append(d)
        bm = f'{d["beta_matched"]:>12.4f}' if d['beta_matched'] is not None else f'{"---":>12s}'
        print(f'{lab:34s}{d["beta_uncontrolled"]:>11.4f}{d["beta_controlled"]:>10.4f}{bm}'
              f'{d["r2_controlled"]:>7.3f}{d["delta_13"]:>13.2f}{d["delta_1"]:>12.2f}')
    print()


PLANT = [('logpop1970', 'log population 1970'), ('mfgshare1970', 'manufacturing share 1970'),
         ('_li70', 'log family income 1970'), ('ownrate1970', 'homeownership 1970'),
         ('_lmfgemp70', 'log manufacturing employment 1970')]
run(raw, 'treat', PLANT, matched_betas('matched_results.json'),
    'OSTER DELTA -- LARGE PUBLIC PLANT (full frame, unweighted)', 'plant')

# Military treatment, defined exactly as in matched_military.py.
b = raw.copy()
b['mil_pc'] = pd.to_numeric(b.cdb_fac_military, errors='coerce').fillna(0) / b.pop1940.replace(0, np.nan)
cut = b.loc[b.mil_pc > 0, 'mil_pc'].quantile(0.90)
b['treat_mil'] = ((b.mil_pc >= cut) & (b.mil_pc > 0)).astype(int)
mil = b[~((b.treat == 1) & (b.treat_mil == 1))].copy()

MIL = [('logpop1970', 'log population 1970'), ('mfgshare1970', 'manufacturing share 1970'),
       ('_li70', 'log family income 1970'), ('ownrate1970', 'homeownership 1970')]
run(mil, 'treat_mil', MIL, matched_betas('matched_military.json'),
    'OSTER DELTA -- TOP-DECILE MILITARY INSTALLATION (full frame, unweighted)', 'military')

(AN / 'oster_bounds.json').write_text(json.dumps(res, indent=2))
print(f'-> {AN/"oster_bounds.json"}')
