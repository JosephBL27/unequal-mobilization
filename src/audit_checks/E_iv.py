from functools import lru_cache as _lru
# ---------------------------------------------------------------------------
# LANE E_iv -- Sections 5.4 (Postwar divergence), 5.6 (What the estimates can
# and cannot support) and 5.9 (An instrument, and why it does not work).
#
# HOW TO SPLICE.  The PREAMBLE block below goes immediately above `CHECKS=[`
# in src/audit_paper_vs_data.py (it only reads artifacts that block already
# loads, plus regression_results.json's `interactions` key, master_panel_iv
# .parquet, and the Haines 1920 file).  The list literal LANE_E_IV then splices
# straight into CHECKS.
#
# Every condition compares against a value read from a stored artifact or
# recomputed from source, never against a literal, and every tolerance is no
# wider than the precision the manuscript prints.
# ---------------------------------------------------------------------------

# ================================ PREAMBLE =================================
import pyreadstat                                   # for the 1920 Haines file

# equation (8)'s interactions -- regression_results.json's fourth key, which
# nothing in the audit read even though Section 5.4 quotes two of its cells.
RI = {r['outcome']: r for r in
      json.loads((AN/'regression_results.json').read_text())['interactions']}

# The tenth-to-ninetieth spread of B_A, on the same screen the interaction
# regression applies, and on the contracted subsample.  Section 5.4's "roughly
# 0.6" is only reachable on the second of these; the sentence names neither.
@_lru(maxsize=None)
def _BA_spread():
    B = pd.to_numeric(m.B_A, errors='coerce').where(m.valid_BA.fillna(False))
    full = float(B.quantile(.9) - B.quantile(.1))
    Bc = B[pd.to_numeric(m.contract_k, errors='coerce').fillna(0) > 0]
    return full, float(Bc.quantile(.9) - Bc.quantile(.1))
BA_SPREAD_ALL, BA_SPREAD_CONTRACTED = _BA_spread()

# Conley: the significance bucket each row lands in under each SE, so that
# "leaves every sign and significance level in place" is tested rather than
# asserted.  Buckets are the ones the tables star: 10 / 5 / 1 percent.
def _sig_bucket(t):
    t = abs(t)
    return 3 if t >= 2.576 else 2 if t >= 1.96 else 1 if t >= 1.645 else 0
@_lru(maxsize=None)
def _conley_buckets():
    out = []
    for blk in rb['conley']:
        for k in ('W_C','W_F','W_M','B'):
            c = blk[k]
            out.append((_sig_bucket(c['coef']/c['se_cluster']),
                        _sig_bucket(c['coef']/c['se_conley']),
                        c['coef']))
    return out
CONLEY_BUCKETS = _conley_buckets()

# Dropping the twenty largest recipients: the largest proportional move, and
# whether any coefficient changed sign.  robustness.json stores no p-values,
# so the "no change in significance" half of the sentence is NOT testable from
# the artifact -- see the note in the lane report.
@_lru(maxsize=None)
def _drop20():
    mx, flip = 0.0, 0
    for blk in rb['drop_top20']:
        for k in ('W_C','W_F','W_M','B'):
            c = blk[k]
            mx = max(mx, abs(c['drop20']-c['full'])/abs(c['full']))
            flip += (c['drop20']*c['full'] <= 0)
    return mx, flip
DROP20_MAXPCT, DROP20_FLIPS = _drop20()

# Illinois: the state's county count and how many carry a recorded death.
IL_N       = int(((m.fips//1000) == 17).sum())
IL_WITH_D  = int((((m.fips//1000) == 17) & (m.deaths_all.fillna(0) > 0)).sum())

# The 1920 pre-trend footnote.  Recomputed from the Haines part-24 file the way
# robustness.py builds it, because robustness.json stores only the regression
# and none of the three coverage figures the footnote quotes.
@_lru(maxsize=None)
def _haines1920():
    h, _ = pyreadstat.read_dta(
        str(ROOT/'data/raw/haines_icpsr2896/02896-0024-Data.dta'),
        usecols=['county','fips','totpop'])
    h['fips'] = pd.to_numeric(h.fips, errors='coerce')
    h = h[(pd.to_numeric(h.county, errors='coerce') != 0) & h.fips.notna()].copy()
    h['fips'] = h.fips.astype(int)
    _ic = pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
    _icm = dict(zip(_ic.city_fips.astype(int), _ic.parent_fips.astype(int)))
    h['fips'] = h.fips.map(lambda f: _icm.get(f, f))
    h = h[~(h.fips//1000).isin([2,15,60,66,69,72,78])]
    h = h.groupby('fips', as_index=False).totpop.sum().rename(columns={'totpop':'pop1920'})
    d = m.merge(h, on='fips', how='left')
    d['pop1920'] = pd.to_numeric(d.pop1920, errors='coerce')
    nomatch = d[d.pop1920.isna()]
    # a county can carry a Haines row whose population is missing; it then has
    # no usable 1920 figure without having failed the merge.
    usable = np.log(pd.to_numeric(d.pop1930, errors='coerce').replace(0, np.nan)
                    / d.pop1920.replace(0, np.nan)).notna()
    return {'n_merged':      int(d.pop1920.notna().sum()),
            'n_nomatch':     int(len(nomatch)),
            'n_usable':      int(usable.sum()),
            'n_no_usable':   int(len(d) - usable.sum()),
            'pop1920_bn':    float(d.pop1920.sum()/1e6),
            'nomatch_pop_share': float(100*nomatch.pop1940.sum()/d.pop1940.sum())}
H20 = _haines1920()

# The IMP instrument's own coverage, from the panel build_instruments.py writes.
# Section 5.9's opening four counts print to stdout and are stored nowhere.
_ivp = pd.read_parquet(AN/'master_panel_iv.parquet',
                       columns=['fips','imp_fac','mil_prewar'])
IMPCOV = {'facilities': int(round(float(_ivp.imp_fac.sum()))),
          'fac_counties': int((_ivp.imp_fac > 0).sum()),
          'mil_sites': int(round(float(_ivp.mil_prewar.sum()))),
          'mil_counties': int((_ivp.mil_prewar > 0).sum())}

IVP  = {r['outcome']: r for r in ivv['placebo']}      # IMP exclusion placebos
FS   = {r['spec']: r for r in iv['first_stage']}
CLF  = SS['classifier']
# ============================== END PREAMBLE ===============================


CHECKS_E_IV = [

 # ---- 5.4 Postwar divergence ---------------------------------------------
 # The two extensive-margin coefficients were checked; neither p-value was.
 ('with a manufacturing share $1.70$ points higher in 1970 ($p = 0.001$), merely\n'
  'hosting a military installation with $3.72$ points lower ($p < 0.001$).',
                                    abs(rb['extensive']['any_F']['coef']-1.70438)<0.005 and
                                    abs(rb['extensive']['any_F']['p']-0.001)<0.0005 and
                                    abs(rb['extensive']['any_M']['coef']+3.72484)<0.005 and
                                    rb['extensive']['any_M']['p']<0.001,
                                    f"F {rb['extensive']['any_F']['coef']:.3f} p={rb['extensive']['any_F']['p']} / "
                                    f"M {rb['extensive']['any_M']['coef']:.3f} p={rb['extensive']['any_M']['p']}"),

 # theta_C and theta_F reached a table in September and no check followed them
 # there.  Section 4 calls these "the paper's distinctive parameters".
 ('Three of the four pairs are null. The exception is\n'
  'the 1970 manufacturing share, where $\\theta_C = +0.0115$ ($p < 0.001$) and\n'
  '$\\theta_F = +0.0036$ ($p = 0.10$)',
                                    abs(RI['manufacturing share 1970']['theta_C']-0.01154)<0.00005 and
                                    RI['manufacturing share 1970']['p_C']<0.001 and
                                    abs(RI['manufacturing share 1970']['theta_F']-0.00355)<0.00005 and
                                    abs(RI['manufacturing share 1970']['p_F']-0.10)<0.005 and
                                    sum(1 for k,r in RI.items()
                                        if k!='manufacturing share 1970'
                                        and r['p_C']>=0.10 and r['p_F']>=0.10)==3,
                                    f"theta_C={RI['manufacturing share 1970']['theta_C']} p={RI['manufacturing share 1970']['p_C']} "
                                    f"theta_F={RI['manufacturing share 1970']['theta_F']} p={RI['manufacturing share 1970']['p_F']}; "
                                    f"{sum(1 for k,r in RI.items() if k!='manufacturing share 1970' and r['p_C']>=0.10 and r['p_F']>=0.10)} null pairs"),

 # The interaction table must not contradict the sentence pointing at it.
 ('$\\theta_C = +0.0115$ ($p < 0.001$) and\n$\\theta_F = +0.0036$ ($p = 0.10$)',
                                    (lambda R: abs(round(R['theta_C'],4)-0.0115)<1e-9 and
                                               abs(round(R['theta_F'],4)-0.0036)<1e-9
                                    )(RI['manufacturing share 1970']),
                                    f"{RI['manufacturing share 1970']['theta_C']:.4f} / "
                                    f"{RI['manufacturing share 1970']['theta_F']:.4f}"),

 # DEFECT -- this check FAILS on the manuscript as it stands.  The p10-p90
 # spread of B_A over the estimation sample is 72.05, so theta_C times that
 # spread is 0.83, not 0.6.  0.6 is the contracted-county spread (51.7).  The
 # sentence names no base and no artifact stores either number.  Fix the prose
 # to 0.83, or name the base; then this check pins whichever is chosen.
 ('moving across the tenth-to-ninetieth range of\n'
  '$B_i^{A}$ among counties that received a contract adds roughly $0.6$ to a main\n'
  'effect of $0.33$',
                                    abs(RI['manufacturing share 1970']['theta_C']*BA_SPREAD_CONTRACTED-0.6)<0.05 and
                                    abs(_t4('Contracts',4)-0.3325)<0.005,
                                    f"theta_C x p10-p90 = {RI['manufacturing share 1970']['theta_C']*BA_SPREAD_ALL:.3f} "
                                    f"(all counties, spread {BA_SPREAD_ALL:.1f}); "
                                    f"{RI['manufacturing share 1970']['theta_C']*BA_SPREAD_CONTRACTED:.3f} "
                                    f"(contracted only, spread {BA_SPREAD_CONTRACTED:.1f}); "
                                    f"main effect {_t4('Contracts',4)}"),

 # ---- 5.6 Conley, drop-top-20, Illinois -----------------------------------
 ('Conley kernel at 200 kilometers leave every sign and significance level in place',
                                    all(a==b and c!=0 for a,b,c in CONLEY_BUCKETS) and
                                    len(CONLEY_BUCKETS)==8,
                                    f"{sum(1 for a,b,_ in CONLEY_BUCKETS if a==b)}/{len(CONLEY_BUCKETS)} "
                                    f"rows keep their significance bucket"),

 # The two exceptions, at the precision the footnote prints, and read from the
 # artifact rather than from the typeset cell (_conley() already asserts the
 # two agree).
 ('where the Conley error is 0.0042 against 0.0034 and the $t$ statistic\n'
  'is still 8.25, and war plant on the 1970 manufacturing share, at 0.0873 against\n'
  '0.0829 and $t = 3.26$.',
                                    (lambda P,M: abs(round(P['W_C']['se_conley'],4)-0.0042)<1e-9 and
                                                 abs(round(P['W_C']['se_cluster'],4)-0.0034)<1e-9 and
                                                 abs(round(P['W_C']['t_conley'],2)-8.25)<1e-9 and
                                                 abs(round(M['W_F']['se_conley'],4)-0.0873)<1e-9 and
                                                 abs(round(M['W_F']['se_cluster'],4)-0.0829)<1e-9 and
                                                 abs(round(M['W_F']['t_conley'],2)-3.26)<1e-9 and
                                                 P['W_C']['se_conley']>P['W_C']['se_cluster'] and
                                                 M['W_F']['se_conley']>M['W_F']['se_cluster']
                                    )(rb['conley'][0], rb['conley'][1]),
                                    f"pop W_C {rb['conley'][0]['W_C']['se_conley']} vs {rb['conley'][0]['W_C']['se_cluster']} "
                                    f"t={rb['conley'][0]['W_C']['t_conley']}; "
                                    f"mfg W_F {rb['conley'][1]['W_F']['se_conley']} vs {rb['conley'][1]['W_F']['se_cluster']} "
                                    f"t={rb['conley'][1]['W_F']['t_conley']}"),

 ('moves no coefficient by more than\nfive percent of its own value',
                                    DROP20_MAXPCT<0.05 and DROP20_FLIPS==0,
                                    f"largest move {100*DROP20_MAXPCT:.2f}% of own value, {DROP20_FLIPS} sign flips"),

 ('where 80 of 102 counties\nappear',
                                    IL_WITH_D==80 and IL_N==102 and
                                    IL['n_full']-IL['n_noIL']==102,
                                    f"{IL_WITH_D} of {IL_N} Illinois counties carry a death; "
                                    f"panel drop {IL['n_full']-IL['n_noIL']}"),

 # ---- 5.6 the 1920 pre-trend ---------------------------------------------
 ('contracts enter at $+0.0004$ ($p = 0.85$), plant at\n'
  '$+0.0044$ ($p = 0.26$), installations at $+0.0008$ ($p = 0.85$), and fatal burden\n'
  'at $-0.0004$ ($p = 0.81$), on the 3{,}041 counties whose 1920 population can be\nmatched.',
                                    (lambda P: all(abs(round(P['coef'][k],4)-v)<1e-9 for k,v in
                                                   [('W_C',0.0004),('W_F',0.0044),('W_M',0.0008),('B',-0.0004)])
                                               and all(abs(round(P['p'][k],2)-v)<1e-9 for k,v in
                                                   [('W_C',0.85),('W_F',0.26),('W_M',0.85),('B',0.81)])
                                               and P['n']==3041
                                    )([r for r in rb['pretrends'] if r['outcome']=='log pop growth 1920->1930'][0]),
                                    f"{[r for r in rb['pretrends'] if r['outcome']=='log pop growth 1920->1930'][0]['coef']} "
                                    f"{[r for r in rb['pretrends'] if r['outcome']=='log pop growth 1920->1930'][0]['p']} "
                                    f"n={[r for r in rb['pretrends'] if r['outcome']=='log pop growth 1920->1930'][0]['n']}"),

 # DEFECT -- this check FAILS as written.  31 panel counties have no Haines
 # part-24 row; the 32nd (Armstrong Co., SD, 46001) matches a row whose 1920
 # population is missing, so it did not "fail to match" and was not "created
 # after 1920".  None of the three coverage figures has a producing script.
 ('against a 1920 continental census of 105.7 million; the thirty-one counties that\n'
  'fail to match were created after 1920, and one further county lacks a usable 1920\n'
  'figure. Together they hold 0.14 percent of 1940 population.',
                                    abs(H20['pop1920_bn']-105.7)<0.05 and
                                    H20['n_nomatch']==31 and H20['n_no_usable']==32 and
                                    abs(H20['nomatch_pop_share']-0.14)<0.005,
                                    f"{H20['pop1920_bn']:.1f}M over {H20['n_merged']} merged; "
                                    f"{H20['n_nomatch']} fail to match, {H20['n_no_usable']} lack a usable "
                                    f"1920 figure, {H20['nomatch_pop_share']:.3f}% of 1940 population"),

 # DEFECT -- this check FAILS as written.  Table tab:pretrends stars W^M on the
 # 1940 manufacturing share at -0.0014***, so installations predict the prewar
 # manufacturing share too, with the opposite sign.  The sentence names only
 # contracts, and the sentence after it generalises to "already industrial".
 ('yet contracts and\nmilitary installations both predict 1930--40 population growth, and both predict\n'
  'the prewar manufacturing share --- contracts positively and installations\n'
  'negatively',
                                    (lambda G,S: G['p']['W_C']<0.05 and G['p']['W_M']<0.05 and
                                                 G['p']['W_F']>=0.05 and
                                                 S['p']['W_C']<0.05 and S['p']['W_M']<0.05 and
                                                 S['coef']['W_C']>0 and S['coef']['W_M']<0
                                    )([r for r in rb['pretrends'] if r['outcome']=='log pop growth 1930->1940'][0],
                                      [r for r in rb['pretrends'] if r['outcome']=='mfg share 1940 (pre-war level)'][0]),
                                    "mfg share 1940 p: " +
                                    str([r for r in rb['pretrends'] if r['outcome']=='mfg share 1940 (pre-war level)'][0]['p']) +
                                    "; coef " +
                                    str([r for r in rb['pretrends'] if r['outcome']=='mfg share 1940 (pre-war level)'][0]['coef'])),

 # ---- 5.9 the instrument --------------------------------------------------
 # Four counts that build_instruments.py prints to stdout and stores nowhere.
 ('I recover 8{,}810 allocated facilities across 833 counties and 529\n'
  'prewar military sites across 133.',
                                    IMPCOV=={'facilities':8810,'fac_counties':833,
                                             'mil_sites':529,'mil_counties':133},
                                    f"{IMPCOV['facilities']:,} facilities / {IMPCOV['fac_counties']} counties; "
                                    f"{IMPCOV['mil_sites']} sites / {IMPCOV['mil_counties']} counties"),

 # 63.6 and 18.9 were checked; the first of the three never was.
 ('$F$ statistics of 23.5 for contracts on allocated facilities',
                                    abs(FS['contracts ~ IMP facilities']['F']-23.471)<0.05 and
                                    abs(round(FS['contracts ~ IMP facilities']['F'],1)-23.5)<1e-9,
                                    fmt(FS['contracts ~ IMP facilities']['F'],3)),

 # The exclusion placebo, in the three directions the paragraph asserts.
 ('The industrial allocation is strongly related to the 1940\n'
  'manufacturing share ($p < 0.001$) and the 1940 urban share ($p < 0.001$); so are\n'
  'the prewar bases. It is unrelated to 1930--40 population growth',
                                    IVP['manufacturing share 1940']['imp_p']<0.001 and
                                    IVP['urban share 1940']['imp_p']<0.001 and
                                    IVP['manufacturing share 1940']['mil_p']<0.001 and
                                    IVP['urban share 1940']['mil_p']<0.001 and
                                    IVP['log population growth 1930-40']['imp_p']>0.10,
                                    f"imp mfg={IVP['manufacturing share 1940']['imp_p']} "
                                    f"urb={IVP['urban share 1940']['imp_p']} "
                                    f"growth={IVP['log population growth 1930-40']['imp_p']}; "
                                    f"mil mfg={IVP['manufacturing share 1940']['mil_p']} "
                                    f"(coef {IVP['manufacturing share 1940']['mil_coef']}) "
                                    f"urb={IVP['urban share 1940']['mil_p']}"),

 ('they still predict 1940 log population at\n$p < 0.001$',
                                    ISP['Aeronautical branch only']['placebo']['1940 log population']<0.001 and
                                    ISP['Aeronautical and optical branches only']['placebo']['1940 log population']<0.001,
                                    f"aero {ISP['Aeronautical branch only']['placebo']['1940 log population']}, "
                                    f"aero+optic {ISP['Aeronautical and optical branches only']['placebo']['1940 log population']}"),

 ('any allocated facility at a partial $R^2$ of $0.055$, fails all three\n'
  'level placebos at $p < 0.001$',
                                    max(ISP['Any allocated facility (extensive margin)']['placebo'][k]
                                        for k in ('1940 manufacturing share','1940 urban share',
                                                  '1940 log population'))<0.001 and
                                    ISP['Any allocated facility (extensive margin)']['partial_r2']>=0.05 and
                                    sum(1 for s in imp['specifications'] if s['partial_r2']>=0.05)==1,
                                    f"max level placebo p = "
                                    f"{max(ISP['Any allocated facility (extensive margin)']['placebo'][k] for k in ('1940 manufacturing share','1940 urban share','1940 log population'))}; "
                                    f"{sum(1 for s in imp['specifications'] if s['partial_r2']>=0.05)} spec(s) clear 0.05"),

 # REPLACEMENT for the existing check on this anchor.  That one reads
 # abs(PR2['W_M']-0.0125)<0.001 -- a literal no artifact produces, with a
 # tolerance twice the printed precision.  It passes on a stored 0.0133 and
 # would also pass on 0.0116, which prints as 0.012.
 ('is $0.030$ for contracts and\n$0.013$ for military installations',
                                    abs(round(PR2['W_C'],3)-0.030)<1e-9 and
                                    abs(round(PR2['W_M'],3)-0.013)<1e-9 and
                                    max(PR2['W_C'],PR2['W_M'])<0.03,
                                    f"{PR2['W_C']:.4f} / {PR2['W_M']:.4f}"),

 # DEFECT -- this check FAILS as written, and is meant to.  Nothing in src/
 # computes the conditioned specification: shiftshare.json carries only the
 # three shift-share rows and the IMP benchmark, and tabA_shiftshare.tex has no
 # conditioned row.  Reconstructing it (the baseline shift-share plus
 # arcsinh(total 1940 war-related establishments) in the control vector)
 # reproduces the partial R^2 (0.0129 -> 0.013) and the manufacturing-share
 # placebo (0.8691 -> 0.87) exactly, and returns F = 11.29, which prints as
 # 11.3 rather than 11.2.  build_shiftshare.py should evaluate and store the
 # row as SS['shiftshare_conditioned']; this check then pins it.
 ('$F$ falls to $11.3$ and the partial $R^2$ to $0.013$, while the urban\n'
  'share and log population still reject at $p<0.001$',
                                    'shiftshare_conditioned' in SS and
                                    abs(round(SS['shiftshare_conditioned']['F'],1)-11.3)<1e-9 and
                                    abs(round(SS['shiftshare_conditioned']['partial_r2'],3)-0.013)<1e-9 and
                                    abs(round(SS['shiftshare_conditioned']['placebo']['1940 mfg share'],2)-0.87)<1e-9 and
                                    max(SS['shiftshare_conditioned']['placebo'][k] for k in
                                        ('1940 urban share','1940 log population'))<0.001,
                                    ("no producer: shiftshare.json has no 'conditioned' key and "
                                     "tabA_shiftshare.tex has no conditioned row"
                                     if 'shiftshare_conditioned' not in SS else
                                     f"F={SS['shiftshare_conditioned']['F']} r2={SS['shiftshare_conditioned']['partial_r2']} "
                                     f"mfg p={SS['shiftshare_conditioned']['placebo']['1940 mfg share']}")),

 ('and ammunition at \\$14.4 billion contributes $0.0000$',
                                    abs(ROT['ammunition']['national_bn']-14.36)<0.05 and
                                    abs(round(ROT['ammunition']['partial_r2'],4))<1e-9,
                                    f"${ROT['ammunition']['national_bn']}bn r2={ROT['ammunition']['partial_r2']}"),

 ('twenty-one classes recovered from the description carried on every contract',
                                    CLF['n_classes']==21 and len(SS['classes'])==21 and
                                    len(ROT)==21,
                                    f"{CLF['n_classes']} classes, {len(ROT)} in the Rotemberg decomposition"),

 # ---- restatements: the same figures where Section 6 repeats them ---------
 # These are second occurrences.  The existing checks find the Section 5.9
 # sentence and stop, which is exactly how "30.8 percent of aircraft dollars"
 # survived in the conclusion for a week after Section 5.2 was corrected.
 ('at $F = 45.1$ against $19.7$,\nand fails the same three placebos at $p<0.001$',
                                    abs(round(SSA['F'],1)-45.1)<1e-9 and
                                    abs(round(SSI['F'],1)-19.7)<1e-9 and
                                    max(SSA['placebo'][k] for k in
                                        ('1940 mfg share','1940 urban share','1940 log population'))<0.001,
                                    f"{SSA['F']} vs {SSI['F']}, max level placebo "
                                    f"{max(SSA['placebo'][k] for k in ('1940 mfg share','1940 urban share','1940 log population'))}"),

 ('27.9 percent of aircraft dollars and 77.2 percent of ammunition dollars went to\n'
  'counties with no prewar plant of that kind',
                                    abs(round(100*GF['aircraft']['greenfield_dollar_share'],1)-27.9)<1e-9 and
                                    abs(round(100*GF['ammunition']['greenfield_dollar_share'],1)-77.2)<1e-9,
                                    f"{100*GF['aircraft']['greenfield_dollar_share']:.1f} / "
                                    f"{100*GF['ammunition']['greenfield_dollar_share']:.1f}"),
]
