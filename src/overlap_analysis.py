#!/usr/bin/env python3
"""
The paper's central descriptive estimand: how far does the county geography of
Army/AAF fatal loss coincide with the county geography of war procurement?

  A  = sum_i min(p_i^D, p_i^W)          overlap coefficient, 0..1
  JS = Jensen-Shannon divergence         distributional distance
  rho= Spearman rank correlation         ordinal association

Prints the numbers. Writes data/analysis/overlap_results.json.
"""
import json
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
AN   = ROOT/'data/analysis'

# --- the master panel is the single county universe (independent cities folded)
p = pd.read_parquet(AN/'master_panel.parquet')[
      ['fips','name','pop1940','deaths_all','contract_k']].copy()
print(f'1940 county universe: {len(p):,} counties, {p.pop1940.sum()/1e6:.1f}M people')
print(f'  counties with any Army/AAF death : {(p.deaths_all>0).sum():,} '
      f'({(p.deaths_all>0).mean():.1%})')
print(f'  counties with any contract dollar: {(p.contract_k>0).sum():,} '
      f'({(p.contract_k>0).mean():.1%})')
print(f'  counties with deaths but NO contracts: '
      f'{((p.deaths_all>0)&(p.contract_k==0)).sum():,}')

# --- national shares ------------------------------------------------------
pD = p.deaths_all       / p.deaths_all.sum()
pW = p.contract_k / p.contract_k.sum()

A   = float(np.minimum(pD, pW).sum())
mmix = 0.5*(pD+pW)
def kl(a, b):
    mask = a > 0
    return float(np.sum(a[mask]*np.log2(a[mask]/b[mask])))
JS  = 0.5*kl(pD, mmix) + 0.5*kl(pW, mmix)
rho = spearmanr(p.deaths_all, p.contract_k).statistic

# concentration
def top_share(s, n):
    return float(s.sort_values(ascending=False).head(n).sum()/s.sum())

res = {
  'n_counties': int(len(p)),
  'overlap_coefficient_A': round(A, 4),
  'jensen_shannon_bits': round(JS, 4),
  'spearman_rho': round(float(rho), 4),
  'deaths_total': int(p.deaths_all.sum()),
  'contract_dollars_k_total': float(p.contract_k.sum()),
  'deaths_top20_share':    round(top_share(p.deaths_all, 20), 4),
  'contracts_top20_share': round(top_share(p.contract_k, 20), 4),
  'deaths_top100_share':   round(top_share(p.deaths_all, 100), 4),
  'contracts_top100_share':round(top_share(p.contract_k, 100), 4),
  'counties_zero_contracts': int((p.contract_k == 0).sum()),
    # The paper cites the JOINT count -- lost men AND got nothing -- and the
    # audit was checking the marginal above it with a one-sided inequality,
    # so any value from 1 to 1,583 would have passed.
    'counties_deaths_no_contracts':
        int(((p.deaths_all.fillna(0) > 0) & (p.contract_k.fillna(0) == 0)).sum()),
}
print(f"""
=== CENTRAL RESULT =========================================
  overlap coefficient  A   = {A:.3f}
  Jensen-Shannon           = {JS:.3f} bits
  Spearman rank rho        = {rho:.3f}

  top-20 counties hold {res['deaths_top20_share']:.1%} of deaths
                   but {res['contracts_top20_share']:.1%} of contract dollars
  top-100 counties     {res['deaths_top100_share']:.1%} of deaths
                   vs  {res['contracts_top100_share']:.1%} of dollars
  {res['counties_zero_contracts']:,} counties received zero major contracts
============================================================""")

# per-capita burden vs investment
p['B_civic'] = 1000*p.deaths_all/p.pop1940.replace(0, np.nan)
p['W_pc']    = p.contract_k/p.pop1940.replace(0, np.nan)
sub = p.dropna(subset=['B_civic','W_pc'])
res['spearman_percapita'] = round(float(spearmanr(sub.B_civic, sub.W_pc).statistic), 4)
print(f"per-capita: Spearman(B_civic, contract $/person) = {res['spearman_percapita']:.3f}")

p.to_parquet(AN/'county_exposure_panel.parquet', index=False)
(AN/'overlap_results.json').write_text(json.dumps(res, indent=2))
print(f"\npanel -> {AN/'county_exposure_panel.parquet'}")
