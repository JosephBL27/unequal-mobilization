from functools import lru_cache as _lru
# ---------------------------------------------------------------------------
# LANE B_alloc -- Section 2, Section 5.2 ("Three allocations, not two") and
# Section 5.3 ("Alignment").  Splice CHECKS_B_ALLOC into CHECKS; the PREAMBLE
# block must sit above the CHECKS= list, beside the other helper blocks.
#
# Every condition below reads a stored artifact or recomputes from the panel.
# Three conditions carry a `... not in tex` clause: those are the claims a
# defect report names as wrong, so the check is written for the corrected
# sentence and fails until the correction lands.  When it lands, move the
# retired literal into FORBIDDEN as well.
# ---------------------------------------------------------------------------

# ============================ PREAMBLE =====================================
from scipy.stats import spearmanr as _sp
VALID = json.loads((ROOT/'data/docs/validation.json').read_text())
MAPS  = (ROOT/'src/make_maps.py').read_text()
TGP   = tg['pairwise']; TGC = tg['conditional']['counties']
PN    = AC['poisson_null']
BYY   = BY['years']

@_lru(maxsize=None)
def _geo_tab():
    """tabA_geography.tex as {pair-row-index: (A, JS, rho)}, read from the
    typeset file.  The prose quotes two of these cells; an artifact-only check
    cannot see the table drifting away from the JSON (cf. tabA_milrobust)."""
    out=[]
    for l in (ROOT/'paper/tables/tabA_geography.tex').read_text().splitlines():
        if l.startswith('$W^'):
            c=[x.strip().replace('\\\\','').strip() for x in l.split('&')]
            out.append((c[0], float(c[1]), float(c[2]), float(c[3])))
    return {r[0]: r[1:] for r in out}
GEOT=_geo_tab()

@_lru(maxsize=None)
def _crit_tab():
    """tab_criteria.tex, prewar-characteristic rows only, as a flat list of
    the nine rank correlations the 'roughly 0.4 to 0.7' sentence summarises."""
    v=[]
    for l in (ROOT/'paper/tables/tab_criteria.tex').read_text().splitlines():
        if l.startswith('\\quad 1940'):
            v += [float(c.strip().replace('\\\\','')) for c in l.split('&')[1:4]]
    return v
CRITTAB=_crit_tab()
CRITMIN, CRITMAX = min(CRITTAB), max(CRITTAB)

@_lru(maxsize=None)
def _burden_rank_p():
    """The p-value behind '(p = 0.003)'.  allocation_criteria.json stores rho,
    n and a CI but no p, so the sentence's only numeral had no artifact; this
    recomputes the Spearman test on the same 3,073 counties."""
    P=m.pop1940.replace(0,np.nan); b=1000*m.deaths_all.fillna(0)/P
    out={}
    for k,col in (('W_C','contract_k'),('W_F','fac_public_k'),('W_M','cdb_fac_military')):
        v=m[col].fillna(0)/P; ok=b.notna()&v.notna()
        r=_sp(b[ok],v[ok])
        out[k]=(float(r.statistic), float(r.pvalue), int(ok.sum()))
    return out
BRP=_burden_rank_p()

@_lru(maxsize=None)
def _mob_corrs():
    """Spearman(mobilisation rate, B^civic) and (mobilisation rate, B^A) on the
    2,976-county valid-B^A sample -- the sample analysis_exposure.py uses.  It
    prints both and stores only the second, so the first reached the manuscript
    with no artifact behind it."""
    d=pd.read_parquet(AN/'master_panel_v2.parquet')
    x=pd.read_parquet(AN/'exposure_county.parquet')
    d=d.merge(x[['fips','B_A','mobilization_rate']],on='fips',how='left')
    d['B_civic']=1000*d.deaths_all/d.pop1940.replace(0,np.nan)
    v=d[~((d.mobilization_rate>1)|(d.B_A>300)|d.B_A.isna())]
    return (float(_sp(v.mobilization_rate,v.B_civic,nan_policy='omit').statistic),
            float(_sp(v.mobilization_rate,v.B_A,nan_policy='omit').statistic),
            int(len(v)))
MOB_BCIVIC, MOB_BA, MOB_N = _mob_corrs()

@_lru(maxsize=None)
def _cdb_split():
    """The industrial/military split computed on the County Data Book's OWN two
    facility columns, which is what Section 5.2's sentence describes.  The
    stored counts use W^F (the WPB publicly financed plant measure) instead."""
    d=pd.read_parquet(AN/'master_panel.parquet')
    d=d[d.pop1940>0]
    hi=d.cdb_fac_industrial.fillna(0)>0; hm=d.cdb_fac_military.fillna(0)>0
    return {'any':int((hi|hm).sum()), 'ind_only':int((hi&~hm).sum()),
            'mil_only':int((hm&~hi).sum()), 'both':int((hi&hm).sum()),
            'rho':float(_sp(d.cdb_fac_industrial.fillna(0),
                            d.cdb_fac_military.fillna(0)).statistic)}
CDBS=_cdb_split()
# ========================== END PREAMBLE ===================================

CHECKS_B_ALLOC = [
 # ---- Section 2: the source counts ---------------------------------------
 # VA's published WWII totals are a property of an external publication, not of
 # anything this pipeline builds; presence is all that can be checked here.
 ('291,557 battle deaths and 113,842 other deaths in service',
                                  True,
                                  'VA 2025 published totals (sum 405,399), external document'),
 ('65,507 Navy/Marine Corps/Coast Guard casualty-list observations',
                                  VALID['ds3_navy_casualties']['rows']==65507,
                                  f"{VALID['ds3_navy_casualties']['rows']} rows in DS3"),
 ('ICPSR 38927 DS3 & individual casualty & 65{,}507',
                                  VALID['ds3_navy_casualties']['rows']==65507,
                                  f"{VALID['ds3_navy_casualties']['rows']} (Table 1 restates it)"),

 # ---- Section 5.2: the industrial/military split -------------------------
 # The sentence attributes the split to the County Data Book's own two facility
 # series.  The stored counts are computed on W^F (WPB publicly financed plant)
 # against CDB military, which is a different partition: 1,059/435/334/290.
 # Both pairs round to 0.31, so the correlation survives either reading.
 ('(Spearman $\\rho = 0.31$)',    round(TGP['W_F x W_M']['spearman'],2)==0.31 and
                                  round(CDBS['rho'],2)==0.31 and
                                  GEOT['$W^F$ $\\times$ $W^M$'][2]==round(TGP['W_F x W_M']['spearman'],3),
                                  f"W^F x W^M {TGP['W_F x W_M']['spearman']}; "
                                  f"CDB ind x CDB mil {CDBS['rho']:.4f}"),
 ('386 received publicly financed plant only\n($W^F$), 349 a military installation only ($W^M$), and 275 both.',
                                  TGC['plant only']==386 and TGC['base only']==349 and
                                  TGC['both']==275 and
                                  sum(TGC.values())==1010,
                                  f"W^F-based {TGC['plant only']}/{TGC['base only']}/{TGC['both']} "
                                  f"of {sum(TGC.values())}; CDB-series basis would be "
                                  f"{CDBS['ind_only']}/{CDBS['mil_only']}/{CDBS['both']} of {CDBS['any']}"),

 # ---- Section 5.3: the pairwise geography quoted in prose ----------------
 ('which correlate at $\\rho = 0.616$',
                                  abs(TGP['W_C x W_F']['spearman']-0.616)<0.0005 and
                                  GEOT['$W^C$ $\\times$ $W^F$'][2]==0.616,
                                  f"{TGP['W_C x W_F']['spearman']} (table {GEOT['$W^C$ $\\times$ $W^F$'][2]})"),
 ('for military installations $\\mathcal{A} = 0.278$',
                                  abs(TGP['W_M x D']['A']-0.278)<0.0005 and
                                  GEOT['$W^M$ $\\times$ D'][0]==0.278,
                                  f"{TGP['W_M x D']['A']} (table {GEOT['$W^M$ $\\times$ D'][0]})"),

 # ---- the overlap decomposition, gap and interaction ---------------------
 ('Decomposing the $0.534$ gap', abs((1-ACD['observed'])-0.534)<0.0005,
                                  f"1 - {ACD['observed']} = {1-ACD['observed']:.4f}"),
 ('leave the\nremaining 18 percent in an unassigned interaction',
                                  abs(100*ACD['interaction_share']-18)<0.5 and
                                  abs(ACD['share_from_contract_concentration']
                                      +ACD['share_from_death_deviation']
                                      +ACD['interaction_share']-1)<0.002,
                                  f"{100*ACD['interaction_share']:.1f}%"),
 ('from 76 to 85 percent of the misalignment',
                                  abs(100*ACD['share_from_contract_concentration']-76)<0.5 and
                                  abs(100*ACD['shapley_contract_share']-85)<0.5,
                                  f"{100*ACD['share_from_contract_concentration']:.1f} -> "
                                  f"{100*ACD['shapley_contract_share']:.1f}"),
 # The null MEAN was unchecked while only its z was pinned.  It is a different
 # quantity from A(P, W^C) = 0.4979 two sentences earlier, and the two are
 # printed as the same 0.498.
 ('below the null mean of $0.498$',
                                  abs(PN['mean']-0.498)<0.0005 and PN['sd']>0,
                                  f"Poisson null mean {PN['mean']} (sd {PN['sd']}); "
                                  f"A(P,W^C) = {ACD['deaths_prop_to_pop']}"),

 # ---- the installation near-zero: its interval, its p, its R^2 -----------
 ('has a confidence interval of $[-0.089, -0.018]$, which excludes zero\n($p = 0.003$)',
                                  ACR['fatal burden, per resident']['W_M']['ci']==[-0.089,-0.018] and
                                  abs(BRP['W_M'][1]-0.003)<0.0005 and
                                  BRP['W_M'][2]==3073,
                                  f"CI {ACR['fatal burden, per resident']['W_M']['ci']}, "
                                  f"p={BRP['W_M'][1]:.5f}, n={BRP['W_M'][2]}"),
 ('three-tenths of one\npercent of the variance in installation spending',
                                  round(100*ACR['fatal burden, per resident']['W_M']['rho']**2,1)==0.3,
                                  f"rho^2 = {100*ACR['fatal burden, per resident']['W_M']['rho']**2:.3f}%"),
 # The other two near-zeros are called 'not statistically distinguishable from
 # zero'; nothing checked that, and the sentence turns on it.
 ('Two of the three are not statistically distinguishable from zero',
                                  BRP['W_C'][1]>0.05 and BRP['W_F'][1]>0.05,
                                  f"p_C={BRP['W_C'][1]:.3f}, p_F={BRP['W_F'][1]:.3f}"),

 # ---- the summary of the allocation function's weights -------------------
 # DEFECT: the printed band is '$0.4$ to $0.7$', but the nine cells the sentence
 # summarises run 0.234 to 0.693 and three of them (all of W^M) sit below 0.4 --
 # including the +0.23 the sentence three lines above reports.  The anchor is
 # the fragment that survives the correction.
 ('on prewar industrial capacity, urbanization and size, and a',
                                  abs(CRITMIN-0.234)<0.0005 and abs(CRITMAX-0.693)<0.0005 and
                                  '$0.4$ to $0.7$' not in tex,
                                  f"prewar-row rank correlations run {CRITMIN:+.3f} to {CRITMAX:+.3f}"),
 ('the standard error of a rank correlation is\n$0.018$',
                                  abs(1/np.sqrt(ACR['1940 log population']['W_C']['n']-3)-0.018)<0.0005,
                                  f"1/sqrt({ACR['1940 log population']['W_C']['n']}-3) = "
                                  f"{1/np.sqrt(ACR['1940 log population']['W_C']['n']-3):.4f}"),
 ('standard error of a rank correlation at $n = 3{,}073$ is $0.018$.',
                                  abs(1/np.sqrt(ACR['fatal burden, per resident']['W_M']['n']-3)-0.018)<0.0005
                                  and ACR['fatal burden, per resident']['W_M']['n']==3073,
                                  f"{1/np.sqrt(ACR['fatal burden, per resident']['W_M']['n']-3):.4f} "
                                  f"at n={ACR['fatal burden, per resident']['W_M']['n']}"),

 # ---- the year-by-year footnote -----------------------------------------
 # The existing coverage check reads max(coverage); the sentence names 1943, so
 # this pins the year rather than the maximum.
 ('contract in 1940 against 40.1 percent in 1943',
                                  abs(100*BY['coverage'][BYY.index(1943)]-40.1)<0.05 and
                                  abs(100*BY['coverage'][BYY.index(1940)]-15.0)<0.05,
                                  f"1940 {100*BY['coverage'][BYY.index(1940)]:.1f}%, "
                                  f"1943 {100*BY['coverage'][BYY.index(1943)]:.1f}%"),
 ('column that is 85 percent zeros is mechanically attenuated',
                                  abs(100*(1-BY['coverage'][BYY.index(1940)])-85)<0.5,
                                  f"{100*(1-BY['coverage'][BYY.index(1940)]):.1f}% zeros in 1940"),
 ('on standard errors of\n$0.0008$ to $0.0014$ against coefficients never exceeding $0.0012$ in absolute\nvalue',
                                  abs(min(BY['b_enlistee']['se'])-0.0008)<0.00005 and
                                  abs(max(BY['b_enlistee']['se'])-0.0014)<0.00005 and
                                  max(abs(c) for c in BY['b_enlistee']['coef'])<=0.00125,
                                  f"se {min(BY['b_enlistee']['se'])}-{max(BY['b_enlistee']['se'])}, "
                                  f"max|coef| {max(abs(c) for c in BY['b_enlistee']['coef'])}"),

 # ---- B^A is not a restatement of B^civic --------------------------------
 # DEFECT: '+0.101' reproduces on no sample.  analysis_exposure.py prints this
 # correlation and stores only its sibling, so nothing could catch the drift.
 # Current value on the 2,976-county valid-B^A sample is +0.094 (all 3,073
 # counties give +0.084).  Anchor chosen to survive the correction.
 ('is nearly independent of the share of military-age',
                                  abs(MOB_BCIVIC-0.0945)<0.0005 and MOB_N==2976 and
                                  '$\\rho = +0.101$' not in tex,
                                  f"Spearman(mob, B^civic) = {MOB_BCIVIC:+.4f} on n={MOB_N}; "
                                  f"manuscript prints +0.101"),
 # its paired figure, checked on the same recomputation rather than the JSON
 ('whereas $B_i^{A}$ is strongly negatively related to',
                                  abs(MOB_BA-ex['spearman_mob_BA'])<0.0005,
                                  f"{MOB_BA:+.4f} (stored {ex['spearman_mob_BA']})"),

 # ---- figure notes: trims and caps are properties of make_maps.py --------
 ('Colour scales are trimmed at the 98th\npercentile',
                                  "v.quantile(.98)" in MAPS,
                                  'make_maps.py trims each panel at the 98th percentile'),
 ('Counties with fewer than 1{,}000 residents in 1940 are\nshown grey',
                                  "gd.pop1940 < 1000" in MAPS,
                                  'make_maps.py: SMALL = gd.pop1940 < 1000'),
 ('the 99th-percentile cap on fatal burden before residualizing',
                                  "gd.burden.quantile(.99)" in MAPS,
                                  'make_maps.py caps burden at the 99th percentile'),
 ('trimmed at the 97th\npercentile of $|I_i|$',
                                  "gd.imbalance.abs().quantile(.97)" in MAPS,
                                  'make_maps.py: lim = |I_i| 97th percentile'),
 ('Fatal burden is capped at its 99th percentile before\nresidualizing',
                                  "gd.burden.quantile(.99)" in MAPS,
                                  'make_maps.py caps burden at the 99th percentile'),
 ('residualized on 1940 log population, urban\nshare, Black population share, manufacturing share, and 1930--40 population\ngrowth',
                                  "['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040']" in MAPS,
                                  'make_maps.py residualises on exactly those five'),

 # The same statistic, two bases, six pages apart and neither named: Section 2's
 # 44.0 is the top-twenty share of the reconstruction restricted to the 3,070
 # counties the County Data Book also covers (like-for-like with its 42.7),
 # while Section 5.3's 43.8 is the same share on all 3,073.  Pin them together
 # so the pair cannot drift apart silently.
 ('in levels, and places 44.0 percent of dollars in the top twenty counties',
                                  abs(VAL['top20_recon']-43.96)<0.05 and VAL['n']==3070 and
                                  abs(100*m.nlargest(20,'contract_k').contract_k.sum()
                                      /m.contract_k.sum()-43.75)<0.05 and
                                  '43.8 percent of the contract dollars' in tex,
                                  f"44.0 = {VAL['top20_recon']:.2f}% on the {VAL['n']}-county CDB overlap; "
                                  f"43.8 = {100*m.nlargest(20,'contract_k').contract_k.sum()/m.contract_k.sum():.2f}% on all 3,073"),
]
