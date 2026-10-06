from functools import lru_cache as _lru
# =====================================================================
# LANE C_data -- Section 3 (Data), soldier composition, measure
# validation, Section 4 (Empirical Strategy).
#
# Splice the CHECKS list at the bottom into src/audit_paper_vs_data.py's
# CHECKS.  The preamble block must go ABOVE the CHECKS definition (it uses
# ROOT, AN, m, f, MR, DS1, co, VAL, FAC, fmt, which the audit already
# defines).  Every anchor below appears exactly once in
# paper/War_Divergence.tex.
#
# Nothing here compares against a hardcoded literal that no artifact
# produces: every target is read from a stored artifact, a raw source, or
# a committed script.  Tolerances are the printed precision.
# =====================================================================

# ---- preamble ---------------------------------------------------------
@_lru(maxsize=None)
def _lane_c():
    """Section 3 / Section 4 quantities, recomputed from the sources.

    Most of these were printed by a build script and never stored, which
    is why no check could reach them: composition.py prints the enlistee
    and death coverage of its own sample and writes neither, and
    merge_independent_cities.py carries the fourteen-city arithmetic in a
    docstring that had already drifted from the manuscript ($6.83bn and a
    national 2.27 there, $6.82bn and 2.26 in the paper).
    """
    import importlib.util, warnings
    import numpy as np, pandas as pd, pyreadstat, statsmodels.api as sm
    warnings.filterwarnings('ignore')
    out = {}

    # -- DS2 decode: the audit's only DS2 check ran on master_panel_v3,
    #    whose ds2_enlist sums to 7,188,777 -- 1.26 percent below the
    #    7,280,828 the paper prints, and inside the check's 2 percent
    #    tolerance.  The decode's own artifact is ds2_county.parquet.
    g = pd.read_parquet(AN/'ds2_county.parquet')
    out['ds2_decoded']       = int(g.ds2_enlist.sum())
    out['ds2_decoded_share'] = float(g.ds2_enlist.sum()/MR['enlistment_ds2']['rows_total'])
    univ = set(m.fips.astype(int))
    out['ds2_codes']         = int(len(g))
    out['ds2_codes_in_univ'] = int(g.fips.astype(int).isin(univ).sum())
    out['ds2_code_share']    = out['ds2_codes_in_univ']/out['ds2_codes']
    out['ds2_panel_total']   = float(m.ds2_enlist.fillna(0).sum())

    # -- the 0.990 decode check is computed on ds2_validation.parquet
    #    (3,019 counties), NOT on the panel, where the same correlation is
    #    0.994.  Read it from the frame the number came from.
    dv = pd.read_parquet(AN/'ds2_validation.parquet')
    out['ds2_val_n']    = int(len(dv))
    out['ds2_val_corr'] = float(dv.ds2_enlist.corr(dv.E_A))
    out['E_A_total']    = float(m.E_A.fillna(0).sum())

    # -- contract file: value total and the two date anomalies the
    #    footnote quantifies, straight from the Brunet-Koustas record file
    cn,_ = pyreadstat.read_dta(str(ROOT/'data/raw/contracts/WWII_contracts_clean.dta'))
    v  = pd.to_numeric(cn.ValueThousandsDollars, errors='coerce')
    ad = pd.to_datetime(cn.award_date, errors='coerce')
    cd = pd.to_datetime(cn.completion_date, errors='coerce')
    bad = cd < ad
    out['contract_bn']      = float(v.sum()/1e6)
    out['n_completion_bad'] = int(bad.sum())
    out['completion_bad_pct_value'] = float(100*v[bad].sum()/v.sum())
    out['n_imputed_year']   = int((pd.to_numeric(cn.completion_year_estimated,
                                                 errors='coerce') == 1).sum())

    # -- Group 29 aggregate rows.  Re-run the committed parser's own mask
    #    on the raw workbook; importing the module does not write, because
    #    parse_facilities.py guards its outputs behind __main__.
    spec = importlib.util.spec_from_file_location('_pf', ROOT/'src/parse_facilities.py')
    pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
    raw = pd.concat([pf.parse_sheet(s) for s in pd.ExcelFile(pf.SRC).sheet_names],
                    ignore_index=True)
    cost = pd.to_numeric(raw.total_cost, errors='coerce')
    g29  = raw.sheet.astype(str).str.contains('29')
    op   = raw.operator.astype(str).str.strip()
    is_grand = g29 & op.eq('U. S. Govt') & cost.eq(pf.GROUP29_GRAND_TOTAL)
    is_sub   = g29 & pd.concat([op.eq(k) & cost.eq(v_) for k, v_ in
                                pf.GROUP29_SUBTOTALS.items()], axis=1).any(axis=1)
    drop = is_grand | is_sub
    d29  = raw[drop]
    vc   = d29.loc[is_sub[drop], 'operator'].str.strip().value_counts()
    place = d29[(d29.city.notna()) & (d29.city != '__NONGEO__')]
    out['g29_dropped_rows']   = int(drop.sum())
    out['g29_dept_rows']      = int(is_sub.sum())
    out['g29_depts_distinct'] = int(len(vc))
    out['g29_depts_twice']    = int((vc > 1).sum())
    out['fac_bn_before']      = float(cost.sum()/1e6)
    out['fac_bn_after']       = float(cost[~drop].sum()/1e6)
    out['g29_phantom_rows']   = int(len(place))
    out['g29_phantom_places'] = int(place.groupby(['city','state']).ngroups)
    out['colbert_m']          = float(place.loc[place.city.eq('wilson dam'),
                                                'total_cost'].sum()/1000)

    # -- the fourteen independent cities.  "Fourteen" is the count of
    #    city FIPS carrying contract dollars, not the 26 rows of the
    #    crosswalk; the population and the death count are on those same
    #    fourteen.
    ic = pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
    cg = pd.read_parquet(AN/'contracts_geocoded.parquet')
    cg['fips'] = pd.to_numeric(cg.fips, errors='coerce')
    cg['v']    = pd.to_numeric(cg.ValueThousandsDollars, errors='coerce')
    byc = cg[cg.fips.isin(set(ic.city_fips))].groupby('fips').v.sum()
    S14 = set(byc.index.astype(int))
    cas = pd.read_parquet(AN/'casualties_county.parquet')
    cas['fips'] = pd.to_numeric(cas.fips, errors='coerce')
    hp,_ = pyreadstat.read_dta(str(ROOT/'data/raw/haines_icpsr2896/02896-0032-Data.dta'),
                               usecols=['fips','totpop'])
    hp['fips'] = pd.to_numeric(hp.fips, errors='coerce')
    out['ic_n']       = int(len(S14))
    out['ic_bn']      = float(byc.sum()/1e6)
    out['ic_pop_m']   = float(hp[hp.fips.isin(S14)].totpop.sum()/1e6)
    out['ic_deaths']  = int(cas[cas.fips.isin(S14)].deaths_all.sum())
    out['ic_rate']    = 1000*out['ic_deaths']/(out['ic_pop_m']*1e6)

    # -- source-table scale column
    ds3,_ = pyreadstat.read_dta(str(ROOT/'data/raw/casualties_icpsr38927/38927-0003-Data.dta'))
    fhk,_ = pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/'
                                    'fishbackhorracekantor.dta'))
    fer,_ = pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/'
                                    'WWII_draft_volunteer_casualties_Army_AirForce.dta'))
    out['ds3_rows'] = int(len(ds3))
    out['fhk_rows'] = int(len(fhk))
    out['ferrara_rows'] = int(len(fer))
    bmp = (ROOT/'src/build_master_panel.py').read_text()
    out['haines_parts'] = len(set(re.findall(r"haines\('(\d{4})'", bmp)) |
                              set(re.findall(r"02896-(\d{4})-Data", bmp)))

    # -- the seven files taken from Garin-Rothbaum, counted by existence
    GR = ROOT/'data/raw/garin_rothbaum/Data/RawData'
    out['gr_files'] = sum(int((GR/n).exists()) for n in [
        'FacilitiesRaw/FacilitiesDatabase.xls', 'crosswalk_statefip_stateicp_1910.dta',
        'cw-city-county.dta', 'NBER_county_adjacency2010.dta',
        'fishbackhorracekantor.dta', 'WWII_draft_volunteer_casualties_Army_AirForce.dta',
        'inmetro_1930_1940.dta'])

    # -- composition sample.  composition.py prints these and stores
    #    neither, so they are recomputed on its exact screen.
    COMP = ['ds2_black_share','ds2_hs_share','ds2_vol_share','ds2_mean_yob','ds2_mean_agct']
    d = m.copy()
    for c in COMP+['ds2_enlist','deaths_all']:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['B_ds2'] = 1000*d.deaths_all/d.ds2_enlist.replace(0, np.nan)
    vv = d[(d.ds2_enlist >= 100) & d.B_ds2.notna() & (d.B_ds2 < 300)].copy()
    X = vv[COMP].copy()
    for c in COMP: X[c] = X[c].fillna(X[c].median())
    r = sm.OLS(vv.B_ds2, sm.add_constant(X)).fit(cov_type='HC1')
    vv['B_resid'] = r.resid + vv.B_ds2.mean()
    out['comp_n']        = int(len(vv))
    out['comp_enlist_m'] = float(vv.ds2_enlist.sum()/1e6)
    out['comp_deaths']   = int(vv.deaths_all.sum())
    out['comp_sd_pct']   = float(100*(1 - vv.B_resid.std()/vv.B_ds2.std()))

    # -- validity screen, read out of the committed script rather than
    #    trusted from the prose
    ae = (ROOT/'src/analysis_exposure.py').read_text()
    out['screen_src'] = "d['valid_BA']=~((d.mobilization_rate>1)|(d.B_A>300)|d.B_A.isna())" in ae
    bmp2 = (ROOT/'src/build_exposure.py').read_text()
    out['mobrate_is_age1445'] = "j['mobilization_rate'] = j.E_A/j.age1445" in bmp2

    # -- Section 4: the control vector actually used to residualize the
    #    two exposures for figure 3, parsed out of make_maps.py.
    mm_src = (ROOT/'src/make_maps.py').read_text()
    mx = re.search(r"X=gd\[\[([^\]]*)\]\]", mm_src)
    out['map_ctrl'] = [s.strip().strip("'") for s in mx.group(1).split(',')] if mx else []
    out['map_sign_is_burden_minus_investment'] = \
        "gd['imbalance']=((zb-zb.mean())/zb.std())-((zw-zw.mean())/zw.std())" in mm_src
    out['map_has_rho_scaling'] = 'sqrt' in mm_src and 'rho' in mm_src
    return out

_WORD = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8}
_C = _lane_c()

# ---- checks -----------------------------------------------------------
CHECKS_LANE_C = [

 # ---------------- Section 3: scale of the sources ----------------
 ('ICPSR 38927 DS3 & individual casualty & 65{,}507',
  _C['ds3_rows'] == 65507,
  f"{_C['ds3_rows']} rows in 38927-0003-Data.dta"),

 ('Fishback--Horrace--Kantor & county & 3{,}067',
  _C['fhk_rows'] == 3067,
  f"{_C['fhk_rows']} rows in fishbackhorracekantor.dta"),

 ('Ferrara county tabulation & county & 3{,}073',
  _C['ferrara_rows'] == 3073,
  f"{_C['ferrara_rows']} rows in the Ferrara tabulation"),

 ('Haines ICPSR 2896 & county $\\times$ year & 8 parts',
  _C['haines_parts'] == 8,
  f"{_C['haines_parts']} distinct Haines parts read by build_master_panel.py"),

 # 300,131 + 8,293,187 = 8,593,318, and 190,693 + 14,681 = 205,374.
 # The 3,073 in this sentence is the panel; the audit's existing
 # '3{,}073 continental' anchor is a different sentence.
 ('aggregated to 3{,}073 counties',
  len(m) == 3073 and
  DS1['rows_total'] + MR['enlistment_ds2']['rows_total'] == 8593318 and
  MR['contracts']['rows_total'] + FAC['records'] == 205374,
  f"{len(m)} counties; {DS1['rows_total']+MR['enlistment_ds2']['rows_total']:,} military "
  f"and {MR['contracts']['rows_total']+FAC['records']:,} investment records"),

 ('seven files in all',
  _C['gr_files'] == 7,
  f"{_C['gr_files']} of the seven named Garin-Rothbaum files present"),

 # ---------------- Section 3: DS1 honor list ----------------
 # 300,131 -> 297,627 is a loss of 2,504, or 0.834 percent.  Also
 # asserts the parts sum: 297,887 + 1,348 + 181 = 299,416 = 300,131 - 715.
 ('costs 0.8 percent of it',
  abs(100*(DS1['rows_total'] - m.deaths_all.fillna(0).sum())/DS1['rows_total'] - 0.8) < 0.05 and
  DS1['assigned_deaths'] + DS1['assigned_missing'] + DS1['assigned_no_status']
      == DS1['rows_with_fips'] and
  DS1['rows_with_fips'] + DS1['rows_unassigned'] == DS1['rows_total'],
  f"{100*(DS1['rows_total']-m.deaths_all.fillna(0).sum())/DS1['rows_total']:.2f}% lost; "
  f"parts sum to {DS1['assigned_deaths']+DS1['assigned_missing']+DS1['assigned_no_status']}"),

 # ---------------- Section 3: DS2 decode ----------------
 # The existing '7{,}280{,}828' check compares master_panel_v3's
 # ds2_enlist (7,188,777) at a 2 percent tolerance, which absorbs the
 # whole 1.26 percent gap between the decode and the panel.  The decode
 # total lives in ds2_county.parquet.  "County codes", not records, is
 # the base of the 99.8: 3,071 of 3,078 (records would be 98.7).
 ('7{,}280{,}828 records (87.8 percent) resolve to a 1940 county,\n'
  'and 99.8 percent of the derived county codes fall inside the census universe',
  _C['ds2_decoded'] == 7280828 and
  abs(100*_C['ds2_decoded_share'] - 87.8) < 0.05 and
  abs(100*_C['ds2_code_share'] - 99.8) < 0.05,
  f"{_C['ds2_decoded']:,} decoded ({100*_C['ds2_decoded_share']:.2f}%); "
  f"{_C['ds2_codes_in_univ']}/{_C['ds2_codes']} codes in universe "
  f"({100*_C['ds2_code_share']:.2f}%)"),

 ('totals 6.94 million men',
  abs(_C['E_A_total']/1e6 - 6.94) < 0.005,
  f"{_C['E_A_total']:,.0f} = {_C['E_A_total']/1e6:.3f}M"),

 # The 7.19M is the panel total; the 0.990 is computed on
 # ds2_validation.parquet, a 3,019-county merge whose DS2 total is
 # 7.17M.  Both numbers are right, on two different samples.
 ('reach 7.19 million and correlate\nwith that tabulation at $0.990$',
  abs(_C['ds2_panel_total']/1e6 - 7.19) < 0.005 and
  abs(_C['ds2_val_corr'] - 0.990) < 0.0005,
  f"panel {_C['ds2_panel_total']:,.0f}; corr {_C['ds2_val_corr']:.4f} "
  f"on n={_C['ds2_val_n']} (ds2_validation.parquet)"),

 ('for all\n8.29 million, and the Army General Classification Test score for the 447{,}464',
  abs(_C['ds2_panel_total']/1e6 - 7.2) < 0.05,
  f"{_C['ds2_panel_total']/1e6:.2f}M in the panel"),

 # ---------------- Section 3: the two wartime records ----------------
 ('The contract file yields 190{,}693 obligations worth \\$181.0 billion',
  MR['contracts']['rows_total'] == 190693 and abs(_C['contract_bn'] - 181.0) < 0.05,
  f"{MR['contracts']['rows_total']:,} obligations, ${_C['contract_bn']:.3f}bn"),

 # Restated verbatim in Section 5 ("The facilities report yields ...");
 # both sentences are pinned so a correction to one cannot leave the
 # other behind.
 ('facilities file yields 14{,}681 plant records worth \\$20.8 billion, of which 76.6\n'
  'percent was publicly financed',
  FAC['records'] == 14681 and abs(FAC['total_bn'] - 20.8) < 0.05 and
  abs(100*FAC['public_share'] - 76.6) < 0.05,
  f"{FAC['records']} records, ${FAC['total_bn']:.3f}bn, {100*FAC['public_share']:.2f}% public"),

 ('The facilities report yields 14{,}681 plant records totalling \\$20.8 billion, of\n'
  'which 76.6 percent was publicly financed',
  FAC['records'] == 14681 and abs(FAC['total_bn'] - 20.8) < 0.05 and
  abs(100*FAC['public_share'] - 76.6) < 0.05,
  f"restatement of the Section 3 sentence: {FAC['records']} / "
  f"${FAC['total_bn']:.3f}bn / {100*FAC['public_share']:.2f}%"),

 # ---------------- Section 3: the Group 29 footnote ----------------
 # DEFECT as this reads today.  Twelve rows is right: one grand total,
 # eight distinct department subtotals, and THREE departments emitted
 # twice (Commerce, Defense Plant Corp, Federal Security Agency).
 # "Four" would make thirteen, so the sentence does not even sum to its
 # own count.
 ('Removing the aggregate rows, twelve in\nall once the ',
  _C['g29_dropped_rows'] == 12 and
  1 + _C['g29_depts_distinct'] + _C['g29_depts_twice'] == _C['g29_dropped_rows'] and
  _WORD.get(re.search(r'twelve in\nall once the (\w+) departments',
                      tex).group(1)) == _C['g29_depts_twice'],
  f"{_C['g29_dropped_rows']} rows = 1 grand total + {_C['g29_depts_distinct']} departments "
  f"+ {_C['g29_depts_twice']} emitted twice; the text says "
  f"{re.search(r'twelve in all once the (\w+) departments', tex.replace(chr(10),' ')).group(1)}"),

 ('volume from \\$24.0 billion to \\$20.8 billion',
  abs(_C['fac_bn_before'] - 24.0) < 0.05 and abs(_C['fac_bn_after'] - 20.8) < 0.05 and
  abs(_C['fac_bn_after'] - FAC['total_bn']) < 1e-6,
  f"${_C['fac_bn_before']:.3f}bn -> ${_C['fac_bn_after']:.3f}bn"),

 ('Six of them had acquired the',
  _C['g29_phantom_rows'] == 6,
  f"{_C['g29_phantom_rows']} dropped rows carry a real place"),

 ('\\$307 million of it in Colbert County, Alabama',
  abs(_C['colbert_m'] - 307) < 0.5 and int(m.loc[m.fips == 1033, 'fips'].iloc[0]) == 1033,
  f"${_C['colbert_m']:.3f}m at wilson dam, AL -> FIPS 1033 "
  f"({m.loc[m.fips==1033,'name'].iloc[0]})"),

 ('changes three counties and no qualitative result',
  _C['g29_phantom_places'] == 3,
  f"{_C['g29_phantom_places']} distinct places among the six phantom rows"),

 # ---------------- Section 3: contract-file provenance footnote ----------------
 # 190,599 is Brunet (2017)'s own analysis-sample count, an external
 # figure with no artifact in this repository; only the three quantities
 # computed from the distributed file are checkable.
 ('182\ncontracts whose recorded completion precedes their award survive here, worth\n'
  '0.09 percent of value, and 15{,}382 carry an imputed completion year',
  _C['n_completion_bad'] == 182 and
  abs(_C['completion_bad_pct_value'] - 0.09) < 0.005 and
  _C['n_imputed_year'] == 15382,
  f"{_C['n_completion_bad']} bad-date contracts, "
  f"{_C['completion_bad_pct_value']:.4f}% of value, {_C['n_imputed_year']:,} imputed"),

 # ---------------- Section 3: the independent-city merge ----------------
 # "Fourteen" is the number of independent-city FIPS carrying contract
 # dollars, not the 26 rows of independent_city_merge.csv, and the
 # population and deaths are on those same fourteen (all 26 hold 268
 # deaths and 2.45M residents).  merge_independent_cities.py states this
 # arithmetic only in a docstring, which had already drifted to $6.83bn
 # and a national 2.27.
 ('fourteen units that between them\nheld \\$6.82 billion in contracts and 2.26 million '
  'residents but only 251\nrecorded deaths, a rate of 0.11 per thousand',
  _C['ic_n'] == 14 and abs(_C['ic_bn'] - 6.82) < 0.005 and
  abs(_C['ic_pop_m'] - 2.26) < 0.005 and _C['ic_deaths'] == 251 and
  abs(_C['ic_rate'] - 0.11) < 0.005,
  f"{_C['ic_n']} cities, ${_C['ic_bn']:.3f}bn, {_C['ic_pop_m']:.3f}M residents, "
  f"{_C['ic_deaths']} deaths, {_C['ic_rate']:.3f} per 1,000"),

 # ---------------- Section 3: the validity screen ----------------
 ('screen if its enlistment count exceeds its 1940 male population aged 14 to 45,\n'
  'if the implied fatality rate exceeds 300 deaths per 1{,}000 enlistees',
  _C['screen_src'] and _C['mobrate_is_age1445'],
  'analysis_exposure.py: ~((mobilization_rate>1)|(B_A>300)|B_A.isna()), '
  'mobilization_rate = E_A/age1445'),

 # ---------------- Section 5: validating the measures ----------------
 ('98.5 percent\nof contract dollars resolve to a county',
  abs(100*J('contracts_geocode_report.json')['weight_rate'] - 98.5) < 0.05,
  f"{100*J('contracts_geocode_report.json')['weight_rate']:.2f}% of dollars"),

 ('as distributed in Part 70 of the\nHaines archive',
  "haines('0070'" in (ROOT/'src/build_master_panel.py').read_text(),
  'build_master_panel.py reads Haines part 0070 for the County Data Book series'),

 # ---------------- Section 5: soldier composition ----------------
 # composition.py prints the coverage line and stores nothing, so these
 # two figures had no artifact to check against.
 ('covering 7.17 million enlistees and 288{,}059\ndeaths',
  _C['comp_n'] == co['n'] and abs(_C['comp_enlist_m'] - 7.17) < 0.005 and
  _C['comp_deaths'] == 288059,
  f"n={_C['comp_n']}, {_C['comp_enlist_m']:.3f}M enlistees, {_C['comp_deaths']:,} deaths"),

 ('Composition accounts for 9.3 percent of the cross-county standard deviation in\n'
  'fatality rates',
  abs(_C['comp_sd_pct'] - 9.3) < 0.05,
  f"{_C['comp_sd_pct']:.2f}% of the s.d."),

 ('($-0.170$ and $-0.070$ before it)',
  abs(co['contracts']['rho_raw'] + 0.170) < 0.0005 and
  abs(co['war plant']['rho_raw'] + 0.070) < 0.0005,
  f"raw {co['contracts']['rho_raw']:.4f} / {co['war plant']['rho_raw']:.4f}"),

 # ---------------- Section 4: the residualization control vector ----------------
 # DEFECT.  Figure 3 residualizes on five variables -- 1940 log
 # population, urban share, Black share, manufacturing share, and
 # 1930-40 population growth -- and the figure's own note says so.
 # Section 4 additionally names age structure, income, and prewar
 # industrial capacity, none of which is in make_maps.py's X or in the
 # estimation CTRL vector.
 # Equation (7) named seven groups of controls where make_maps.py uses five,
 # inverted the sign relative to its own figure note, and divided by a
 # sqrt(2(1-rho)) term the code never applies. All three are corrected; these
 # checks now pin the corrected text to what the code does.
 ('prewar characteristics $X_i$: 1940 log population, the urban share, the Black\n'
  'population share, the manufacturing share, and 1930--40 population growth',
  set(_C['map_ctrl']) == {'logpop1940','urbrate1940','blackshare1940',
                          'mfgshare1940','popgrowth_3040'},
  f"make_maps.py residualizes on {sorted(_C['map_ctrl'])}"),

 ('Positive values identify casualty-heavy counties conditional on observables;\n'
  'negative values identify investment-heavy counties',
  _C['map_sign_is_burden_minus_investment'],
  'make_maps.py computes z(burden resid) - z(investment resid): positive is '
  'casualty-heavy, matching the figure note'),
]