from functools import lru_cache as _lru
# LANE A_restate -- abstract, introduction, Section 6 (rhetoric), Conclusion.
#
# These sections restate figures established in Results.  Before this lane the
# audit held 7 checks anchored in the abstract, 5 in the introduction (four of
# which used anchors that appear 2-4 times in the manuscript and therefore
# cannot distinguish the primary statement from its restatement), 0 in
# Section 6, and 1 in the Conclusion.  Every anchor below occurs exactly once.
#
# PRELUDE -- splice above CHECKS, after the artifact-loading block.
# ---------------------------------------------------------------------------
MDS = J('matched_design_setup.json')
# The three allocation-vs-allocation overlaps (the D pairs are a different
# statistic and the introduction/conclusion range is over the W pairs only).
_WA   = [v['A']        for k, v in tg['pairwise'].items() if 'D' not in k]
_WRHO = {k: v['spearman'] for k, v in tg['pairwise'].items() if 'D' not in k}
_BR   = ACR['fatal burden, per resident']
_PREWAR = ('1940 manufacturing share', '1940 urban share', '1940 log population')
# The composition sample's coverage.  composition_results.json stores n and the
# correlations but NOT the enlistee count the paper quotes, so it is recomputed
# on exactly the filter composition.py applies.
@_lru(maxsize=None)
def _comp_cov():
    e = pd.to_numeric(m.ds2_enlist, errors='coerce')
    d = pd.to_numeric(m.deaths_all, errors='coerce')
    B = 1000 * d / e.replace(0, np.nan)
    v = m[(e >= 100) & B.notna() & (B < 300)]
    return float(pd.to_numeric(v.ds2_enlist, errors='coerce').sum()), int(len(v))
COMP_ENL, COMP_N = _comp_cov()
# "only two received both" is the difference between the pre-drop and design
# treated counts: matched_military.py drops counties that are both plant- and
# installation-treated so the two designs cannot contaminate each other.
BOTH_TREATED = mm['n_treated_predrop'] - mm['n_treated_design']
EXP_BOTH     = MDS['sample_treated'] * mm['n_treated_predrop'] / MDS['sample_n']
_DEATHPCT    = 100 * (m.deaths_all.fillna(0) > 0).mean()
_CONTPCT     = 100 * (m.contract_k.fillna(0) > 0).mean()
# ---------------------------------------------------------------------------

CHECKS_A_RESTATE = [

 # ================= ABSTRACT =================================================
 ('Assembling a 3{,}073-county panel from the Civilian Production',
                                   o['n_counties'] == 3073 and len(m) == 3073 and
                                   ex['n_total'] == 3073,
                                   f"{o['n_counties']} counties, panel {len(m)}"),
 ('report, 8.3 million Army enlistment records',
                                   round(MR['enlistment_ds2']['rows_total'] / 1e6, 1) == 8.3,
                                   f"{MR['enlistment_ds2']['rows_total']:,}"),

 # ================= INTRODUCTION =============================================
 # 'at $+0.693$', '$+0.23$ to $+0.51$', '98.2 percent' and '48.5 percent' are
 # already checked, but each of those anchors matches 2-4 places in the text and
 # the audit stops at the first.  These re-anchor the introduction's own copy.
 ('geographies whose pairwise overlap runs from $0.22$ to $0.59$, and of 2{,}973\n'
  'counties only two received both a large public plant and a top-decile\n'
  'installation, against 2.2 expected under independence.',
                                   round(min(_WA), 2) == 0.22 and round(max(_WA), 2) == 0.59
                                   and MDS['sample_n'] == 2973 and BOTH_TREATED == 2
                                   and round(EXP_BOTH, 1) == 2.2,
                                   f"A {min(_WA):.4f}-{max(_WA):.4f}; {MDS['sample_n']} counties; "
                                   f"both={BOTH_TREATED} vs {EXP_BOTH:.2f} expected"),
 ('contract dollars correlate with the 1940 manufacturing share at $+0.693$, the\n'
  'urban share at $+0.648$ and log population at $+0.666$; with fatal burden they\n'
  'correlate at $-0.026$.',
                                   round(ACR['1940 manufacturing share']['W_C']['rho'], 3) == 0.693
                                   and round(ACR['1940 urban share']['W_C']['rho'], 3) == 0.648
                                   and round(ACR['1940 log population']['W_C']['rho'], 3) == 0.666
                                   and round(_BR['W_C']['rho'], 3) == -0.026,
                                   ' '.join(fmt(ACR[r]['W_C']['rho']) for r in _PREWAR)
                                   + f" burden {_BR['W_C']['rho']:+.4f}"),
 ('Plant and installations load on the same prewar\n'
  'characteristics at $+0.23$ to $+0.51$ and on burden at $+0.013$ and $-0.054$.',
                                   round(min(ACR[r][k]['rho'] for r in _PREWAR
                                             for k in ('W_F', 'W_M')), 2) == 0.23
                                   and round(max(ACR[r][k]['rho'] for r in _PREWAR
                                                 for k in ('W_F', 'W_M')), 2) == 0.51
                                   and round(_BR['W_F']['rho'], 3) == 0.013
                                   and round(_BR['W_M']['rho'], 3) == -0.054,
                                   f"{min(ACR[r][k]['rho'] for r in _PREWAR for k in ('W_F','W_M')):.3f}"
                                   f"-{max(ACR[r][k]['rho'] for r in _PREWAR for k in ('W_F','W_M')):.3f}, "
                                   f"burden {_BR['W_F']['rho']:+.4f} {_BR['W_M']['rho']:+.4f}"),
 ('any association above $0.09$ in absolute value, and the one that does exclude\n'
  'zero, $-0.054$ for installations, is negative',
                                   max(abs(b) for k in ('W_C', 'W_F', 'W_M')
                                       for b in _BR[k]['ci']) <= 0.09
                                   and max(_BR['W_M']['ci']) < 0
                                   and _BR['W_C']['ci'][0] < 0 < _BR['W_C']['ci'][1]
                                   and _BR['W_F']['ci'][0] < 0 < _BR['W_F']['ci'][1],
                                   f"widest |bound| "
                                   f"{max(abs(b) for k in ('W_C','W_F','W_M') for b in _BR[k]['ci']):.3f};"
                                   f" W_M CI {_BR['W_M']['ci']}"),
 ('and they turn negative when deaths are conditioned\non enlistment.',
                                   all(BENL[k]['rho'] < 0 for k in ('W_C', 'W_F', 'W_M')),
                                   ' '.join(f"{BENL[k]['rho']:+.4f}" for k in ('W_C', 'W_F', 'W_M'))),
 ('Coverage tells the same story: 98.2 percent of counties recorded\n'
  'a death while 48.5 percent received any major contract.',
                                   round(_DEATHPCT, 1) == 98.2 and round(_CONTPCT, 1) == 48.5,
                                   f"{_DEATHPCT:.2f}% deaths, {_CONTPCT:.2f}% contracts"),
 ('employment by more, left manufacturing employment where it found it, and lowered\n'
  'homeownership by seven and a half points.',
                                   me['log population 1970']['coef'] > pe['log population 1970']['matched']
                                   and me['log total employment 1970']['coef'] >
                                       pe['log total employment 1970']['matched']
                                   and me['log manufacturing employment 1970']['p'] > 0.05
                                   and round(me['homeownership 1970']['coef'], 1) == -7.5,
                                   f"pop {me['log population 1970']['coef']:.3f} vs "
                                   f"{pe['log population 1970']['matched']:.3f}; emp "
                                   f"{me['log total employment 1970']['coef']:.3f} vs "
                                   f"{pe['log total employment 1970']['matched']:.3f}; own "
                                   f"{me['homeownership 1970']['coef']:.4f}"),

 # ================= SECTION 6 (rhetoric) =====================================
 # This section carried no checks at all before this lane.
 ('Nationally, 42.9 Army and\nArmy Air Forces enlistees died per thousand who served.',
                                   round(ex['fatality_rate_national'], 1) == 42.9,
                                   fmt(ex['fatality_rate_national'], 2)),
 ('ninetieth percentile of that rate was $3.58$ times the tenth.',
                                   round(ex['BA_p90_p10_ratio'], 2) == 3.58,
                                   fmt(ex['BA_p90_p10_ratio'], 3)),
 ('Some 1{,}553\ncounties---more than half of those that lost men---received no major war contract of\nany kind.',
                                   o['counties_deaths_no_contracts'] == 1553
                                   and o['counties_deaths_no_contracts'] >
                                       0.5 * int((m.deaths_all.fillna(0) > 0).sum()),
                                   f"{o['counties_deaths_no_contracts']} of "
                                   f"{int((m.deaths_all.fillna(0)>0).sum())} counties that lost men"),
 ('per-capita rank correlations of\n'
  '$-0.026$, $+0.013$ and $-0.054$ against prewar loadings of $0.23$ to $0.69$, and\n'
  'a coverage asymmetry in which 98.2 percent of counties recorded a death and 48.5\n'
  'percent received a major contract.',
                                   round(_BR['W_C']['rho'], 3) == -0.026
                                   and round(_BR['W_F']['rho'], 3) == 0.013
                                   and round(_BR['W_M']['rho'], 3) == -0.054
                                   and round(min(ACR[r][k]['rho'] for r in _PREWAR
                                                 for k in ('W_C', 'W_F', 'W_M')), 2) == 0.23
                                   and round(max(ACR[r][k]['rho'] for r in _PREWAR
                                                 for k in ('W_C', 'W_F', 'W_M')), 2) == 0.69
                                   and round(_DEATHPCT, 1) == 98.2 and round(_CONTPCT, 1) == 48.5,
                                   f"{_BR['W_C']['rho']:+.4f} {_BR['W_F']['rho']:+.4f} "
                                   f"{_BR['W_M']['rho']:+.4f}; loadings "
                                   f"{min(ACR[r][k]['rho'] for r in _PREWAR for k in ('W_C','W_F','W_M')):.3f}"
                                   f"-{max(ACR[r][k]['rho'] for r in _PREWAR for k in ('W_C','W_F','W_M')):.3f}"),
 # The Shapley share, not the one-at-a-time share: the two differ by 12 points
 # and the one-at-a-time pair does not sum to one.
 ('relative to population --- 85 percent of the shortfall ---',
                                   round(100 * ACD['shapley_contract_share']) == 85
                                   and abs(ACD['shapley_contract_share']
                                           + ACD['shapley_death_share'] - 1) < 1e-6,
                                   f"{100*ACD['shapley_contract_share']:.1f}% "
                                   f"(one-at-a-time {100*ACD['share_from_contract_concentration']:.1f}%)"),
 ('added employment of every other kind and a measured homeownership rate lower by\n'
  'seven and a half points',
                                   round(me['homeownership 1970']['coef'], 1) == -7.5
                                   and me['log total employment 1970']['p'] < 0.05
                                   and me['log manufacturing employment 1970']['p'] > 0.05,
                                   f"own {me['homeownership 1970']['coef']:.4f}; mfg-emp p="
                                   f"{me['log manufacturing employment 1970']['p']}"),

 # ================= CONCLUSION ===============================================
 ('overlap runs from $0.22$ to $0.59$. The two capital programs are the weakly\n'
  'related pair, correlating at $\\rho = 0.31$; contracts and plant, both of which\n'
  'followed existing industry, are the exception at $\\rho = 0.62$.',
                                   round(min(_WA), 2) == 0.22 and round(max(_WA), 2) == 0.59
                                   and round(_WRHO['W_F x W_M'], 2) == 0.31
                                   and _WRHO['W_F x W_M'] == min(_WRHO.values())
                                   and round(_WRHO['W_C x W_F'], 2) == 0.62
                                   and _WRHO['W_C x W_F'] == max(_WRHO.values()),
                                   f"A {min(_WA):.4f}-{max(_WA):.4f}; rho "
                                   + ' '.join(f"{k}={v:.4f}" for k, v in _WRHO.items())),
 ('Of 2{,}973 counties, 118 received a large public\n'
  'plant and 56 a top-decile installation, and only two received both --- against\n'
  '2.2 expected if the two programs had been allocated independently of one\n'
  'another.',
                                   MDS['sample_n'] == 2973 and MDS['sample_treated'] == 118
                                   and mm['n_treated_predrop'] == 56 and BOTH_TREATED == 2
                                   and round(EXP_BOTH, 1) == 2.2,
                                   f"{MDS['sample_n']}/{MDS['sample_treated']}/"
                                   f"{mm['n_treated_predrop']}; both={BOTH_TREATED}, "
                                   f"expected {EXP_BOTH:.3f}"),
 ('Measured per resident on the same\n'
  '3{,}073 counties, contract dollars correlate with the 1940 manufacturing share\n'
  'at $+0.693$ and with fatal burden at $-0.026$; the other two allocations load on\n'
  'prewar characteristics at $+0.23$ to $+0.51$ and on burden at $+0.013$ and\n'
  '$-0.054$.',
                                   all(ACR[r][k]['n'] == 3073 for r in _PREWAR
                                       for k in ('W_C', 'W_F', 'W_M'))
                                   and round(ACR['1940 manufacturing share']['W_C']['rho'], 3) == 0.693
                                   and round(_BR['W_C']['rho'], 3) == -0.026
                                   and round(min(ACR[r][k]['rho'] for r in _PREWAR
                                                 for k in ('W_F', 'W_M')), 2) == 0.23
                                   and round(max(ACR[r][k]['rho'] for r in _PREWAR
                                                 for k in ('W_F', 'W_M')), 2) == 0.51
                                   and round(_BR['W_F']['rho'], 3) == 0.013
                                   and round(_BR['W_M']['rho'], 3) == -0.054,
                                   f"n={ACR['1940 manufacturing share']['W_C']['n']}, "
                                   f"mfg {ACR['1940 manufacturing share']['W_C']['rho']}, "
                                   f"burden {_BR['W_C']['rho']:+.4f}"),
 ('size these exclude any association above $0.09$ in absolute value. Coverage says the same: 98.2 percent\n'
  'of counties recorded a death while 48.5 percent received any major contract, and\n'
  '1{,}553 counties lost men and received no major war contract at all.',
                                   max(abs(b) for k in ('W_C', 'W_F', 'W_M')
                                       for b in _BR[k]['ci']) <= 0.09
                                   and round(_DEATHPCT, 1) == 98.2 and round(_CONTPCT, 1) == 48.5
                                   and o['counties_deaths_no_contracts'] == 1553,
                                   f"widest |bound| "
                                   f"{max(abs(b) for k in ('W_C','W_F','W_M') for b in _BR[k]['ci']):.3f}; "
                                   f"{_DEATHPCT:.2f}/{_CONTPCT:.2f}; "
                                   f"{o['counties_deaths_no_contracts']}"),
 ('volunteer status from 7.2 million individual enlistment records, and test score\n'
  'from the 5 percent of them that carry one --- leaves all three\n'
  'negative, and makes two of the three more so.',
                                   round(COMP_ENL / 1e6, 1) == 7.2 and COMP_N == co['n']
                                   and all(co[k]['rho_adjusted'] < 0
                                           for k in ('contracts', 'war plant', 'military'))
                                   and sum(co[k]['rho_adjusted'] < co[k]['rho_raw']
                                           for k in ('contracts', 'war plant', 'military')) == 2,
                                   f"{COMP_ENL/1e6:.3f}M over {COMP_N} counties; adj "
                                   + ' '.join(f"{co[k]['rho_adjusted']:+.4f}"
                                              for k in ('contracts', 'war plant', 'military'))),
 ('lowered measured homeownership by seven and a half points. The two allocations did not\n'
  'have opposite effects on manufacturing',
                                   round(me['homeownership 1970']['coef'], 1) == -7.5
                                   and me['log manufacturing employment 1970']['p'] > 0.05
                                   and pe['log manufacturing employment 1970']['p'] < 0.05,
                                   f"own {me['homeownership 1970']['coef']:.4f}; mil mfg-emp p="
                                   f"{me['log manufacturing employment 1970']['p']}, plant p="
                                   f"{pe['log manufacturing employment 1970']['p']}"),
 ('Both designs pass placebo tests on pre-treatment outcomes',
                                   all(r['p'] > 0.05 for r in mp['placebo'])
                                   and all(r['p'] > 0.05 for r in mm['placebo']),
                                   f"min plant placebo p={min(r['p'] for r in mp['placebo'])}, "
                                   f"min military p={min(r['p'] for r in mm['placebo'])}"),
 # PROPOSED CORRECTION -- see the defect note.  The military design leaves ONE
 # standardized difference past 0.10 (1930--40 population growth, 0.106), which
 # Section 5.8 discloses as "imbalance falls from eight of nine covariates to
 # one" but the conclusion does not.  Unlike latitude and the Black population
 # share, that covariate does describe economic structure, so the clause
 # "balance on every prewar covariate that describes economic structure" is not
 # true of both designs.  This anchor pins the corrected sentence and reports
 # NOT IN TEXT until the manuscript is fixed.
 ('the military design leaves one, 1930--40 population\ngrowth at $0.106$',
                                   sum(abs(b['matched']) > 0.10 for b in mm['balance']) == 1
                                   and [b['var'] for b in mm['balance']
                                        if abs(b['matched']) > 0.10] == ['popgrowth_3040']
                                   and round([b['matched'] for b in mm['balance']
                                              if b['var'] == 'popgrowth_3040'][0], 3) == 0.106
                                   and sum(abs(b['raw']) > 0.10 for b in mm['balance']) == 8,
                                   ' '.join(f"{b['var']}={b['matched']:+.4f}" for b in mm['balance']
                                            if abs(b['matched']) > 0.10)
                                   + f" (raw imbalanced {sum(abs(b['raw'])>0.10 for b in mm['balance'])})"),
 ('The plant design leaves two of nine standardized\n'
  'differences just past the conventional $0.10$ threshold, latitude and the 1940\n'
  'Black population share',
                                   len(mp['balance']) == 9 and mp['imbalanced_matched'] == 2
                                   and sorted(b['var'] for b in mp['balance']
                                              if abs(b['smd_matched']) > 0.10)
                                       == ['LATITUDE', 'blackshare1940']
                                   and all(abs(b['smd_matched']) < 0.15 for b in mp['balance']),
                                   ' '.join(f"{b['var']}={b['smd_matched']:+.4f}"
                                            for b in mp['balance'] if abs(b['smd_matched']) > 0.10)),
 ('survive the most demanding available comparison --- treated counties against\n'
  'their own untreated neighbors, sharing a labor market, a climate, and a state.',
                                   all(aj[k]['p'] < 0.05 for k in
                                       ('log pop 1970', 'mfg share 1970', 'log income 1970'))
                                   and aj['log pop 1970']['n_treated'] == 111,
                                   ' '.join(f"{k} p={aj[k]['p']}" for k in
                                            ('log pop 1970', 'mfg share 1970', 'log income 1970'))),
 # "puts it at zero" is a claim about significance, which _own() strips, so the
 # stars are read straight off the typeset row.
 ('and the continuous specification of\nTable \\ref{tab:main} puts it at zero',
                                   '^{*' not in [c for c in
                                       [l for l in _t6 if l.startswith('War plant')][0].split('&')][7]
                                   and abs(T6['War plant']) < abs(pe['homeownership 1970']['matched']),
                                   f"Table 4 col 7, War plant = {T6['War plant']} (no stars)"),
 ('The point estimate is\n'
  '$+0.94$ points against matched controls ($p = 0.12$) and $+0.40$ against\n'
  'adjacent counties ($p = 0.48$)',
                                   round(pe['homeownership 1970']['matched'], 2) == 0.94
                                   and round(pe['homeownership 1970']['p'], 2) == 0.12
                                   and round(aj['homeownership 1970']['coef'], 2) == 0.40
                                   and round(aj['homeownership 1970']['p'], 2) == 0.48,
                                   f"{pe['homeownership 1970']['matched']:.4f} "
                                   f"p={pe['homeownership 1970']['p']}; "
                                   f"{aj['homeownership 1970']['coef']:.4f} "
                                   f"p={aj['homeownership 1970']['p']}"),
 ('smaller under the neighbor comparison --- 4.6 percent against 7.3 percent ---\n'
  'so roughly a third of the national-pool estimate is regional rather than local.',
                                   round(100 * (math.exp(aj['log income 1970']['coef']) - 1), 1) == 4.6
                                   and round(100 * (math.exp(pe['log family income 1970']['matched']) - 1),
                                             1) == 7.3
                                   and 0.28 < 1 - aj['log income 1970']['coef'] \
                                        / pe['log family income 1970']['matched'] < 0.42,
                                   f"{100*(math.exp(aj['log income 1970']['coef'])-1):.2f}% vs "
                                   f"{100*(math.exp(pe['log family income 1970']['matched'])-1):.2f}%; "
                                   f"shrink {1-aj['log income 1970']['coef']/pe['log family income 1970']['matched']:.3f}"),
 ('randomization inference on 500\npermutations returns $p \\leq 0.004$. But the treated group is 52 counties',
                                   all(r['n_draws'] == 500 for r in am['randomization'])
                                   and max(r['perm_p'] for r in am['randomization']) <= 0.004
                                   and mm['n_treated'] == 52,
                                   f"{len(am['randomization'])} outcomes, max perm p="
                                   f"{max(r['perm_p'] for r in am['randomization'])}, "
                                   f"n_treated={mm['n_treated']}"),
 # PROPOSED CORRECTION -- see the defect note.  Section 5.8 (line 1235-1240)
 # states that the manufacturing-share coefficient is "flat rather than
 # monotone" and that only "two of the three outcomes" show the dose-response
 # pattern; audit_military.json confirms it (-9.09, -4.72, -4.31, -4.61, -4.18).
 # The conclusion currently reads "with a monotone dose--response", which the
 # results section disowns.  This anchor pins the corrected sentence and will
 # report NOT IN TEXT until the manuscript is fixed.
 ('definitions with a monotone dose--response in two of the three outcomes',
                                   [r['own rate']['coef'] for r in am['thresholds']]
                                       == sorted((r['own rate']['coef'] for r in am['thresholds']))
                                   and [r['log pop']['coef'] for r in am['thresholds']]
                                       == sorted((r['log pop']['coef'] for r in am['thresholds']),
                                                 reverse=True)
                                   and [r['mfg share']['coef'] for r in am['thresholds']]
                                       != sorted((r['mfg share']['coef'] for r in am['thresholds'])),
                                   'mfg share ' + ' '.join(f"{r['mfg share']['coef']:.4f}"
                                                           for r in am['thresholds'])
                                   + f" then {am['absolute']['mfg share']['coef']:.4f}"),
 ('The natural instrument --- the 1938 Industrial Mobilization Plan --- passes the\n'
  'first-stage $F$ test, is weak on partial $R^2$, and fails its exclusion\n'
  'restriction outright',
                                   SSI['F'] > imp['thresholds']['F']
                                   and SSI['partial_r2'] < imp['thresholds']['partial_r2']
                                   and min(SSI['placebo'].values()) < imp['thresholds']['placebo_p'],
                                   f"F={SSI['F']} partial R2={SSI['partial_r2']} "
                                   f"min placebo p={min(SSI['placebo'].values())}"),
 ('Of nine ways of building the instrument from that source, from\n'
  'every allocated establishment to the aeronautical branch alone, none clears\n'
  'relevance and exclusion together.',
                                   imp['n_specs'] == 9 and len(imp['specifications']) == 9
                                   and imp['n_usable'] == 0
                                   and not any(s['usable'] for s in imp['specifications'])
                                   and imp['specifications'][0]['var'] == 'imp_total'
                                   and any(s['var'] == 'imp_aero' for s in imp['specifications']),
                                   f"{imp['n_specs']} specs, {imp['n_usable']} usable"),
 ('it is the stronger instrument, at $F = 45.1$ against $19.7$,\n'
  'and fails the same three placebos at $p<0.001$.',
                                   round(SSA['F'], 1) == 45.1 and round(SSI['F'], 1) == 19.7
                                   and SSA['F'] > SSI['F']
                                   and SSA['partial_r2'] > SSI['partial_r2']
                                   and sum(p < 0.001 for p in SSA['placebo'].values()) == 3,
                                   f"F {SSA['F']} vs {SSI['F']}; partial R2 "
                                   f"{SSA['partial_r2']} vs {SSI['partial_r2']}; placebo "
                                   + ' '.join(f"{v}" for v in SSA['placebo'].values())),
 ('27.9 percent of aircraft dollars and 77.2 percent of ammunition dollars went to\n'
  'counties with no prewar plant of that kind',
                                   round(100 * GF['aircraft']['greenfield_dollar_share'], 1) == 27.9
                                   and round(100 * GF['ammunition']['greenfield_dollar_share'], 1) == 77.2,
                                   f"{100*GF['aircraft']['greenfield_dollar_share']:.2f}% / "
                                   f"{100*GF['ammunition']['greenfield_dollar_share']:.2f}%"),
]
