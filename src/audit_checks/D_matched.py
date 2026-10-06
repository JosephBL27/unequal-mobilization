from functools import lru_cache as _lru
# ---------------------------------------------------------------------------
# LANE D_matched -- Sections 5.7 and 5.8 (the two matched designs).
#
# Splice the CHECKS entries at the bottom of this file into src/audit_paper_vs_data.py's
# CHECKS list, and the helper block above it next to the other module-level
# helpers (after `aj=mr['adjacency']`, before `CHECKS=[`).
#
# Names assumed already defined by the audit: ROOT, AN, J, m, mp, mm, mr, am,
# aj, pe, me, MILP, FAC, GM, T6, fmt, np, pd, re, json.
#
# Three claims in this lane cannot be read from any stored artifact, because
# matched_military.py never persists its matched sample and matched_robustness.py
# never persists its neighbour pool:
#     the 481-county neighbour control pool,
#     the military design's state counts (27 states, max four, 27 clusters),
#     the plant design's cluster count (the table note says 40),
#     the Fisher exact test on plant x installation co-incidence.
# The helpers below recompute them.  The cheaper permanent fix is for
# matched_robustness.py to store `n_neighbour_pool` and for matched_military.py
# to store `n_controls`, `n_states_treated`, `max_treated_per_state` and
# `n_state_clusters`; then these helpers collapse to dictionary lookups.
# ---------------------------------------------------------------------------

_CTRL_D=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
         'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
_X0_D=_CTRL_D+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940',
               'mfg_suppressed']

@_lru(maxsize=None)
def _nbr_pool():
    """Size of the neighbour control pool, by matched_robustness.py's own rule.

    The manuscript says 481 in two places (Section 5.7 and the note to
    Table \\ref{tab:matchedrobust}).  The audit check that quoted 481 tested
    aj['log pop 1970']['n']==273 -- the matched N, a different quantity -- so
    the count itself was never compared to anything.
    """
    import pyreadstat
    if not hasattr(_nbr_pool,'_v'):
        base=pd.read_parquet(AN/'matched_sample_raw.parquet')
        adj,_=pyreadstat.read_dta(str(ROOT/'data/raw/garin_rothbaum/Data/RawData/'
                                       'NBER_county_adjacency2010.dta'))
        adj['fipscounty']=pd.to_numeric(adj.fipscounty,errors='coerce')
        adj['fipsneighbor']=pd.to_numeric(adj.fipsneighbor,errors='coerce')
        tre=set(base.loc[base.treat==1,'fips'])
        nb=(adj[adj.fipscounty.isin(tre)&~adj.fipsneighbor.isin(tre)]
            .fipsneighbor.dropna().astype(int).unique())
        sub=base[(base.treat==1)|(base.fips.isin(nb))]
        _nbr_pool._v=int((1-sub.treat).sum())
    return _nbr_pool._v

@_lru(maxsize=None)
def _plant_clusters():
    """(state clusters, states carrying a treated county) for the plant design."""
    if not hasattr(_plant_clusters,'_v'):
        s=pd.read_parquet(AN/'matched_sample.parquet',columns=['treat','mweight','statefip'])
        w=s[s.mweight>0]
        _plant_clusters._v=(int(w.statefip.nunique()),
                            int(w[w.treat==1].statefip.nunique()))
    return _plant_clusters._v

@_lru(maxsize=None)
def _mil_design():
    """Re-run matched_military.py's match to recover what its JSON does not store.

    Returns n_controls, n_state_clusters, n_states_treated, max_treated_per_state.
    """
    if not hasattr(_mil_design,'_v'):
        import statsmodels.api as sm
        from scipy.spatial import cKDTree
        s=pd.read_parquet(AN/'matched_sample_raw.parquet')
        s['mil_pc']=(pd.to_numeric(s.cdb_fac_military,errors='coerce').fillna(0)
                     /s.pop1940.replace(0,np.nan))
        cut=s.loc[s.mil_pc>0,'mil_pc'].quantile(0.90)
        s['treat_mil']=((s.mil_pc>=cut)&(s.mil_pc>0)).astype(int)
        s=s[~((s.treat==1)&(s.treat_mil==1))].copy()
        Zr=s[_X0_D].astype(float); Zr=Zr.loc[:,Zr.std()>1e-10]
        Zs=(Zr-Zr.mean())/Zr.std()
        ps=sm.Logit(s.treat_mil,sm.add_constant(Zs)).fit(disp=0,method='bfgs',maxiter=500)
        s['pscore']=ps.predict(sm.add_constant(Zs))
        lo,hi=s.loc[s.treat_mil==1,'pscore'].min(),s.loc[s.treat_mil==1,'pscore'].max()
        sup=s[(s.pscore>=lo)&(s.pscore<=hi)].copy()
        cal=0.2*sup.pscore.std()
        tr=sup[sup.treat_mil==1]; ct=sup[sup.treat_mil==0]
        dist,idx=cKDTree(ct[['pscore']].values).query(tr[['pscore']].values,k=min(3,len(ct)))
        w=pd.Series(0.0,index=sup.fips); mt=[]
        for i,(dd,ii) in enumerate(zip(np.atleast_2d(dist),np.atleast_2d(idx))):
            keep=[j for dj,j in zip(dd,ii) if dj<=cal]
            if not keep: continue
            mt.append(tr.iloc[i].fips)
            for j in keep: w[ct.iloc[j].fips]+=1.0/len(keep)
        sup['mweight']=np.where(sup.treat_mil==1,sup.fips.isin(mt).astype(float),
                                sup.fips.map(w).fillna(0))
        mw=sup[sup.mweight>0]
        vc=mw[mw.treat_mil==1].statefip.value_counts()
        _mil_design._v={'n_treated':len(mt),
                        'n_controls':int((mw.treat_mil==0).sum()),
                        'n_clusters':int(mw.statefip.nunique()),
                        'n_states_treated':int(vc.size),
                        'max_per_state':int(vc.max())}
    return _mil_design._v

@_lru(maxsize=None)
def _cooccur():
    """Plant x top-decile installation on the 2,973-county estimation sample."""
    if not hasattr(_cooccur,'_v'):
        from scipy.stats import fisher_exact
        s=pd.read_parquet(AN/'matched_sample_raw.parquet',
                          columns=['treat','cdb_fac_military','pop1940'])
        pc=(pd.to_numeric(s.cdb_fac_military,errors='coerce').fillna(0)
            /s.pop1940.replace(0,np.nan))
        cut=pc[pc>0].quantile(0.90)
        tm=((pc>=cut)&(pc>0)).astype(int)
        n=len(s); a=int(s.treat.sum()); b=int(tm.sum())
        both=int(((s.treat==1)&(tm==1)).sum())
        p=float(fisher_exact([[both,a-both],[b-both,n-a-b+both]])[1])
        _cooccur._v={'n':n,'plant':a,'mil':b,'both':both,'expected':a*b/n,'fisher_p':p}
    return _cooccur._v

def _bal(src,key,var):
    return [b for b in src['balance'] if b['var']==var][0][key]

def _tabN(stem,col=-1):
    """The N column of a typeset table body, as integers."""
    out=[]
    for l in (ROOT/'paper/tables'/f'{stem}.tex').read_text().splitlines():
        if '&' not in l or l.lstrip().startswith(('\\toprule','\\midrule','\\bottomrule',
                                                  '\\multicolumn','\\cmidrule','Outcome',
                                                  '&')): continue
        cells=[c.strip().rstrip('\\\\').strip() for c in l.split('&')]
        try: out.append(int(re.sub(r'[^0-9]','',cells[col])))
        except (ValueError,IndexError): pass
    return out

@_lru(maxsize=None)
def _tab_bal():
    """The nine (raw, matched) SMD pairs of tabA_balance.tex, as typeset."""
    out=[]
    for l in (ROOT/'paper/tables/tabA_balance.tex').read_text().splitlines():
        c=[x.strip() for x in l.split('&')]
        if len(c)!=3 or c[0].startswith(('Covariate','Imbalanced')): continue
        try: out.append((float(c[1]),float(re.sub(r'[^0-9.\-]','',c[2]))))
        except ValueError: pass
    return out

@_lru(maxsize=None)
def _tab_bal_counts():
    for l in (ROOT/'paper/tables/tabA_balance.tex').read_text().splitlines():
        if l.startswith('Imbalanced'):
            return tuple(int(re.search(r'(\d+) of 9',c).group(1))
                         for c in l.split('&')[1:3])
    raise KeyError('Imbalanced row')

@_lru(maxsize=None)
def _tt_footer():
    """(plant treated, military treated, plant imbalanced, military imbalanced)
    from tab_twotreatments.tex as typeset."""
    T=I=None
    for l in (ROOT/'paper/tables/tab_twotreatments.tex').read_text().splitlines():
        if l.startswith('Treated counties'):
            c=[x.strip() for x in l.split('&')]; T=(int(c[1]),int(c[3]))
        if l.startswith('Covariates imbalanced'):
            c=[x.strip() for x in l.split('&')]
            I=(int(re.search(r'(\d+) of 9',c[1]).group(1)),
               int(re.search(r'(\d+) of 9',c[3]).group(1)))
    return (T[0],T[1],I[0],I[1])

_LADDER=lambda k: [r[k]['coef'] for r in am['thresholds']]+[am['absolute'][k]['coef']]
_LADDP =lambda k: [r[k]['p']    for r in am['thresholds']]+[am['absolute'][k]['p']]

# ---------------------------------------------------------------------------
# splice from here into CHECKS
# ---------------------------------------------------------------------------
CHECKS_D_MATCHED = [

 # ==== 5.7  treatment construction and sample ==============================
 # The three printed thresholds are the design.  Recomputing the located
 # qualifying count under exactly the numbers the sentence prints ties the
 # prose to the parser rather than to a remembered constant.
 ('publicly financed (private share of structure spending at most five\npercent), newly built (structures above forty percent of plant cost), and large\n(cost of at least \\$10 million)',
                                   (lambda g: int(((np.where((pd.to_numeric(g.pub_struct,errors='coerce').fillna(0)
                                                              +pd.to_numeric(g.priv_struct,errors='coerce').fillna(0))>0,
                                     pd.to_numeric(g.priv_struct,errors='coerce').fillna(0)/
                                     (pd.to_numeric(g.pub_struct,errors='coerce').fillna(0)
                                      +pd.to_numeric(g.priv_struct,errors='coerce').fillna(0)).replace(0,np.nan),
                                     np.where(pd.to_numeric(g.priv_total,errors='coerce').fillna(0)>0,1.0,0.0))<=0.05)
                                    &(g.get('newplant',pd.Series(False,index=g.index)).fillna(False).astype(bool)
                                      |(np.where(pd.to_numeric(g.total_cost,errors='coerce').fillna(0)>0,
                                        (pd.to_numeric(g.pub_struct,errors='coerce').fillna(0)
                                         +pd.to_numeric(g.priv_struct,errors='coerce').fillna(0))
                                        /pd.to_numeric(g.total_cost,errors='coerce').replace(0,np.nan),0)>0.40))
                                    &(pd.to_numeric(g.total_cost,errors='coerce').fillna(0)>=10000)
                                    &g.fips.notna()).sum()))(f)
                                   ==J('matched_design_setup.json')['n_bigpub_plants'],
                                   f"{J('matched_design_setup.json')['n_bigpub_plants']} located plants under 5%/40%/$10m"),
 ('Those 214 are worth\n\\$8.08 billion, are spread across 164 counties after the independent-city merge',
                                   abs(J('matched_design_setup.json')['bigpub_dollars_k']/1e6-8.08)<0.005 and
                                   J('matched_design_setup.json')['treated_counties']==164 and
                                   abs(FAC['located_bn']-J('matched_design_setup.json')['bigpub_dollars_k']/1e6)<0.005,
                                   f"${J('matched_design_setup.json')['bigpub_dollars_k']/1e6:.3f}bn in "
                                   f"{J('matched_design_setup.json')['treated_counties']} counties"),
 # 3,073 - 2,973 = the hundred dropped; the sentence and the arithmetic have to agree
 ('The hundred largest manufacturing counties of 1940 are dropped',
                                   len(m)-J('matched_design_setup.json')['sample_n']==100,
                                   f"{len(m)-J('matched_design_setup.json')['sample_n']} dropped "
                                   f"({len(m)} - {J('matched_design_setup.json')['sample_n']})"),
 ('After this restriction the sample is 2{,}973 counties, of\nwhich 118 are treated',
                                   J('matched_design_setup.json')['sample_n']==2973 and
                                   J('matched_design_setup.json')['sample_treated']==118,
                                   f"{J('matched_design_setup.json')['sample_n']} / "
                                   f"{J('matched_design_setup.json')['sample_treated']}"),
 # the caliper is stored in propensity units; 0.2 sd is the claim
 ('matched to at most\nthree controls within a caliper of 0.2 standard deviations, on common support',
                                   abs(mp['setup']['caliper']
                                       -0.2*pd.read_parquet(AN/'matched_sample.parquet',
                                                            columns=['pscore']).pscore.std())<1e-5 and
                                   mp['setup']['n_support']==len(pd.read_parquet(
                                       AN/'matched_sample.parquet',columns=['pscore'])),
                                   f"caliper {mp['setup']['caliper']} = 0.2 sd on {mp['setup']['n_support']} on support"),

 # ==== 5.7  balance ========================================================
 ('seven of the nine covariates exceed the conventional\n0.10 threshold, and log population differs by 1.45 standard deviations',
                                   sum(1 for b in mp['balance'] if abs(b['smd_raw'])>0.10)==7 and
                                   mp['imbalanced_raw']==7 and
                                   abs(_bal(mp,'smd_raw','logpop1940')-1.45)<0.005,
                                   f"{mp['imbalanced_raw']} of 9 raw, logpop {_bal(mp,'smd_raw','logpop1940'):.4f}"),
 ('latitude ($-0.124$), a geographic coordinate rather than a measure of economic\nstructure, and the 1940 Black population share ($0.107$)',
                                   abs(_bal(mp,'smd_matched','LATITUDE')+0.124)<0.0005 and
                                   abs(_bal(mp,'smd_matched','blackshare1940')-0.107)<0.0005 and
                                   sorted(b['var'] for b in mp['balance']
                                          if abs(b['smd_matched'])>0.10)==['LATITUDE','blackshare1940'],
                                   f"lat {_bal(mp,'smd_matched','LATITUDE'):.4f}, "
                                   f"black {_bal(mp,'smd_matched','blackshare1940'):.4f}"),
 ('the treated\nand control groups are balanced to within $0.10$ standard deviations',
                                   max(abs(_bal(mp,'smd_matched',v)) for v in
                                       ('logpop1940','urbrate1940','mfgshare1940','popgrowth_3040'))<0.10,
                                   f"worst of the four prewar dims = "
                                   f"{max(abs(_bal(mp,'smd_matched',v)) for v in ('logpop1940','urbrate1940','mfgshare1940','popgrowth_3040')):.4f}"),
 # The typeset balance table is what the reader sees, so compare it to the JSON
 # rather than comparing the JSON to itself: nine SMD pairs plus the two counts.
 ('\\emph{Balance.} Table \\ref{tab:balance} reports standardized mean differences.',
                                   _tab_bal()==[(round(b['smd_raw'],3),round(b['smd_matched'],3))
                                                for b in mp['balance']] and
                                   _tab_bal_counts()==(mp['imbalanced_raw'],mp['imbalanced_matched']),
                                   f"tabA_balance counts {_tab_bal_counts()} vs JSON "
                                   f"({mp['imbalanced_raw']}, {mp['imbalanced_matched']})"),

 # ==== 5.7  estimates ======================================================
 ('all relative to matched controls and all significant at the one percent\nlevel',
                                   max(pe[k]['p'] for k in ('log population 1970',
                                       'manufacturing share 1970','log family income 1970'))<0.01,
                                   f"max p = {max(pe[k]['p'] for k in ('log population 1970','manufacturing share 1970','log family income 1970')):.4f}"),
 ('Inverse-probability weighting on common\nsupport gives the same signs throughout and larger magnitudes for population,\nmanufacturing and income.',
                                   all(np.sign(e['ipw'])==np.sign(e['matched']) for e in mp['effects']) and
                                   all(abs(pe[k]['ipw'])>abs(pe[k]['matched']) for k in
                                       ('log population 1970','manufacturing share 1970','log family income 1970')),
                                   ' '.join(f"{k.split()[-2]}:{pe[k]['ipw']:.3f}>{pe[k]['matched']:.3f}" for k in
                                            ('log population 1970','manufacturing share 1970','log family income 1970'))),
 ('115 treated counties matched to 249 distinct controls within a\n0.2 standard-deviation caliper on the propensity score, excluding the 100\nlargest manufacturing counties of 1940',
                                   mp['setup']['n_matched_treated']==115 and
                                   int(pd.read_parquet(AN/'matched_sample.parquet',
                                       columns=['treat','mweight']).query('treat==0 and mweight>0').shape[0])==249 and
                                   len(m)-J('matched_design_setup.json')['sample_n']==100,
                                   f"{mp['setup']['n_matched_treated']} treated / "
                                   f"{int(pd.read_parquet(AN/'matched_sample.parquet',columns=['treat','mweight']).query('treat==0 and mweight>0').shape[0])} controls"),
 # The note says N "varies by one where an outcome is missing".  It does not
 # vary: all eight rows are the matched sample.  This pins the column to the
 # matched sample size and to a spread of at most one, which is the strongest
 # true reading of the sentence.
 ('$N$ is the number of distinct counties on the matched sample.',
                                   (lambda N: len(N)==8 and max(N)-min(N)<=1 and
                                    max(N)==mp['effects'][0]['n'])(_tabN('tab_matched')),
                                   f"tab_matched N column = {sorted(set(_tabN('tab_matched')))}"),

 # ==== 5.7  neighbour comparison ===========================================
 # 481 appears twice and matches nothing the committed code produces: the rule
 # in matched_robustness.py returns 475 untreated neighbours inside the 2,973
 # county sample (529 unique neighbour fips nationally, 524 in the 3,073-county
 # panel).  It is a figure computed before a sample restriction.
 ('The control pool is restricted to the 475\nuntreated counties that directly border a treated one',
                                   _nbr_pool()==475,
                                   f"{_nbr_pool()} untreated neighbours in the estimation sample"),
 ('The final panel restricts the control pool to the 475 untreated counties that directly border a treated county',
                                   _nbr_pool()==475,
                                   f"{_nbr_pool()} untreated neighbours in the estimation sample"),
 ('at magnitudes between roughly half and the whole of the matched-control\nestimate',
                                   all(0.45<=aj[a]['coef']/pe[b]['matched']<=1.00 for a,b in
                                       [('log pop 1970','log population 1970'),
                                        ('mfg share 1970','manufacturing share 1970'),
                                        ('log income 1970','log family income 1970')]),
                                   ' '.join(f"{aj[a]['coef']/pe[b]['matched']:.2f}" for a,b in
                                            [('log pop 1970','log population 1970'),
                                             ('mfg share 1970','manufacturing share 1970'),
                                             ('log income 1970','log family income 1970')])),

 # ==== 5.8  design, balance, clusters ======================================
 ('52 of the 54 match to 152 controls, and\nthe treated counties are spread across 27 states with at most four in any one',
                                   _mil_design()['n_treated']==52 and
                                   _mil_design()['n_controls']==152 and
                                   _mil_design()['n_states_treated']==27 and
                                   _mil_design()['max_per_state']==4 and
                                   mm['n_treated']==52 and mm['n_treated_design']==54,
                                   f"{_mil_design()['n_treated']} treated / {_mil_design()['n_controls']} controls / "
                                   f"{_mil_design()['n_states_treated']} states, max {_mil_design()['max_per_state']}"),
 ('imbalance falls from eight of nine covariates to one',
                                   sum(1 for b in mm['balance'] if abs(b['raw'])>0.10)==8 and
                                   sum(1 for b in mm['balance'] if abs(b['matched'])>0.10)==1,
                                   f"{sum(1 for b in mm['balance'] if abs(b['raw'])>0.10)} raw -> "
                                   f"{sum(1 for b in mm['balance'] if abs(b['matched'])>0.10)} matched"),
 # Table 7's own footer rows, read from the typeset file: treated counts and
 # imbalance counts for both designs, against the two JSONs that produce them.
 ('Table \\ref{tab:twotreatments} sets the two treatments side by side',
                                   _tt_footer()==(mp['setup']['n_matched_treated'],mm['n_treated'],
                                                  mp['imbalanced_matched'],
                                                  sum(1 for b in mm['balance'] if abs(b['matched'])>0.10)),
                                   f"tab_twotreatments footer {_tt_footer()} vs "
                                   f"({mp['setup']['n_matched_treated']}, {mm['n_treated']}, "
                                   f"{mp['imbalanced_matched']}, "
                                   f"{sum(1 for b in mm['balance'] if abs(b['matched'])>0.10)})"),
 # The plant design clusters on 44 states, not 40.  Nothing checked this: the
 # note is typeset text and the cluster count is not stored in any JSON.
 ('standard errors\nclustered on state, 44 state clusters for the plant design and 40 for the\nmilitary design, of which 38 and 27 respectively carry a treated county',
                                   _plant_clusters()==(44,38) and
                                   (_mil_design()['n_clusters'],_mil_design()['n_states_treated'])==(40,27),
                                   f"plant {_plant_clusters()[0]} clusters / {_plant_clusters()[1]} with treated; "
                                   f"military {_mil_design()['n_clusters']} / {_mil_design()['n_states_treated']}"),
 ('Family income rose under both.',
                                   pe['log family income 1970']['matched']>0 and
                                   me['log family income 1970']['coef']>0 and
                                   max(pe['log family income 1970']['p'],
                                       me['log family income 1970']['p'])<0.01,
                                   f"plant {pe['log family income 1970']['matched']:.4f} "
                                   f"(p={pe['log family income 1970']['p']:.4f}), military "
                                   f"{me['log family income 1970']['coef']:.4f} (p={me['log family income 1970']['p']:.4f})"),

 # ==== 5.8  threshold ladder ===============================================
 ('Every definition gives the same signs at $p<0.01$',
                                   max(max(_LADDP(k)) for k in ('log pop','mfg share','own rate'))<0.01 and
                                   all(len(set(np.sign(_LADDER(k))))==1 for k in
                                       ('log pop','mfg share','own rate')),
                                   f"max p across the five definitions = "
                                   f"{max(max(_LADDP(k)) for k in ('log pop','mfg share','own rate')):.4f}"),
 ('the homeownership effect declines\nmonotonically from $-9.25$ points at the top five percent to $-4.29$ at the\nabsolute cutoff',
                                   abs(_LADDER('own rate')[0]+9.25)<0.005 and
                                   abs(_LADDER('own rate')[-1]+4.29)<0.005 and
                                   all(b>a for a,b in zip(_LADDER('own rate'),_LADDER('own rate')[1:])),
                                   f"{_LADDER('own rate')}"),
 ('population likewise from $0.87$ to $0.37$ log points',
                                   abs(_LADDER('log pop')[0]-0.87)<0.005 and
                                   abs(_LADDER('log pop')[-1]-0.37)<0.005 and
                                   all(b<a for a,b in zip(_LADDER('log pop'),_LADDER('log pop')[1:])),
                                   f"{_LADDER('log pop')}"),
 ('The\nmanufacturing effect falls from $-9.09$ to roughly $-4.3$ and is then flat rather\nthan monotone',
                                   abs(_LADDER('mfg share')[0]+9.09)<0.005 and
                                   not all(b<=a for a,b in zip([abs(x) for x in _LADDER('mfg share')],
                                                               [abs(x) for x in _LADDER('mfg share')][1:])) and
                                   max(abs(x) for x in _LADDER('mfg share')[1:])<4.8,
                                   f"{_LADDER('mfg share')}"),
 ('permuting treatment 500 times gives permutation $p$-values of',
                                   all(r['n_draws']==500 for r in am['randomization']) and
                                   len(am['randomization'])==3,
                                   f"{[r['n_draws'] for r in am['randomization']]}"),
 ('$0.000$ for population, $0.004$ for the manufacturing share, and $0.000$ for\nhomeownership.',
                                   (lambda R: R['log pop']<0.001 and abs(R['mfg share']-0.004)<0.0005
                                    and R['own rate']<0.001)({r['outcome']:r['perm_p']
                                                              for r in am['randomization']}),
                                   ' '.join(f"{r['outcome']}={r['perm_p']}" for r in am['randomization'])),
 ('it requires no distributional assumption about the 52 treated units',
                                   mm['n_treated']==52 and _mil_design()['n_treated']==52,
                                   f"{mm['n_treated']}"),

 # ==== 5.8  tenure and GI Bill ============================================
 ('the fatality\nrate per enlistee is again indistinguishable ($p = 0.78$)',
                                   abs(GM['deaths per 1,000 enlistees']['p']-0.78)<0.005,
                                   f"{GM['deaths per 1,000 enlistees']['coef']:.3f} "
                                   f"p={GM['deaths per 1,000 enlistees']['p']:.4f}"),
 # restatement of the 5.7 estimate inside the 5.8 footnote; the p was unchecked here
 ('coefficient on 1970 homeownership is $+0.94$ points against matched controls\n($p = 0.12$), $+0.40$ against untreated neighbors ($p = 0.48$)',
                                   round(pe['homeownership 1970']['matched'],2)==0.94 and
                                   round(pe['homeownership 1970']['p'],2)==0.12 and
                                   round(aj['homeownership 1970']['coef'],2)==0.40 and
                                   round(aj['homeownership 1970']['p'],2)==0.48,
                                   f"{pe['homeownership 1970']['matched']:.4f} p={pe['homeownership 1970']['p']:.4f} / "
                                   f"{aj['homeownership 1970']['coef']:.4f} p={aj['homeownership 1970']['p']:.4f}"),
 # "indistinguishable from zero in the continuous specification" -- read the
 # typeset Table 4 cell, stars and all, not a JSON p-value
 ('indistinguishable from zero in the continuous specification of\nTable \\ref{tab:main}',
                                   abs(T6['War plant']-0.0562)<0.0005 and
                                   '$^{*' not in [l for l in (ROOT/'paper/tables/tab_main.tex')
                                                  .read_text().splitlines()
                                                  if l.startswith('War plant')][0].split('&')[7],
                                   f"tab_main own-rate cell for War plant = {T6['War plant']}, unstarred"),
 ('The installation coefficient is $-7.49$ points and\nsurvives every specification tried',
                                   abs(me['homeownership 1970']['coef']+7.49)<0.005 and
                                   all(c<0 for c in _LADDER('own rate')) and
                                   max(_LADDP('own rate'))<0.01,
                                   f"baseline {me['homeownership 1970']['coef']:.4f}; ladder {_LADDER('own rate')}"),

 # ==== 5.8  co-incidence of the two treatments =============================
 ('only two received both --- against\n2.2 expected if the two allocations were statistically independent (Fisher\nexact $p = 1.00$)',
                                   _cooccur()['both']==2 and
                                   abs(_cooccur()['expected']-2.2)<0.05 and
                                   round(_cooccur()['fisher_p'],2)==1.00,
                                   f"both={_cooccur()['both']}, expected={_cooccur()['expected']:.3f}, "
                                   f"Fisher p={_cooccur()['fisher_p']:.3f}"),
 ('design. Of the 2{,}973 counties in the sample, 118 received a large public\nplant and 56 a top-decile installation',
                                   _cooccur()['plant']==J('matched_design_setup.json')['sample_treated']==118 and
                                   _cooccur()['mil']==mm['n_treated_predrop']==56 and
                                   _cooccur()['n']==J('matched_design_setup.json')['sample_n'],
                                   f"{_cooccur()['plant']} plant / {_cooccur()['mil']} military "
                                   f"on {_cooccur()['n']} counties"),

 # ==== claims about other people's papers ==================================
 # No artifact in this repository can produce these; they are properties of
 # Garin-Rothbaum (2025) and Fetter (2013).  Presence-only, and labelled as
 # such so nobody later reads a passing row as a data check.
 ('against roughly 70 percent for\ntheir 353-plant definition', True,
                                   'Garin-Rothbaum coverage; external, not computable here'),
 ('attributes 7.4\npercent of the 1940--60 national rise in home ownership', True,
                                   'Fetter (2013) magnitude; external, not computable here'),
 ('and 25 percent of the\nrise for affected cohorts', True,
                                   'Fetter (2013) magnitude; external, not computable here'),
]
