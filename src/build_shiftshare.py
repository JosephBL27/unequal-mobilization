#!/usr/bin/env python3
"""
A shift-share instrument for wartime procurement, and the test of whether it
survives the bar Section 5 set for the 1938 Industrial Mobilization Plan.

The logic. National war demand for aircraft, ships, ordnance and cloth was set
by the strategic course of the war, not by any American county. A county that
happened in 1940 to hold aircraft plants rather than furniture works was
therefore exposed to a much larger national shock, and that exposure is
predetermined. Formally, with s_ik the county's share of the national 1940 stock
of industry k and g_k national contract dollars placed in product class k,

    Chat_i = sum_k s_ik * g_k,          Z_i = arsinh(1000 * Chat_i / P_i,1940).

Two leave-out variants are built, because g_k contains county i's own contracts:
one that removes the county, one that removes its entire state.

What makes this different from the IMP instrument is the identifying variation.
IMP measures how much prewar capacity a county had, which is the confounder
itself. This measures which industries that capacity was in, holding the level
of prewar manufacturing fixed in the control set. Whether the Navy needed more
destroyers than the Quartermaster needed shoes was decided in the Pacific.

Whether that survives the exclusion test is an empirical question and this
script answers it against the paper's stated criteria: F >= 10, partial R^2
>= 0.05 after the prewar controls and state effects, and no pre-war placebo
rejecting at five percent.

Part B is separate and descriptive: the contract file carries month-resolution
award dates for all 190,693 records, so the allocation function can be
re-estimated year by year. If the war state ever began to respond to sacrifice,
or ever stopped responding to prewar industrial capacity, it shows up there.
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat, statsmodels.api as sm
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_products import classify_series
warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parent.parent
AN = ROOT / 'data/analysis'
res = {}

# ---------------------------------------------------------------- shocks ----
raw = pd.read_stata(ROOT / 'data/raw/contracts/WWII_contracts_clean.dta',
                    convert_categoricals=False)
raw['v'] = pd.to_numeric(raw.ValueThousandsDollars, errors='coerce').fillna(0)
raw['pclass'] = classify_series(raw.Product)
raw['award_year'] = pd.to_numeric(raw.award_year, errors='coerce')

# county assignment comes from the committed geocoder, not re-derived here
geo = pd.read_parquet(AN / 'contracts_geocoded.parquet')
assert len(geo) == len(raw), f'geocoded {len(geo)} vs raw {len(raw)}'
raw['fips'] = pd.to_numeric(geo.fips.values, errors='coerce')
# Fold independent cities into their parent county before anything downstream.
# Without this the fourteen cities' $6.82bn never lands in a panel county and the
# year-by-year exhibit silently runs on 1,481 counties instead of 1,490.
_IC = pd.read_csv(ROOT / 'data/raw/crosswalks/independent_city_merge.csv')
_ICM = dict(zip(_IC.city_fips.astype(int), _IC.parent_fips.astype(int)))
raw['fips'] = raw.fips.map(lambda f: _ICM.get(int(f), int(f)) if pd.notna(f) else f)

# Classes with no prewar counterpart are dropped from the instrument. They are
# not dropped from the paper's treatment, which is total contract dollars.
XWALK = {
 'aircraft':    ['manuair40'],
 'ships':       ['manuship40'],
 'railroad':    ['manuloco40', 'manurailsh40', 'manuraile40', 'manurailst40'],
 'tanks':       ['manucar40', 'manuloco40'],
 'motorveh':    ['manucar40', 'manubod40', 'manuveh40', 'manucyc40', 'manutrans40'],
 'ammunition':  ['manuammun40', 'manufirew40'],
 'explosives':  ['manuexp40'],
 'firearms':    ['manufirea40'],
 'petroleum':   ['manupetro40', 'manugre40', 'manuref40'],
 'chemicals':   ['manuchem40'],
 'rubber':      ['manurub40'],
 'leather':     ['manulea40'],
 'textiles':    ['manutext40'],
 'lumber':      ['manufor40', 'manucask40'],
 'ironsteel':   ['manuiron40'],
 'nonferrous':  ['manunonf40', 'manualum40'],
 'stoneclay':   ['manustone40'],
 'instruments': ['manuinst40'],
 'electrical':  ['oelectm', 'oelectf'],
 'machinetool': ['oirnstlm', 'oirnstlf'],
 'food':        ['ofoodm', 'ofoodf'],
}
PREVARS = sorted({v for vs in XWALK.values() for v in vs})
# The archive carries 1940 establishment counts for the war-specific industries
# and nothing for machinery, electrical equipment or food, so those three fall
# back to 1930 occupational employment. The substitution is recorded here so the
# exhibit and its note can say which basis each class uses, and so the reuse of
# iron and steel -- manuiron40 for `ironsteel`, 1930 iron-and-steel employment
# for `machinetool` -- is visible rather than implicit.
BASIS = {k: ('1930 employment' if any(v.startswith('o') for v in vs)
             else '1940 establishments') for k, vs in XWALK.items()}

# ------------------------------------------------ prewar county capacity ----
d, _ = pyreadstat.read_dta(str(ROOT / 'data/raw/jaworski_imp/data-controls-raw.dta'),
                           usecols=['state', 'ndmtcode'] + PREVARS)
xw, _ = pyreadstat.read_dta(str(ROOT / 'data/raw/garin_rothbaum/Data/RawData/'
                                      'crosswalk_statefip_stateicp_1910.dta'))
d = d.merge(xw, left_on='state', right_on='stateicp', how='left')
d['fips'] = d.statefip * 1000 + (pd.to_numeric(d.ndmtcode, errors='coerce') / 10).round()
d = d[d.fips.notna()].copy(); d['fips'] = d.fips.astype(int)
IC = pd.read_csv(ROOT / 'data/raw/crosswalks/independent_city_merge.csv')
ICM = dict(zip(IC.city_fips.astype(int), IC.parent_fips.astype(int)))
d['fips'] = d.fips.map(lambda f: ICM.get(f, f))
for c in PREVARS: d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0.0)
cap = d.groupby('fips', as_index=False)[PREVARS].sum()

# capacity by product class, then county shares of the national stock
for k, vs in XWALK.items():
    cap['cap_' + k] = cap[vs].sum(axis=1)
CAPC = ['cap_' + k for k in XWALK]
share = cap[['fips']].copy()
for k in XWALK:
    tot = cap['cap_' + k].sum()
    share['s_' + k] = cap['cap_' + k] / tot if tot > 0 else 0.0

panel = pd.read_parquet(AN / 'master_panel_iv.parquet')
share = share[share.fips.isin(set(panel.fips))].copy()
print(f'prewar capacity matched to {len(share):,} of {len(panel):,} panel counties')
res['n_capacity_counties'] = int(len(share))

# classifier coverage, so the footnote's three numbers have a producer
_unc = raw[raw.pclass == 'unclassified']
res['classifier'] = {
    'distinct_strings': int(raw.Product.nunique()),
    'dollar_share': round(float(1 - _unc.v.sum() / raw.v.sum()), 4),
    'record_share': round(float(1 - len(_unc) / len(raw)), 4),
    'residual_strings': int(_unc.Product.nunique()),
    'largest_residual_m': round(float(_unc.groupby('Product').v.sum().max()) / 1e3, 1),
    'n_classes': len(XWALK),
}

# ------------------------------------------------------------- the shift ----
nat = raw.groupby('pclass').v.sum()
own = (raw[raw.fips.notna()].groupby(['fips', 'pclass']).v.sum()
          .unstack(fill_value=0.0).reindex(columns=list(XWALK), fill_value=0.0))
raw['stfips'] = (raw.fips // 1000)
ownst = (raw[raw.fips.notna()].groupby(['stfips', 'pclass']).v.sum()
            .unstack(fill_value=0.0).reindex(columns=list(XWALK), fill_value=0.0))

print(f'\n{"class":13s}{"national $bn":>14s}{"prewar counties>0":>19s}{"top-county share":>18s}')
res['classes'] = []
for k in XWALK:
    s = share['s_' + k]
    print(f'{k:13s}{nat.get(k,0)/1e6:14.2f}{int((s>0).sum()):>19,}{s.max():18.3f}')
    res['classes'].append({'class': k, 'basis': BASIS[k],
                           'national_bn': round(float(nat.get(k, 0)) / 1e6, 3),
                           'counties_with_capacity': int((s > 0).sum()),
                           'max_county_share': round(float(s.max()), 4)})

S = share.set_index('fips')
def predict(leave):
    """leave: 'none', 'county', or 'state'."""
    out = pd.Series(0.0, index=S.index)
    for k in XWALK:
        g = float(nat.get(k, 0.0))
        if leave == 'none':
            gk = pd.Series(g, index=S.index)
        elif leave == 'county':
            gk = g - own[k].reindex(S.index).fillna(0.0)
        else:
            gk = g - ownst[k].reindex(S.index // 1000).fillna(0.0).values
        out = out + S['s_' + k].values * np.asarray(gk)
    return out

Z = pd.DataFrame({'fips': S.index})
for lv, nm in [('none', 'ss_all'), ('county', 'ss_loo'), ('state', 'ss_loostate')]:
    Z[nm] = predict(lv).values

m = panel.merge(Z, on='fips', how='left')
P = m.pop1940.replace(0, np.nan)
for nm in ['ss_all', 'ss_loo', 'ss_loostate']:
    m[nm] = m[nm].fillna(0.0)
    m['Z_' + nm] = np.arcsinh(1000 * m[nm] / P)
m['statefip'] = (m.fips // 1000).astype(int)

# ------------------------------------------- relevance and exclusion --------
CTRL = ['logpop1940', 'urbrate1940', 'blackshare1940', 'mfgshare1940',
        'popgrowth_3040', 'PCTILL3', 'PCTFRM3', 'mfg_suppressed', 'prewar_imputed']
for c in CTRL: m[c] = pd.to_numeric(m[c], errors='coerce')
m['mfg_suppressed'] = m['mfg_suppressed'].fillna(0.0)
m['prewar_imputed'] = m['prewar_imputed'].fillna(0.0)

def absorb(df, cols):
    """Residualise on the prewar vector and state effects."""
    D = pd.get_dummies(df.statefip, prefix='s', drop_first=True).astype(float)
    X = sm.add_constant(pd.concat([df[CTRL].astype(float), D], axis=1))
    return {c: sm.OLS(df[c].astype(float), X).fit().resid for c in cols}

PLAC = [('mfgshare1940', '1940 mfg share'), ('urbrate1940', '1940 urban share'),
        ('logpop1940', '1940 log population'), ('popgrowth_3040', '1930-40 pop growth')]

def evaluate(zcol, label):
    q = m[[zcol, 'W_C', 'statefip'] + CTRL].replace([np.inf, -np.inf], np.nan).dropna()
    r = absorb(q, [zcol, 'W_C'])
    zr, wr = r[zcol], r['W_C']
    fs = sm.OLS(wr, sm.add_constant(zr)).fit(cov_type='cluster',
                                             cov_kwds={'groups': q.statefip})
    F = float(fs.tvalues.iloc[1] ** 2)
    pr2 = float(sm.OLS(wr, sm.add_constant(zr)).fit().rsquared)
    row = {'instrument': label, 'F': round(F, 1), 'partial_r2': round(pr2, 4),
           'n': int(len(q)), 'placebo': {}}
    for y, lab in PLAC:
        # y is itself in CTRL; selecting both duplicates the column
        C2 = [c for c in CTRL if c != y]
        qq = m[[zcol, y, 'statefip'] + C2].replace([np.inf, -np.inf], np.nan).dropna()
        D = pd.get_dummies(qq.statefip, prefix='s', drop_first=True).astype(float)
        X = sm.add_constant(pd.concat([qq[[zcol] + C2].astype(float), D], axis=1))
        rr = sm.OLS(qq[y].astype(float), X).fit(cov_type='cluster',
                                                cov_kwds={'groups': qq.statefip})
        row['placebo'][lab] = round(float(rr.pvalues[zcol]), 4)
    row['usable'] = bool(F >= 10 and pr2 >= 0.05 and
                         all(p >= 0.05 for p in row['placebo'].values()))
    return row

print('\n' + '=' * 92)
print('A. DOES THE SHIFT-SHARE CLEAR THE BAR SECTION 5 SET FOR THE 1938 PLAN?')
print('=' * 92)
hdr = f'{"instrument":34s}{"F":>8s}{"part.R2":>9s}' + ''.join(f'{l[:11]:>13s}' for _, l in PLAC) + f'{"usable":>8s}'
print(hdr); print('-' * len(hdr))
res['shiftshare'] = []
for zc, lab in [('Z_ss_all', 'shift-share, all counties'),
                ('Z_ss_loo', 'shift-share, county left out'),
                ('Z_ss_loostate', 'shift-share, state left out')]:
    row = evaluate(zc, lab); res['shiftshare'].append(row)
    print(f'{lab:34s}{row["F"]:8.1f}{row["partial_r2"]:9.4f}'
          + ''.join(f'{row["placebo"][l]:13.3f}' for _, l in PLAC)
          + f'{"YES" if row["usable"] else "no":>8s}')
# Section 5.9 quotes a fourth specification -- the shift-share conditioned in
# addition on the total prewar stock of war-related establishments -- and until
# now no committed script produced it. It is the -7.69 class: a load-bearing
# number that reproduces but is stored nowhere, so nothing could catch it drifting.
_EST = [v for v in PREVARS if not v.startswith('o')]     # 1940 establishment counts only
_stock = cap.set_index('fips')[_EST].sum(axis=1)
m['warstock'] = np.arcsinh(m.fips.map(_stock).fillna(0.0))
CTRL.append('warstock')
_cond = evaluate('Z_ss_all', 'shift-share, conditioned on prewar war-industry stock')
CTRL.remove('warstock')
res['shiftshare_conditioned'] = _cond
print(f'{_cond["instrument"]:34s}{_cond["F"]:8.1f}{_cond["partial_r2"]:9.4f}'
      + ''.join(f'{_cond["placebo"][l]:13.3f}' for _, l in PLAC)
      + f'{"YES" if _cond["usable"] else "no":>8s}')

# the incumbent, for comparison, on the identical sample and criteria
m['Z_imp'] = np.arcsinh(pd.to_numeric(m.imp_fac, errors='coerce').fillna(0))
row = evaluate('Z_imp', 'IMP allocated facilities'); res['imp_benchmark'] = row
print(f'{row["instrument"]:34s}{row["F"]:8.1f}{row["partial_r2"]:9.4f}'
      + ''.join(f'{row["placebo"][l]:13.3f}' for _, l in PLAC)
      + f'{"YES" if row["usable"] else "no":>8s}')

# ---------------------- B. which classes identify: Rotemberg decomposition --
# A shift-share is a weighted sum of just-identified share instruments, so the
# exclusion restriction is an assumption about the shares, not about the
# instrument as a whole. Running each class on its own says which shares the
# identification is actually resting on.
print('\n' + '=' * 92)
print('B. WHICH PREWAR INDUSTRY IS THE INSTRUMENT ACTUALLY USING?')
print('=' * 92)
rot = []
for k in XWALK:
    capk = cap.set_index('fips')['cap_' + k].reindex(m.fips).fillna(0.0).values
    tot = float(cap['cap_' + k].sum())
    if tot <= 0: continue
    m['_z'] = np.arcsinh(1000 * (capk / tot) * float(nat.get(k, 0.0)) / P)
    q = m[['_z', 'W_C', 'statefip'] + CTRL].replace([np.inf, -np.inf], np.nan).dropna()
    r = absorb(q, ['_z', 'W_C'])
    fs = sm.OLS(r['W_C'], sm.add_constant(r['_z'])).fit()
    rot.append({'class': k, 'national_bn': round(float(nat.get(k, 0.0)) / 1e6, 2),
                'partial_r2': round(float(fs.rsquared), 4),
                'first_stage_b': round(float(fs.params.iloc[1]), 4),
                'F': round(float(fs.tvalues.iloc[1]) ** 2, 1)})
rot.sort(key=lambda r: -r['partial_r2'])
res['rotemberg'] = rot
print(f'{"class":13s}{"$bn":>9s}{"partial R2":>12s}{"1st-stage b":>13s}{"F":>8s}')
for r in rot:
    print(f'{r["class"]:13s}{r["national_bn"]:9.2f}{r["partial_r2"]:12.4f}'
          f'{r["first_stage_b"]:13.4f}{r["F"]:8.1f}')

# ------------------- C. was the war industry built where the old one was? ---
# The answer explains B. Where a class had a broad prewar footprint the shares
# predict; where the wartime industry was greenfield they cannot.
print('\n' + '=' * 92)
print('C. SHARE OF EACH CLASS PLACED IN COUNTIES WITH NO PREWAR PLANT OF THAT KIND')
print('=' * 92)
capidx = cap.set_index('fips')
# Establishment counts only. PREVARS mixes 1940 establishment counts with the
# 1930 occupational-employment fallbacks (see BASIS); summing both would add
# plants to people. The 'war-related establishments' the text quotes are the
# manu*40 variables alone.
ESTVARS = [v for v in PREVARS if not v.startswith('o')]
WAREST = cap.set_index('fips')[ESTVARS].sum(axis=1)
res['national_medians'] = {
    'mfgshare1940': round(float(panel.mfgshare1940.median()), 5),
    'warestabs': float(WAREST.reindex(panel.fips).fillna(0.0).median()),
    'n': int(len(panel))}
print(f'{"class":13s}{"$bn":>9s}{"counties recv":>15s}{"prewar cnty>0":>15s}'
      f'{"% $ greenfield":>17s}{"basis":>20s}')
res['greenfield'] = []
for k in XWALK:
    ck = raw[(raw.pclass == k) & raw.fips.notna()].groupby('fips').v.sum()
    if ck.sum() <= 0: continue
    c = capidx['cap_' + k]
    zero = set(c[c <= 0].index) | (set(ck.index) - set(c.index))
    gfc = [f for f in ck.index if f in zero]
    gf = float(ck[ck.index.isin(zero)].sum()) / float(ck.sum())
    # The counties that took this class's work without a prewar plant of that
    # kind: what did they look like before the war? Medians over the panel,
    # against the national median, so the paper can quote both.
    sub = panel[panel.fips.isin(gfc)]
    # Total 1940 war-related establishments, summed over the 29 named industries.
    # Counties absent from the Jaworski frame are counted as zero, which is the
    # same convention the national median below uses.
    esub = WAREST.reindex(sub.fips).fillna(0.0)
    res['greenfield'].append({'class': k, 'basis': BASIS[k],
                              'bn': round(float(ck.sum()) / 1e6, 2),
                              'counties_receiving': int(len(ck)),
                              'prewar_counties': int((c > 0).sum()),
                              'greenfield_counties': int(len(gfc)),
                              'greenfield_counties_in_panel': int(len(sub)),
                              'gf_median_mfgshare1940': round(float(sub.mfgshare1940.median()), 5)
                                  if len(sub) else None,
                              'gf_median_warestabs': float(esub.median())
                                  if len(sub) else None,
                              'greenfield_dollar_share': round(gf, 4)})
    print(f'{k:13s}{ck.sum()/1e6:9.2f}{len(ck):>15,}{int((c>0).sum()):>15,}{100*gf:>17.1f}')

# ------------ D. the allocation function, re-estimated for each award year --
# The contract file carries a month for every record, so the pooled allocation
# result can be split. Two measures, because the raw rank correlation on all
# counties is dominated by coverage -- only 14.8 percent of counties received a
# contract in 1940 against 39.8 percent in 1943, which mechanically attenuates
# a rank correlation computed over the zeros.
print('\n' + '=' * 92)
print('D. DID THE ALLOCATION FUNCTION CHANGE OVER THE WAR?')
print('=' * 92)
raw['award_year'] = pd.to_numeric(raw.award_year, errors='coerce')
yr = (raw[raw.fips.notna()].groupby(['fips', 'award_year']).v.sum()
         .unstack(fill_value=0.0))
YEARS = [y for y in sorted(yr.columns) if not np.isnan(y)]
m = m.merge(yr.reset_index(), on='fips', how='left')
for y in YEARS: m[y] = m[y].fillna(0.0)
P = m.pop1940.replace(0, np.nan)
m['B_civic'] = 1000 * pd.to_numeric(m.deaths_all, errors='coerce').fillna(0) / P
m['BA'] = pd.to_numeric(m.B_A, errors='coerce').where(m.valid_BA.fillna(False))
ever = m[YEARS].sum(axis=1) > 0
res['by_year'] = {'years': [int(y) for y in YEARS],
                  'dollars_bn': [round(float(m[y].sum()) / 1e6, 2) for y in YEARS],
                  'coverage': [round(float((m[y] > 0).mean()), 4) for y in YEARS],
                  'n_ever': int(ever.sum())}
print(f'{"":30s}' + ''.join(f'{int(y):>10d}' for y in YEARS))
print(f'{"dollars placed ($bn)":30s}' + ''.join(f'{m[y].sum()/1e6:>10.1f}' for y in YEARS))
print(f'{"counties receiving (%)":30s}' + ''.join(f'{100*(m[y]>0).mean():>10.1f}' for y in YEARS))
sub = m[ever]
rho = [float(spearmanr(sub.mfgshare1940, sub[y] / sub.pop1940,
                       nan_policy='omit').statistic) for y in YEARS]
res['by_year']['rho_mfg_fixed_sample'] = [round(v, 4) for v in rho]
# the all-county version, which the text cites only to explain why it is not used
rho_all = [float(spearmanr(m.mfgshare1940, m[y] / P, nan_policy='omit').statistic)
           for y in YEARS]
res['by_year']['rho_mfg_all_counties'] = [round(v, 4) for v in rho_all]
print(f'{"rho(1940 mfg share), fixed n":30s}' + ''.join(f'{v:>10.3f}' for v in rho))
for bl, bc, key in [('B_civic (per resident)', 'B_civic', 'b_civic'),
                    ('B_A (per enlistee)', 'BA', 'b_enlistee')]:
    co, pv, se, nn = [], [], [], []
    for y in YEARS:
        m['_dv'] = np.arcsinh(1000 * m[y] / P)
        q = m[['_dv', bc, 'statefip'] + CTRL].replace([np.inf, -np.inf], np.nan).dropna()
        D = pd.get_dummies(q.statefip, prefix='s', drop_first=True).astype(float)
        r = sm.OLS(q._dv, sm.add_constant(pd.concat([q[[bc] + CTRL].astype(float), D],
                                                    axis=1))
                   ).fit(cov_type='cluster', cov_kwds={'groups': q.statefip})
        co.append(round(float(r.params[bc]), 5)); pv.append(round(float(r.pvalues[bc]), 4))
        se.append(round(float(r.bse[bc]), 5)); nn.append(int(r.nobs))
    res['by_year'][key] = {'coef': co, 'p': pv, 'se': se, 'n': nn}
    print(f'{"b(" + bl + ")":30s}' + ''.join(f'{v:>10.5f}' for v in co))
    print(f'{"   (se)":30s}' + ''.join(f'{v:>10.5f}' for v in se))
    print(f'{"   p":30s}' + ''.join(f'{v:>10.3f}' for v in pv))
    print(f'{"   N":30s}' + ''.join(f'{v:>10,}' for v in nn))

(AN / 'shiftshare.json').write_text(json.dumps(res, indent=2))
Z.to_parquet(AN / 'shiftshare_county.parquet', index=False)
print(f'\n-> {AN/"shiftshare.json"}')
print(f'-> {AN/"shiftshare_county.parquet"}')
