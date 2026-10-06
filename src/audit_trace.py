#!/usr/bin/env python3
"""Emit a machine-checked provenance table: every headline number -> its script and artifact."""
import json, hashlib
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
def J(n): return json.loads((AN/n).read_text())
o,t,e,c,rb,iv,ivs,ivv = (J('overlap_results.json'),J('three_geographies.json'),
    J('exposure_results.json'),J('composition_results.json'),J('robustness.json'),
    J('iv_results.json'),J('iv_single_results.json'),J('iv_validity.json'))
m=pd.read_parquet(AN/'master_panel_iv.parquet')
def h(p):
    f=ROOT/p
    return hashlib.sha256(f.read_bytes()).hexdigest()[:12] if f.exists() else 'MISSING'
CLAIMS=[
 ('Counties in the estimation sample', f'{len(m):,}', 'src/build_master_panel.py','data/analysis/master_panel.parquet'),
 ('1940 population covered', f'{m.pop1940.sum()/1e6:.1f}M','src/build_master_panel.py','data/analysis/master_panel.parquet'),
 ('Army/AAF deaths', f'{m.deaths_all.sum():,.0f}','src/build_county_panel.py','data/analysis/casualties_county.parquet'),
 ('Enlistment records mapped', f'{m.ds2_enlist.sum():,.0f}','src/build_ds2_county.py','data/analysis/ds2_county.parquet'),
 ('Contracts / value', f'{m.n_contracts.sum():,.0f} / ${m.contract_k.sum()/1e6:.1f}bn','src/geocode.py','data/analysis/contracts_geocoded.parquet'),
 ('War plants / public value', f'{m.n_plants.sum():,.0f} / ${m.fac_public_k.sum()/1e6:.1f}bn','src/parse_facilities.py','data/analysis/facilities_geocoded.parquet'),
 ('Overlap coefficient A', o['overlap_coefficient_A'],'src/overlap_analysis.py','data/analysis/overlap_results.json'),
 ('Jensen-Shannon divergence', o['jensen_shannon_bits'],'src/overlap_analysis.py','data/analysis/overlap_results.json'),
 ('Per-capita Spearman (contracts)', o['spearman_percapita'],'src/overlap_analysis.py','data/analysis/overlap_results.json'),
 ('Counties with a death / a contract', f"{o['n_counties']:,} base",'src/overlap_analysis.py','data/analysis/overlap_results.json'),
 ('Zero-contract counties', f"{o['counties_zero_contracts']:,}",'src/overlap_analysis.py','data/analysis/overlap_results.json'),
 ('Pairwise A, plant x military', t['pairwise']['W_F x W_M']['A'],'src/three_geographies.py','data/analysis/three_geographies.json'),
 ('Per-capita rho vs burden (3)', str(t['percapita_vs_burden']),'src/three_geographies.py','data/analysis/three_geographies.json'),
 ('B^A national fatality rate', f"{e['fatality_rate_national']}/1000",'src/analysis_exposure.py','data/analysis/exposure_results.json'),
 ('B^A 90/10 county ratio', e['BA_p90_p10_ratio'],'src/analysis_exposure.py','data/analysis/exposure_results.json'),
 ('Composition R^2', c['composition_R2'],'src/composition.py','data/analysis/composition_results.json'),
 ('Composition-adjusted rho (contracts)', c['contracts']['rho_adjusted'],'src/composition.py','data/analysis/composition_results.json'),
 ('Pre-trend: W_C on 1930-40 growth', rb['pretrends'][0]['coef']['W_C'],'src/robustness.py','data/analysis/robustness.json'),
 ('Conley SE, W_M on mfg 1970', rb['conley'][1]['W_M']['se_conley'],'src/robustness.py','data/analysis/robustness.json'),
 ('First-stage F, plant on IMP', iv['first_stage'][2]['F'],'src/iv_analysis.py','data/analysis/iv_results.json'),
 ('IV partial R^2 (plant)', ivs[4]['partial_r2'],'src/iv_single.py','data/analysis/iv_single_results.json'),
 ('Placebo: IMP on 1940 mfg share', ivv['placebo'][1]['imp_coef'],'src/iv_validity.py','data/analysis/iv_validity.json'),
]
rows=[]
for claim,val,script,art in CLAIMS:
    rows.append({'claim':claim,'value':str(val),'script':script,'artifact':art,
                 'script_sha':h(script),'artifact_sha':h(art)})
df=pd.DataFrame(rows)
(AN/'audit_trace.json').write_text(df.to_json(orient='records',indent=2))
print(f'{len(df)} claims traced; missing artifacts: {(df.artifact_sha=="MISSING").sum()}')
print(df[['claim','value','script']].to_string(index=False,max_colwidth=44))
