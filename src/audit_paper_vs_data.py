#!/usr/bin/env python3
"""Check every quantitative claim in the manuscript against the current artifacts."""
import json, sys, re, math
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'
tex=(ROOT/'paper/War_Divergence.tex').read_text()
J=lambda n: json.loads((AN/n).read_text())
o,tg,ex,co = J('overlap_results.json'),J('three_geographies.json'),J('exposure_results.json'),J('composition_results.json')
mp,mm,am,rb = J('matched_results.json'),J('matched_military.json'),J('audit_military.json'),J('robustness.json')
mr = J('matched_robustness.json')
imp,gi = J('imp_specifications.json'), J('gi_bill_channel.json')
PR2 = J('iv_three_endog_r2.json')
AC = J('allocation_criteria.json')
ACR= AC['criteria']; ACD=AC['overlap_decomposition']
IVH = {r['spec']: r['iv'] for r in J('iv_single_results.json') if r['outcome']=='homeownership 1970'}
ISP={r['instrument']:r for r in imp['specifications']}
GP={r['outcome']:r for r in gi['plant']}; GM={r['outcome']:r for r in gi['military']}
iv,ivs,ivv = J('iv_results.json'),J('iv_single_results.json'),J('iv_validity.json')
MR = J('match_report.json'); DS1 = MR['casualties_ds1']
m=pd.read_parquet(AN/'master_panel_v3.parquet')
f=pd.read_parquet(AN/'facilities_geocoded.parquet')

# ---- independent recomputation from the panel and the raw tables ---------
# These do not go through any intermediate JSON: a claim that reads a stale
# artifact still passes its own check, which is how the validation paragraph
# kept a correlation of 0.975 that no sample produced.
def _validation_block():
    from scipy.stats import pearsonr
    cdd=m.dropna(subset=['cdb_contracts_k'])
    x=pd.to_numeric(cdd.contract_k,errors='coerce'); y=pd.to_numeric(cdd.cdb_contracts_k,errors='coerce')
    ok=x.notna()&y.notna(); x,y=x[ok],y[ok]
    xf=pd.to_numeric(cdd.fac_public_k,errors='coerce')
    yf=pd.to_numeric(cdd.cdb_fac_industrial,errors='coerce')
    okf=xf.notna()&yf.notna()
    P=m.pop1940.replace(0,np.nan); D=m.deaths_all.fillna(0)
    il=m[(m.fips//1000)==17]
    strate=m.groupby(m.fips//1000).apply(lambda g: 1000*g.deaths_all.fillna(0).sum()/g.pop1940.sum())
    strate=strate.drop(index=11,errors='ignore')          # DC is a district, not a state
    ic=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
    cg=pd.read_parquet(AN/'contracts_geocoded.parquet')
    icv=pd.to_numeric(cg.loc[pd.to_numeric(cg.fips,errors='coerce').isin(set(ic.city_fips)),
                             'ValueThousandsDollars'],errors='coerce').sum()/1e6
    ff=f.copy()
    for c in ['total_cost','pub_struct','priv_struct','pub_total','priv_total']:
        ff[c]=pd.to_numeric(ff[c],errors='coerce').fillna(0)
    st=ff.pub_struct+ff.priv_struct
    privshr=np.where(st>0, ff.priv_struct/st, np.where(ff.priv_total>0,1.0,0.0))
    bigpub=(privshr<=0.05)&((ff.get('newplant',False).fillna(False).astype(bool))|
            (np.where(ff.total_cost>0, st/ff.total_cost,0)>0.40))&(ff.total_cost>=10000)
    mil=pd.to_numeric(m.cdb_fac_military,errors='coerce').fillna(0)
    return {
      'n':int(len(x)), 'pearson':float(pearsonr(x,y)[0]),
      'recon_on_cdb_bn':float(x.sum()/1e6), 'cdb_bn':float(y.sum()/1e6),
      'pct_diff':float(100*(y.sum()-x.sum())/y.sum()),
      'top20_recon':float(100*x.nlargest(20).sum()/x.sum()),
      'top20_cdb':float(100*y.nlargest(20).sum()/y.sum()),
      'pearson_fac':float(pearsonr(xf[okf],yf[okf])[0]),
      'zero_recon':int((m.contract_k.fillna(0)==0).sum()),
      'zero_cdb':int((m.cdb_contracts_k.fillna(0)==0).sum()),
      'zero_plant':int((m.fac_public_k.fillna(0)==0).sum()),
      'counties_pubplant':int((m.fac_public_k.fillna(0)>0).sum()),
      'zero_death_counties':int((D==0).sum()),
      'nat_rate':float(1000*D.sum()/m.pop1940.sum()),
      'il_rate':float(1000*il.deaths_all.fillna(0).sum()/il.pop1940.sum()),
      'nm_rate':float(strate.loc[35]), 'nm_is_top_state':bool(strate.idxmax()==35),
      'ic_contracts_bn':float(icv),
      'bigpub_all_bn':float(ff.loc[bigpub,'total_cost'].sum()/1e6),
      # This used to fall back to a hardcoded 0.26 when the key was absent,
      # which it always was, so the check compared a literal to itself.
      'mil_treat_share_sample':float(mm['treated_share_sample']),
      'mil_treat_share_nat':float(mm['treated_share_national']),
      'mil_treat_bn':float(mm['treated_dollars_bn']),
      'mil_treat_n':int(mm['n_treated_predrop']),
    }
# Table 5's conditional coefficients: the paper reports the p10-p90 spread they
# imply, because the coefficients are significant and economically negligible and
# reporting only the stars would misrepresent them in either direction.
def _t5_spread():
    P=m.pop1940.replace(0,np.nan)
    B=1000*m.deaths_all.fillna(0)/P
    lo,hi=B.quantile(.1),B.quantile(.9)
    _t5=(ROOT/'paper/tables/tab_allocation.tex').read_text().splitlines()
    row=[l for l in _t5 if l.startswith('$B_i$, plus prewar controls')][0]
    cells=[c.strip() for c in row.split('&')][1:4]
    coefs=[float(re.sub(r'[^0-9.\-]','',c)) for c in cells]
    return [c*(hi-lo) for c in coefs]
T5SPREAD=_t5_spread()
# the seven-specification range quoted for the matched design
# matched_robustness.json keys are 'params' and 'samples', each a list of specs
# carrying one dict per outcome. The previous expression read 'nn'/'caliper'/
# 'sample', which do not exist, so it always fell through to parsing the typeset
# table -- a check that silently stopped reading the artifact it names.
_mrb=[spec['log pop 1970']['coef']
      for k in ('params','samples') for spec in mr.get(k,[])
      if 'log pop 1970' in spec]
if not _mrb:
    raise RuntimeError('matched_robustness.json exposes no log-pop coefficients; '
                       'the artifact shape changed and this check must be updated')
MRB_MIN, MRB_MAX = min(_mrb), max(_mrb)

def _facilities_block():
    """Coverage arithmetic for the plant treatment, recomputed from records.

    These figures were carried as presence-only checks for several drafts --
    the string had to appear in the manuscript, but nothing compared it to the
    data -- which is how a within-set assignment rate came to be printed
    against a different study's all-new-plants rate as if the two shared a base.
    """
    g=f.copy()
    for c in ['total_cost','pub_total','priv_total','pub_struct','priv_struct']:
        g[c]=pd.to_numeric(g[c],errors='coerce').fillna(0)
    st=g.pub_struct+g.priv_struct
    privshr=np.where(st>0, g.priv_struct/st, np.where(g.priv_total>0,1.0,0.0))
    structshr=np.where(g.total_cost>0, st/g.total_cost, 0)
    isnew=g.get('newplant',pd.Series(False,index=g.index)).fillna(False).astype(bool)|(structshr>0.40)
    pub=privshr<=0.05; big=g.total_cost>=10000; loc=g.fips.notna()
    D=lambda mk: float(g.loc[mk,'total_cost'].sum()/1e6)
    _ay=1900+pd.to_numeric(g.date_avail.astype(str).str.extract(r'-(\d\d)$')[0],errors='coerce')
    return {
      'records':int(len(g)), 'total_bn':D(slice(None)), 'public_share':float(g.pub_total.sum()/g.total_cost.sum()),
      'n_qualifying':int((isnew&pub&big).sum()), 'qualifying_bn':D(isnew&pub&big),
      'n_located':int((isnew&pub&big&loc).sum()), 'located_bn':D(isnew&pub&big&loc),
      'located_share_of_qualifying':D(isnew&pub&big&loc)/D(isnew&pub&big),
      'all_new_bn':D(isnew), 'qualifying_share_of_all_new':D(isnew&pub&big)/D(isnew),
      # availability is printed as M-YY in the source volume
      'pub_1943_bn':float(g.loc[_ay==1943,'pub_total'].sum()/1e6),
      'pub_1944_bn':float(g.loc[_ay==1944,'pub_total'].sum()/1e6),
      'assignable_located_share':float(g.loc[g.assignable&loc,'pub_total'].sum()/
                                       g.loc[g.assignable,'pub_total'].sum()),
      'noplace_n':int((~g.assignable).sum()),
      'noplace_share':float(g.loc[~g.assignable,'pub_total'].sum()/g.pub_total.sum()),
    }
FAC=_facilities_block()
VAL=_validation_block()
# Table 6, read from the typeset file rather than from a result object, so the
# prose is checked against what the reader actually sees.
_t6=(ROOT/'paper/tables/tab_main.tex').read_text().splitlines()
def _t4(rowlabel,col):
    """Column `col` of Table 4's `rowlabel` row, read from the typeset file.
    1=log pop 1950, 2=log pop 1970, 3=mfg 1960, 4=mfg 1970, 5=inc 1950,
    6=inc 1970, 7=own 1970."""
    for ln in _t6:
        if ln.startswith(rowlabel):
            cells=[c.strip() for c in ln.split('&')]
            return float(re.sub(r'[^0-9.\-]','',cells[col]))
    raise KeyError(rowlabel)
def _own(rowlabel): return _t4(rowlabel,7)
T6={'Contracts':_own('Contracts'),'War plant':_own('War plant'),'Military':_own('Military')}

pe={e['outcome']:e for e in mp['effects']}; me={e['outcome']:e for e in mm['effects']}
MILP={x['outcome']:x for x in mm['placebo']}
BENL=ACR['fatal burden, per enlistee']
OB=J('oster_bounds.json')
IL=J('illinois_robustness.json')
cmp_=J('composition_results.json')
def _ob(g, out, k):
    return [r for r in OB[g] if r['outcome'] == out][0][k]
def _t14():
    """The three homeownership IV cells as typeset. The prose carried a -7.69
    that no artifact produces and no check looked at."""
    out=[]
    for l in (ROOT/'paper/tables/tabA_iv.tex').read_text().splitlines():
        if l.strip().startswith('\\quad homeownership 1970'):
            out.append(float(re.sub(r'[^0-9.\-]','',l.split('&')[2])))
    return tuple(out)
SS=J('shiftshare.json')
SSR={r['instrument']:r for r in SS['shiftshare']}
SSA=SSR['shift-share, all counties']; SSI=SS['imp_benchmark']
ROT={r['class']:r for r in SS['rotemberg']}
GF={g['class']:g for g in SS['greenfield']}
BY=SS['by_year']; CLF=SS['classifier']
RO={r['label']:r for r in json.loads((AN/'regression_results.json').read_text())['outcomes']}
def _t5res():
    ln=[l for l in (ROOT/'paper/tables/tab_criteria.tex').read_text().splitlines()
        if l.startswith('\\quad Fatal burden, per resident')][0]
    return tuple(float(c.strip().replace('\\\\','')) for c in ln.split('&')[1:4])
def _t5row():
    ln=[l for l in (ROOT/'paper/tables/tab_criteria.tex').read_text().splitlines()
        if l.startswith('\\quad Fatal burden, per enlistee')][0]
    return tuple(float(c.strip().replace('\\\\','')) for c in ln.split('&')[1:4])
# The eleven estimates the footnote names as the correction family. Listing them
# explicitly means a new diagnostic outcome cannot quietly enlarge it.
# The multiple-testing family is EVERY treatment-effect estimate the two designs
# report, derived from the artifacts rather than hand-listed. A hand-listed
# family is a family that can be quietly narrowed until the awkward estimate
# falls outside it, which is what happened when the employment-level rows were
# excluded while the text claimed manufacturing employment as a finding.
BONF=[e['p'] for e in J('matched_results.json')['effects']] + \
     [e['p'] for e in J('matched_military.json')['effects']]
aj=mr['adjacency']
def _conley():
    """(Conley SE, clustered SE) per row, at full precision from the artifact,
    with an assertion that the typeset table rounds to the same values. The
    table prints four decimals and one pair ties there while differing in the
    fifth, so the count has to come from the JSON."""
    out=[]
    for blk in rb['conley']:
        for k in ('W_C','W_F','W_M','B'):
            out.append((blk[k]['se_conley'],blk[k]['se_cluster']))
    tab=[]
    for ln in (ROOT/'paper/tables/tabA_conley.tex').read_text().splitlines():
        if not ln.startswith('\\quad '): continue
        c=[x.strip() for x in ln.split('&')]
        tab.append((float(c[3]),float(c[2])))
    assert len(tab)==len(out) and all(
        abs(round(a,4)-c)<1e-9 and abs(round(b,4)-d)<1e-9
        for (a,b),(c,d) in zip(out,tab)), 'tabA_conley.tex disagrees with robustness.json'
    return out
def _adj_tab():
    """The neighbour row as typeset. A tolerance of 0.002 against the stored
    0.1805 let the manuscript print 0.181 while the table printed 0.180."""
    ls=(ROOT/'paper/tables/tabA_matchedrobust.tex').read_text().splitlines()
    co=[l for l in ls if l.startswith('\\quad Coefficient')][0]
    pv=[l for l in ls if l.startswith('\\quad $p$-value')][0]
    g=lambda l: float(re.sub(r'[^0-9.\-]','',l.split('&')[1]))
    return g(co),g(pv)
def fmt(x,d=3): return f'{x:.{d}f}'
# ---------------------------------------------------------------------------
# Per-section check modules. The audit covered 53.5 percent of the manuscript's
# numeric claims when this was written, and the uncovered remainder is where
# every sweep kept finding defects. Each file in src/audit_checks/ adds the
# checks for one part of the paper and is loaded into this namespace, so its
# conditions can use the artifacts already bound above.
def _load_extra():
    import pathlib as _pl
    out = []
    d = _pl.Path(__file__).resolve().parent / 'audit_checks'
    for f in sorted(d.glob('*.py')):
        ns = dict(globals())
        exec(compile(f.read_text(), str(f), 'exec'), ns)   # fail loudly, never silently
        got = [v for k, v in ns.items() if k.startswith('CHECKS_') and isinstance(v, list)]
        if not got:
            raise RuntimeError(f'{f.name} defines no CHECKS_* list')
        for g in got: out.extend(g)
    return out

CHECKS=[
 ('3{,}073 continental',            len(m)==3073,                       f'{len(m)}'),
 ('131.7 million residents',        abs(m.pop1940.sum()/1e6-131.7)<0.1, f'{m.pop1940.sum()/1e6:.1f}M'),
 ('300{,}131',                      DS1['rows_total']==300131,           f"{DS1['rows_total']}"),
 ('8{,}293{,}187',                  MR['enlistment_ds2']['rows_total']==8293187,
                                    f"{MR['enlistment_ds2']['rows_total']}"),
 ('190{,}693',                      MR['contracts']['rows_total']==190693 and
                                    len(pd.read_parquet(AN/'contracts_geocoded.parquet',columns=['fips']))==190693,
                                    f"{MR['contracts']['rows_total']}"),
 ('7{,}280{,}828',                  abs(m.ds2_enlist.sum()-7280828)/7280828<0.02,
                                    f'{m.ds2_enlist.sum():,.0f} decoded to a 1940 county'),
 ('= 0.466',                        abs(o['overlap_coefficient_A']-0.466)<0.001, fmt(o['overlap_coefficient_A'])),
 ('$0.338$ bits',                   abs(o['jensen_shannon_bits']-0.338)<0.001,   fmt(o['jensen_shannon_bits'])),
 ('98.2 percent',                   abs(100*(m.deaths_all.fillna(0)>0).mean()-98.2)<0.05,
                                    f"{100*(m.deaths_all.fillna(0)>0).mean():.2f}%"),
 ('48.5 percent',                   abs(100*(m.contract_k.fillna(0)>0).mean()-48.5)<0.05,
                                    f"{100*(m.contract_k.fillna(0)>0).mean():.2f}%"),
 ('1{,}553 counties lost men',      o['counties_deaths_no_contracts']==1553,  f"{o['counties_zero_contracts']} zero-contract"),
 ('43.8 percent of the contract',   abs(o['contracts_top20_share']-0.438)<0.002, f"{o['contracts_top20_share']:.3f}"),
 ('$-0.026$ for contracts',         abs(tg['percapita_vs_burden']['W_C']+0.026)<0.002, fmt(tg['percapita_vs_burden']['W_C'])),
 ('$-0.054$ for military',          abs(tg['percapita_vs_burden']['W_M']+0.0538)<0.0005 and
                                    _t5res()==(-0.026,0.013,-0.054),
                                    f"{tg['percapita_vs_burden']['W_M']:.4f} table {_t5res()}"),
 ('42.9 with a 90/10',              abs(ex['fatality_rate_national']-42.9)<0.1, fmt(ex['fatality_rate_national'],1)),
 ('ratio of $3.58$',                abs(ex['BA_p90_p10_ratio']-3.58)<0.01, fmt(ex['BA_p90_p10_ratio'])),
 ('at $-0.157$, $-0.067$ and $-0.187$ if investment is put',         abs(ex['overlap']['contracts W^C']['rho_per_enlistee']+0.157)<0.002, '-0.157'),
 ('$R^2 = 0.177$',                  abs(co['composition_R2']-0.177)<0.002, fmt(co['composition_R2'])),
 ('$-0.182$ for contracts',         abs(co['contracts']['rho_adjusted']+0.182)<0.002, fmt(co['contracts']['rho_adjusted'])),
 ('226 qualifying plants worth\n\\$8.61 billion, of which 214',
                                    FAC['n_qualifying']==226 and abs(FAC['qualifying_bn']-8.61)<0.01
                                    and FAC['n_located']==214,
                                    f"{FAC['n_qualifying']} / ${FAC['qualifying_bn']:.2f}bn / {FAC['n_located']}"),
 ('carry 93.9 percent of the qualifying dollars',
                                    abs(100*FAC['located_share_of_qualifying']-93.9)<0.05,
                                    f"{100*FAC['located_share_of_qualifying']:.2f}%"),
 ('\\$11.94 billion --- the 226 capture 72.1 percent',
                                    abs(FAC['all_new_bn']-11.94)<0.01 and
                                    abs(100*FAC['qualifying_share_of_all_new']-72.1)<0.05,
                                    f"${FAC['all_new_bn']:.2f}bn, {100*FAC['qualifying_share_of_all_new']:.1f}%"),
 ('118 are treated',                J('matched_design_setup.json')['sample_treated']==118,
                                    f"{J('matched_design_setup.json')['sample_treated']}"),
 ('115 of 118',                     mp['setup']['n_matched_treated']==115, str(mp['setup']['n_matched_treated'])),
 ('only two still do', mp['imbalanced_matched']==2,        f"{mp['imbalanced_matched']} imbalanced"),
 ('52 of the 54 match to 152 controls', mm['n_treated']==52 and mm['n_treated_design']==54,
                                    f"{mm['n_treated']} of {mm['n_treated_design']}"),
 ('$p = 0.66$',                     abs(mm['placebo'][0]['p']-0.66)<0.02, fmt(mm['placebo'][0]['p'],2)),
 ('$p = 0.63$',                     abs(mm['placebo'][1]['p']-0.63)<0.02, fmt(mm['placebo'][1]['p'],2)),
 ('55 log points against 21',       abs(me['log population 1970']['coef']-0.551)<0.01
                                    and abs(pe['log population 1970']['matched']-0.209)<0.01,
                                    f"{me['log population 1970']['coef']:.3f} vs {pe['log population 1970']['matched']:.3f}"),
 ('4.72 points where the plant\nraised it by 3.34', abs(me['manufacturing share 1970']['coef']+4.72)<0.02
                                    and abs(pe['manufacturing share 1970']['matched']-3.338)<0.02,
                                    f"{me['manufacturing share 1970']['coef']:.2f} / {pe['manufacturing share 1970']['matched']:.2f}"),
 ('the installation effect is $-7.49$ points and\nthe plant effect is a null',
                                    abs(me['homeownership 1970']['coef']+7.49)<0.02
                                    and pe['homeownership 1970']['p']>0.05,
                                    f"{me['homeownership 1970']['coef']:.2f} / plant p={pe['homeownership 1970']['p']:.3f}"),
 ('$0.000$ for population',         am['randomization'][0]['perm_p']<0.001, fmt(am['randomization'][0]['perm_p'])),
 ('$0.004$ for the manufacturing',  abs(am['randomization'][1]['perm_p']-0.004)<0.002, fmt(am['randomization'][1]['perm_p'])),
 ('63.6 for war\nplant',            abs(iv['first_stage'][2]['F']-63.6)<0.2, fmt(iv['first_stage'][2]['F'],1)),
 ('the population effect ($+0.180$, $p = 0.002$), the manufacturing',          abs(aj['log pop 1970']['coef']-0.181)<0.002
                                    and abs(aj['log pop 1970']['p']-0.002)<0.002,
                                    f"{aj['log pop 1970']['coef']:.3f} p={aj['log pop 1970']['p']:.3f}"),
 ('$+1.63$, $p = 0.022$',          abs(aj['mfg share 1970']['coef']-1.628)<0.01
                                    and abs(aj['mfg share 1970']['p']-0.022)<0.003,
                                    f"{aj['mfg share 1970']['coef']:.3f} p={aj['mfg share 1970']['p']:.3f}"),
 ('$+0.045$, $p = 0.012$',          abs(aj['log income 1970']['coef']-0.045)<0.002
                                    and abs(aj['log income 1970']['p']-0.012)<0.003,
                                    f"{aj['log income 1970']['coef']:.3f} p={aj['log income 1970']['p']:.3f}"),
 ('again indistinguishable from zero ($+0.40$,\n$p = 0.48$)',
                                    abs(aj['homeownership 1970']['coef']-0.397)<0.01
                                    and abs(aj['homeownership 1970']['p']-0.477)<0.005,
                                    f"{aj['homeownership 1970']['coef']:.3f} p={aj['homeownership 1970']['p']:.3f}"),
 # Was: anchor on 481, condition on aj['log pop 1970']['n']==273 -- a check on a
 # different quantity entirely, so any pool size from 1 up would have passed. It
 # is why 481 survived four sweeps. Same shape as the 1,553/1,583 case.
 ('control pool is restricted to the 475', mr['n_neighbour_pool']==475,
                                    f"pool={mr['n_neighbour_pool']}, treated={mr['n_treated_adjacency']}"),
 ('restricts the control pool to the 475 untreated counties', mr['n_neighbour_pool']==475,
                                    f"{mr['n_neighbour_pool']}"),
 ('111 of the 118 treated counties find a\nmatch inside it', aj['log pop 1970']['n']==273 and
                                    mr['n_treated_adjacency']==118,
                                    f"n={aj['log pop 1970']['n']}, treated={mr['n_treated_adjacency']}"),
 ('$0.193$ to $0.211$',             abs(min(s['log pop 1970']['coef'] for s in mr['params'])-0.193)<0.002
                                    and abs(max(s['log pop 1970']['coef'] for s in mr['params'])-0.211)<0.002,
                                    f"{min(s['log pop 1970']['coef'] for s in mr['params']):.3f}"
                                    f"-{max(s['log pop 1970']['coef'] for s in mr['params']):.3f}"),
 ('1970 population 23.3 percent',   abs((np.exp(pe['log population 1970']['matched'])-1)*100-23.3)<0.2,
                                    f"{(np.exp(pe['log population 1970']['matched'])-1)*100:.1f}%"),
 ('3.34 points higher',             abs(pe['manufacturing share 1970']['matched']-3.338)<0.02,
                                    fmt(pe['manufacturing share 1970']['matched'],2)),
 ('income 7.3 percent',             abs((np.exp(pe['log family income 1970']['matched'])-1)*100-7.3)<0.2,
                                    f"{(np.exp(pe['log family income 1970']['matched'])-1)*100:.1f}%"),
 ('the point\nestimate is $+0.94$ points with a standard error of $0.61$',
                                    abs(pe['homeownership 1970']['matched']-0.942)<0.01
                                    and abs(pe['homeownership 1970']['se']-0.612)<0.01
                                    and pe['homeownership 1970']['p']>0.05,
                                    f"{pe['homeownership 1970']['matched']:.2f} ({pe['homeownership 1970']['se']:.2f}) p={pe['homeownership 1970']['p']:.3f}"),
 ('249 distinct controls',          int((pd.read_parquet(AN/'matched_sample.parquet',columns=['treat','mweight'])
                                        .query('treat==0 and mweight>0')).shape[0])==249,
                                    f"{int((pd.read_parquet(AN/'matched_sample.parquet',columns=['treat','mweight']).query('treat==0 and mweight>0')).shape[0])}"),
 # E_A is Ferrara's tabulation via Garin-Rothbaum, not the DS2 decode. The
 # manuscript credited DS2 with the denominator for several drafts; these two
 # checks pin the distinction to the artifact.
 # the coverage-cutoff disclosure quotes two figures off the availability field
 ('\\$7.0 billion of public plant in 1943', abs(FAC['pub_1943_bn']-7.0)<0.05,
                                    f"${FAC['pub_1943_bn']:.2f}bn"),
 ('billion in 1944',                abs(FAC['pub_1944_bn']-4.6)<0.05,    f"${FAC['pub_1944_bn']:.2f}bn"),
 # These two are properties of external documents, not of any file this
 # pipeline builds, so presence in the manuscript is all that can be checked.
 ('authorized \\emph{through October 1944}', True,                        'WPB volume cutoff, not computable here'),
 ('totals 6.94 million men',        abs(m.E_A.sum()/1e6-6.94)<0.01,       f'{m.E_A.sum()/1e6:.2f}M (E_A)'),
 ('reach 7.19 million',             abs(m.ds2_enlist.sum()/1e6-7.19)<0.01, f'{m.ds2_enlist.sum()/1e6:.2f}M (DS2 decode)'),
 ('a national rate of\n42.9',       abs(1000*m.deaths_all.sum()/m.E_A.sum()-42.9)<0.1,
                                    f'{1000*m.deaths_all.sum()/m.E_A.sum():.1f} per 1,000 on E_A'),
 # the DS1/DS3 non-additivity argument, sourced to each list's own documentation
 ('combat and prison camp, with no non-battle column', True,              'CRS Table 27 columns, not computable here'),
 ('27.5 percent of entries are non-battle',
                                    abs(100*DS1['status_counts']['DNB']/DS1['rows_total']-27.5)<0.05,
                                    f"{100*DS1['status_counts']['DNB']/DS1['rows_total']:.2f}%"),
 ('43.8 percent of the contract dollars',
                                    abs(m.nlargest(20,'contract_k').contract_k.sum()/m.contract_k.sum()-0.438)<0.002,
                                    f"{m.nlargest(20,'contract_k').contract_k.sum()/m.contract_k.sum():.1%} (ranked by contracts)"),
 ('hold 20.4 percent of the dead',  abs(m.nlargest(20,'deaths_all').deaths_all.sum()/m.deaths_all.sum()-0.204)<0.002,
                                    f"{m.nlargest(20,'deaths_all').deaths_all.sum()/m.deaths_all.sum():.1%} (ranked by deaths)"),
 ('14{,}681 plant records',         FAC['records']==14681,               f"{FAC['records']}"),
 ('\\$20.8 billion, of\nwhich 76.6', abs(FAC['total_bn']-20.8)<0.05 and
                                    abs(100*FAC['public_share']-76.6)<0.05,
                                    f"${FAC['total_bn']:.2f}bn, {100*FAC['public_share']:.1f}% public"),
 ('97.8 percent of the\nassignable', abs(100*FAC['assignable_located_share']-97.8)<0.05,
                                    f"{100*FAC['assignable_located_share']:.2f}%"),
 ('180 facilities holding \\$0.59 billion---3.7 percent',
                                    FAC['noplace_n']==180 and abs(100*FAC['noplace_share']-3.7)<0.05,
                                    f"{FAC['noplace_n']} / {100*FAC['noplace_share']:.2f}%"),
 ('fifteen survive a\nBonferroni correction for the full set of tests at $0.05/18 = 0.0028$',
                                    len(BONF)==18 and sum(1 for x in BONF if x<0.05/18)==15,
                                    f"{sum(1 for x in BONF if x<0.05/18)}/{len(BONF)} survive"),
 ('the three\nthat do not are the plant effect on homeownership ($p = 0.124$), the military\neffect on manufacturing employment ($p = 0.103$) and the military\neffect on the 1960 manufacturing share ($p = 0.075$)',
                                    sorted(round(x,3) for x in BONF if x>=0.05/18)==[0.075,0.103,0.124],
                                    f"{sorted(round(x,3) for x in BONF if x>=0.05/18)}"),
 ('\\textbf{None of the nine is usable.}', imp['n_usable']==0 and imp['n_specs']==9,
                                    f"{imp['n_usable']}/{imp['n_specs']} usable"),
 ('manufacturing share ($p = 0.16$)', abs(ISP['Aeronautical branch only']['placebo']['1940 manufacturing share']-0.162)<0.005,
                                    fmt(ISP['Aeronautical branch only']['placebo']['1940 manufacturing share'],3)),
 ('1940 urban share ($p = 0.21$)',  abs(ISP['Aeronautical branch only']['placebo']['1940 urban share']-0.212)<0.005,
                                    fmt(ISP['Aeronautical branch only']['placebo']['1940 urban share'],3)),
 ('partial $R^2$ is $0.003$',       abs(ISP['Aeronautical branch only']['partial_r2']-0.003)<0.001,
                                    fmt(ISP['Aeronautical branch only']['partial_r2'],4)),
 ('any allocated facility at a partial $R^2$ of $0.055$',
                                    abs(ISP['Any allocated facility (extensive margin)']['partial_r2']-0.055)<0.002,
                                    fmt(ISP['Any allocated facility (extensive margin)']['partial_r2'],3)),
 ('gives $-3.63$ ($p = 0.46$)',     abs(GP['enlistees per 1,000 residents']['coef']+3.626)<0.02
                                    and abs(GP['enlistees per 1,000 residents']['p']-0.463)<0.01,
                                    f"{GP['enlistees per 1,000 residents']['coef']:.3f} p={GP['enlistees per 1,000 residents']['p']:.3f}"),
 ('gives $+2.56$ ($p = 0.79$)',     abs(GP['deaths per 1,000 enlistees']['coef']-2.559)<0.02
                                    and abs(GP['deaths per 1,000 enlistees']['p']-0.786)<0.01,
                                    f"{GP['deaths per 1,000 enlistees']['coef']:.3f} p={GP['deaths per 1,000 enlistees']['p']:.3f}"),
 ('$10.2$ more enlistees\nper thousand residents than their controls ($p = 0.033$)',
                                    abs(GM['enlistees per 1,000 residents']['coef']-10.154)<0.05
                                    and abs(GM['enlistees per 1,000 residents']['p']-0.033)<0.005,
                                    f"{GM['enlistees per 1,000 residents']['coef']:.2f} p={GM['enlistees per 1,000 residents']['p']:.3f}"),
 ('4.6 percent against 7.3 percent',
                                    abs((np.exp(aj['log income 1970']['coef'])-1)*100-4.6)<0.2,
                                    f"{(np.exp(aj['log income 1970']['coef'])-1)*100:.1f}%"),
 # ---- construction and validation block ----------------------------------
 # Everything below was added after a pass found that the validation paragraph
 # quoted a correlation, a concentration share and two county counts that no
 # sample reproduced. These recompute from the panel rather than reading a JSON,
 # so a stale intermediate cannot make them pass.
 ('the levels correlation is $0.992$',   abs(VAL['pearson']-0.992)<0.001,  fmt(VAL['pearson'])),
 ('correlates with that series at $0.992$', abs(VAL['pearson']-0.992)<0.001, fmt(VAL['pearson'])),
 ('national totals differ by 1.7 percent', abs(VAL['pct_diff']-1.70)<0.05,  f"{VAL['pct_diff']:.2f}%"),
 ('($44.0$ against $42.7$ percent)',     abs(VAL['top20_recon']-43.96)<0.05
                                         and abs(VAL['top20_cdb']-42.71)<0.05,
                                         f"{VAL['top20_recon']:.2f} vs {VAL['top20_cdb']:.2f}"),
 ('the 3{,}070 counties both series cover', VAL['n']==3070,               f"{VAL['n']}"),
 ("against the older series' 42.7 percent", abs(VAL['top20_cdb']-42.71)<0.05, f"{VAL['top20_cdb']:.2f}"),
 ('1{,}583 counties with no major contract', VAL['zero_recon']==1583,     f"{VAL['zero_recon']}"),
 ("County Data Book's 1{,}506",          VAL['zero_cdb']==1506,           f"{VAL['zero_cdb']}"),
 ('2{,}412 received no publicly financed plant', VAL['zero_plant']==2412, f"{VAL['zero_plant']}"),
 ('landing in 661 of them',              VAL['counties_pubplant']==661,   f"{VAL['counties_pubplant']}"),
 ('the correlation is $0.969$',          abs(VAL['pearson_fac']-0.969)<0.001, fmt(VAL['pearson_fac'])),
 ('\\$6.82 billion in contracts',        abs(VAL['ic_contracts_bn']-6.82)<0.01, f"{VAL['ic_contracts_bn']:.3f}bn"),

 # ---- sample sizes and shares the manuscript states in prose --------------
 ('the 2{,}976 counties passing the validity', ex['n_valid_BA']==2976, f"{ex['n_valid_BA']}"),
 ('Of the 2{,}973 counties in the sample, 118 received a large public',
                                         J('matched_design_setup.json')['sample_n']==2973,
                                         f"{J('matched_design_setup.json')['sample_n']}"),
 ('Restricting to the 2{,}966 counties',  co['n']==2966,                   f"{co['n']}"),
 ('the two figures are\n40.7 and 81.3 percent',
                                         abs(100*o['deaths_top100_share']-40.7)<0.05 and
                                         abs(100*o['contracts_top100_share']-81.3)<0.05,
                                         f"{100*o['deaths_top100_share']:.1f} / {100*o['contracts_top100_share']:.1f}"),
 ('The two correlate at $0.628$',        abs(ex['spearman_BA_Bcivic']-0.628)<0.002, fmt(ex['spearman_BA_Bcivic'])),
 ('it ($\\rho = -0.629$)',     abs(ex['spearman_mob_BA']+0.629)<0.002,    fmt(ex['spearman_mob_BA'])),
 ('205{,}000 individual\nwartime contract', abs(MR['contracts']['rows_total']+FAC['records']-205000)<600,
                                         f"{MR['contracts']['rows_total']+FAC['records']:,}"),

 # ---- the two contract totals must name their own bases -------------------
 ('recovers \\$178.2 billion, of which \\$177.3 billion falls in the 3{,}070 counties',
                                         abs(m.contract_k.fillna(0).sum()/1e6-178.2)<0.05 and
                                         abs(VAL['recon_on_cdb_bn']-177.3)<0.05 and VAL['n']==3070,
                                         f"{m.contract_k.fillna(0).sum()/1e6:.2f} / {VAL['recon_on_cdb_bn']:.2f} / {VAL['n']}"),
 ("series' \\$180.4 billion",             abs(VAL['cdb_bn']-180.4)<0.05, f"{VAL['cdb_bn']:.2f}"),

 # ---- DS1: the death total must reconcile to the source count ------------
 ('sorts 299{,}947 of the 300{,}131 records',  DS1['status_coded']==299947 and
                                         DS1['rows_total']==300131,
                                         f"{DS1['status_coded']} of {DS1['rows_total']}"),
 ('killed in action (171{,}530 records, 57.2 percent)', DS1['status_counts']['KIA']==171530 and
                                         abs(100*DS1['status_counts']['KIA']/DS1['rows_total']-57.2)<0.05,
                                         f"{DS1['status_counts']['KIA']}"),
 ('(82{,}479, 27.5 percent)',            DS1['status_counts']['DNB']==82479,  f"{DS1['status_counts']['DNB']}"),
 ('(24{,}786, 8.3 percent)',             DS1['status_counts']['DOW']==24786,  f"{DS1['status_counts']['DOW']}"),
 ('(18{,}888, 6.3 percent)',             DS1['status_counts']['FOD']==18888,  f"{DS1['status_counts']['FOD']}"),
 ('(912, 0.3 percent)',                  DS1['status_counts']['DOI']==912,    f"{DS1['status_counts']['DOI']}"),
 ('(1{,}352, 0.5 percent)',              DS1['status_counts']['M']==1352,     f"{DS1['status_counts']['M']}"),
 ('184 records carry no status code',    DS1['status_counts']['']==184,       f"{DS1['status_counts']['']}"),
 ('299{,}416\n(99.76 percent) carry a resolvable county; 715 do not',
                                         DS1['rows_with_fips']==299416 and DS1['rows_unassigned']==715
                                         and abs(100*DS1['fips_rate']-99.76)<0.01,
                                         f"{DS1['rows_with_fips']} / {DS1['rows_unassigned']}"),
 ('297{,}887 hold one of the five statuses', DS1['assigned_deaths']==297887, f"{DS1['assigned_deaths']}"),
 ('1{,}348 are carried as missing and 181 have no status',
                                         DS1['assigned_missing']==1348 and DS1['assigned_no_status']==181,
                                         f"{DS1['assigned_missing']} / {DS1['assigned_no_status']}"),
 ('further 260 fall in county codes',    DS1['assigned_deaths']-int(m.deaths_all.sum())==260,
                                         f"{DS1['assigned_deaths']-int(m.deaths_all.sum())}"),
 ('is therefore 297{,}627 Army/AAF deaths, of which 195{,}677',
                                         int(m.deaths_all.sum())==297627 and int(m.deaths_battle.sum())==195677,
                                         f"{int(m.deaths_all.sum())} / {int(m.deaths_battle.sum())}"),
 ('flag, set on 234{,}386 of its records', MR['enlistment_ds2']['total_killed_flag']==234386,
                                         f"{MR['enlistment_ds2']['total_killed_flag']}"),

 # ---- three allocations ---------------------------------------------------
 ('Of the 1{,}010',                      sum(tg['conditional']['counties'].values())==1010,
                                         f"{sum(tg['conditional']['counties'].values())}"),
 ('386 received publicly financed plant only',  tg['conditional']['counties']['plant only']==386,
                                         f"{tg['conditional']['counties']['plant only']}"),
 ('$\\mathcal{A} = 0.413$',              abs(tg['pairwise']['W_F x D']['A']-0.4132)<0.001,
                                         fmt(tg['pairwise']['W_F x D']['A'],4)),
 ('$+0.013$ for industrial plant',       abs(tg['percapita_vs_burden']['W_F']-0.0131)<0.0005,
                                         fmt(tg['percapita_vs_burden']['W_F'],4)),
 ('34.2 percent of the lowest-burden',   abs(tg['plant_share_low_burden_q']-0.3424)<0.002,
                                         fmt(tg['plant_share_low_burden_q'])),
 ('against 54.9 percent of the highest', abs(tg['plant_share_high_burden_q']-0.5489)<0.002,
                                         fmt(tg['plant_share_high_burden_q'])),
 ('$0.0002$ with a standard error of $0.0029$ and $p = 0.95$',           abs(tg['plant_vs_base_controlled']['p']-0.951)<0.005 and
                                         abs(tg['plant_vs_base_controlled']['coef']-0.0002)<0.00005 and
                                         abs(tg['plant_vs_base_controlled']['se']-0.0029)<0.00005,
                                         f"p={tg['plant_vs_base_controlled']['p']:.3f}"),

 # ---- postwar divergence: prose must match Table 6, not an adjacent run ----
 ('$1.70$ points higher in 1970',        abs(rb['extensive']['any_F']['coef']-1.705)<0.01,
                                         fmt(rb['extensive']['any_F']['coef'])),
 ('$3.72$ points lower',                 abs(rb['extensive']['any_M']['coef']+3.725)<0.005,
                                         fmt(rb['extensive']['any_M']['coef'])),
 ('enters at $-0.34$',                   abs(T6['Military']+0.3360)<0.001,   fmt(T6['Military'],4)),
 ('industrial plant enters at $+0.06$',  abs(T6['War plant']-0.0558)<0.001,          fmt(T6['War plant'],4)),
 ('contracts at $-0.05$',                abs(T6['Contracts']+0.0480)<0.001,   fmt(T6['Contracts'],4)),

 # ---- composition ---------------------------------------------------------
 ('$-0.119$ for\nindustrial plant',      abs(co['war plant']['rho_adjusted']+0.1188)<0.001,
                                         fmt(co['war plant']['rho_adjusted'])),
 ('from $-0.178$ to $-0.083$',           abs(co['military']['rho_raw']+0.1784)<0.001
                                         and abs(co['military']['rho_adjusted']+0.0832)<0.001,
                                         f"{co['military']['rho_raw']:.4f} -> {co['military']['rho_adjusted']:.4f}"),

 # ---- source limitations --------------------------------------------------
 ('56 of 3{,}073 counties carry no',     VAL['zero_death_counties']==56,   f"{VAL['zero_death_counties']}"),
 ('1.90 per thousand residents',         abs(VAL['il_rate']-1.901)<0.005,  fmt(VAL['il_rate'])),
 ('against a\nnational 2.26',            abs(VAL['nat_rate']-2.2604)<0.005, fmt(VAL['nat_rate'])),
 ('3.61 per thousand, the highest of any state',
                                         abs(VAL['nm_rate']-3.606)<0.005 and VAL['nm_is_top_state'],
                                         f"{VAL['nm_rate']:.3f} top-state={VAL['nm_is_top_state']}"),

 # ---- treatment construction ---------------------------------------------
 ('226 qualifying plants worth\n\\$8.61 billion', abs(VAL['bigpub_all_bn']-8.609)<0.01,
                                         f"{VAL['bigpub_all_bn']:.3f}bn"),
 ('Fifty-six counties clear the\nthreshold; two of them also received a large public plant',
                                         mm['n_treated_predrop']==56 and
                                         mm['n_treated_predrop']-mm['n_treated_design']==2,
                                         f"{mm['n_treated_predrop']} predrop, {mm['n_treated_design']} design"),
 ('Those 54 hold \\$2.01 billion, 25 percent of the military\nfacility dollars in the sample they are drawn from and 20 percent of the\nnational total',
                                         mm['n_treated_design']==54 and
                                         round(mm['treated_dollars_bn_design'],2)==2.01 and
                                         round(100*mm['treated_share_sample_design'])==25 and
                                         round(100*mm['treated_share_national_design'])==20,
                                         f"n={mm['n_treated_design']} ${mm['treated_dollars_bn_design']:.2f}bn "
                                         f"{mm['treated_share_sample_design']:.3f}/{mm['treated_share_national_design']:.3f}"),
 ('$-4.31$ at the top twenty percent',   abs(am['thresholds'][2]['mfg share']['coef']+4.306)<0.01,
                                         fmt(am['thresholds'][2]['mfg share']['coef'])),
 ('$-4.61$ at the\ntop thirty',          abs(am['thresholds'][3]['mfg share']['coef']+4.611)<0.01,
                                         fmt(am['thresholds'][3]['mfg share']['coef'])),

 # ---- p-values that were quoted from an earlier run ----------------------
 ('($p = 0.45$, $0.73$,\n$0.81$)',        [round(r['p'],2) for r in ex['allocation_BA']]==[0.45,0.73,0.81],
                                         ' '.join(f"{r['p']:.4f}" for r in ex['allocation_BA'])),
 ('($p = 0.66$) and the 1940 manufacturing share ($p = 0.81$)',
                                         round(mp['placebo'][0]['p'],2)==0.66
                                         and round(mp['placebo'][1]['p'],2)==0.81,
                                         f"{mp['placebo'][0]['p']:.3f} / {mp['placebo'][1]['p']:.3f}"),
 ('homeownership rate $1.27$ points above their matched controls, at $p = 0.11$',
                                         round(mp['placebo'][2]['coef'],2)==1.27
                                         and round(mp['placebo'][2]['p'],2)==0.11,
                                         f"{mp['placebo'][2]['coef']:.4f} p={mp['placebo'][2]['p']:.4f}"),
 ('larger in\nmagnitude than the $+0.94$ the same design estimates for 1970',
                                         mp['placebo'][2]['coef'] >
                                         [e for e in mp['effects'] if e['outcome']=='homeownership 1970'][0]['matched'],
                                         f"placebo {mp['placebo'][2]['coef']:.4f} > effect "
                                         f"{[e for e in mp['effects'] if e['outcome']=='homeownership 1970'][0]['matched']:.4f}"),
 # The prose quotes Table 5's per-enlistee row, so this checks the artifact and
 # the typeset row together: the two disagreed for a month while both were right
 # about their own quantity.
 ('$-0.182$ for contracts, $-0.074$ for plant and $-0.193$ for',
                                         abs(BENL['W_C']['rho']+0.1821)<0.001 and
                                         abs(BENL['W_F']['rho']+0.0736)<0.001 and
                                         abs(BENL['W_M']['rho']+0.1934)<0.001 and
                                         _t5row()==(-0.182,-0.074,-0.193),
                                         f"{BENL['W_C']['rho']} {BENL['W_F']['rho']} {BENL['W_M']['rho']}"
                                         f"  table {_t5row()}"),
 ('$-0.067$ and $-0.187$ if investment is put\non a per-enlistee footing',
                                         abs(ex['overlap']['war plant W^F']['rho_per_enlistee']+0.0672)<0.001 and
                                         abs(ex['overlap']['military installations W^M']['rho_per_enlistee']+0.1871)<0.001,
                                         f"{ex['overlap']['war plant W^F']['rho_per_enlistee']} "
                                         f"{ex['overlap']['military installations W^M']['rho_per_enlistee']}"),

 # ---- IV block, recomputed rather than asserted in a docstring -----------
 ('is $0.030$ for contracts and\n$0.013$ for military installations',
                                         abs(PR2['W_C']-0.0296)<0.001 and abs(PR2['W_M']-0.0125)<0.001,
                                         f"{PR2['W_C']:.4f} / {PR2['W_M']:.4f}"),
 ('Only war plant, at\n$0.069$',         abs(PR2['W_F']-0.0694)<0.001, fmt(PR2['W_F'],4)),
 ('coefficient of $-5.29$',              abs(IVH['war plant, instrumented by IMP industrial']+5.2921)<0.005,
                                         fmt(IVH['war plant, instrumented by IMP industrial'],4)),
 ('alone gives $-8.95$',                abs(IVH['contracts, instrumented by IMP facilities']+8.9496)<0.005,
                                         fmt(IVH['contracts, instrumented by IMP facilities'],4)),
 ('installations alone gives $-7.44$',  abs(IVH['military, instrumented by prewar bases']+7.4356)<0.005 and
                                         _t14()==(-5.2921,-8.9496,-7.4356),
                                         fmt(IVH['military, instrumented by prewar bases'],4)),
 ('and 18.9 for military installations', abs(iv['first_stage'][4]['F']-18.86)<0.02,
                                         fmt(iv['first_stage'][4]['F'],2)),
 # ---- Table 5 must not contradict the sentence pointing at it ------------
 ('$0.024$ for contracts, $0.016$ for plant and\n$0.009$ for military installations',
                                         all(abs(a-b)<0.0015 for a,b in
                                         zip(T5SPREAD,[0.0242,0.0162,0.0089])),
                                         ' '.join(f'{x:.4f}' for x in T5SPREAD)),
 ('$0.193$ and $0.217$ across all seven',
                                         abs(MRB_MIN-0.193)<0.001 and abs(MRB_MAX-0.217)<0.001,
                                         f"{MRB_MIN:.3f}-{MRB_MAX:.3f}"),
 # ---- the allocation-criteria exhibit ------------------------------------
 ('at $+0.693$',                   abs(ACR['1940 manufacturing share']['W_C']['rho']-0.693)<0.002,
                                   fmt(ACR['1940 manufacturing share']['W_C']['rho'])),
 ('the 1940 urban share at $+0.648$', abs(ACR['1940 urban share']['W_C']['rho']-0.648)<0.002,
                                   fmt(ACR['1940 urban share']['W_C']['rho'])),
 ('1940 log population at\n$+0.666$', abs(ACR['1940 log population']['W_C']['rho']-0.666)<0.002,
                                   fmt(ACR['1940 log population']['W_C']['rho'])),
 ('$+0.23$ to $+0.51$',            abs(min(ACR[r][k]['rho'] for r in ('1940 manufacturing share',
                                        '1940 urban share','1940 log population')
                                        for k in ('W_F','W_M'))-0.233)<0.003
                                   and abs(max(ACR[r][k]['rho'] for r in ('1940 manufacturing share',
                                        '1940 urban share','1940 log population')
                                        for k in ('W_F','W_M'))-0.514)<0.006,
                                   f"{min(ACR[r][k]['rho'] for r in ('1940 manufacturing share','1940 urban share','1940 log population') for k in ('W_F','W_M')):.3f}"
                                   f" to {max(ACR[r][k]['rho'] for r in ('1940 manufacturing share','1940 urban share','1940 log population') for k in ('W_F','W_M')):.3f}"),
 ('exclude any association above $0.09$',
                                   max(abs(v) for r in ('fatal burden, per resident',)
                                       for k in ACR[r] for v in ACR[r][k]['ci'])<0.09,
                                   f"widest |CI bound| = {max(abs(v) for k in ACR['fatal burden, per resident'] for v in ACR['fatal burden, per resident'][k]['ci']):.3f}"),
 ('$\\mathcal{A}(D, P) = 0.874$',   abs(ACD['contracts_prop_to_pop']-0.8744)<0.001,
                                   fmt(ACD['contracts_prop_to_pop'],4)),
 ('\\emph{people} and contracts, which is $0.498$',
                                   abs(ACD['deaths_prop_to_pop']-0.4979)<0.001,
                                   fmt(ACD['deaths_prop_to_pop'],4)),
 ('$0.455$ of it, 85 percent',    abs(ACD['shapley_contract_share']-0.8527)<0.005 and
                                    abs(ACD['shapley_contract_level']-0.4551)<0.001 and
                                    abs(ACD['shapley_contract_level']+ACD['shapley_death_level']
                                        -(1-ACD['observed']))<1e-3,
                                   f"{ACD['share_from_contract_concentration']:.3f}"),
 ('Only $0.079$, 15 percent',      abs(ACD['shapley_death_share']-0.1473)<0.005 and
                                    abs(ACD['shapley_death_level']-0.0786)<0.001,
                                   f"{ACD['share_from_death_deviation']:.3f}"),
 ('lies 37 standard deviations below',
                                   abs(J('allocation_criteria.json')['poisson_null']['z_of_observed']-36.6)<0.3,
                                   f"z={J('allocation_criteria.json')['poisson_null']['z_of_observed']}"),
 ('8.6 million individual military records',
                                         (300131+8293187)/1e6 > 8.55 and (300131+8293187)/1e6 < 8.65,
                                         f"{(300131+8293187)/1e6:.2f}M"),
 ('Ninety-seven of the 3{,}073 counties fail it, holding\n2.55 percent of the 1940 population',
                                   ex['excluded']==97 and ex['n_total']==3073 and
                                   round(100*ex['excluded_pop_share'],2)==2.55,
                                   f"{ex['excluded']} of {ex['n_total']}, "
                                   f"{100*ex['excluded_pop_share']:.2f}% of population"),
 ('computed on the surviving 2{,}976', ex['n_valid_BA']==2976, f"{ex['n_valid_BA']}"),

 ('The largest movement is\n$+0.018$, on the contract coefficient for the 1960 manufacturing share\n($0.459$ to $0.477$)',
                                   round(IL['max_abs_change'],3)==0.018 and
                                   IL['max_abs_change_at']=='Mfg. share 1960 W_C' and
                                   round(IL['table1']['Mfg. share 1960']['W_C']['full'],3)==0.459 and
                                   round(IL['table1']['Mfg. share 1960']['W_C']['no_IL'],3)==0.477,
                                   f"{IL['max_abs_change']} at {IL['max_abs_change_at']}"),
 ('$\\mathcal{A}$ shifts from $0.466$ to $0.454$',
                                   round(IL['overlap_full'],3)==0.466 and
                                   round(IL['overlap_noIL'],3)==0.454,
                                   f"{IL['overlap_full']} -> {IL['overlap_noIL']}"),

 ('the Army General Classification Test score for the 447{,}464\nrecords --- 5.4 percent --- that carry one',
                                   cmp_['agct_coverage']['records_with_agct']==447464 and
                                   round(100*cmp_['agct_coverage']['share'],1)==5.4,
                                   f"{cmp_['agct_coverage']['records_with_agct']:,} of "
                                   f"{cmp_['agct_coverage']['records_total']:,} "
                                   f"({100*cmp_['agct_coverage']['share']:.2f}%)"),
 ('Army General Classification Test score for 5.4 percent\nof them',
                                   round(100*cmp_['agct_coverage']['share'],1)==5.4,
                                   f"{100*cmp_['agct_coverage']['share']:.2f}%"),
 ('139 counties carry no scored record at all and take\nthe sample median',
                                   cmp_['agct_coverage']['counties_no_agct']==139,
                                   f"{cmp_['agct_coverage']['counties_no_agct']} counties"),

 # This sentence is stated twice -- Section 5.8 and the Conclusion -- so the
 # check asserts both occurrences, not just the first one it finds.
 ('plant and 56 a top-decile installation, and only two received both --- against',
                                   (lambda I: I['n_sample']==2973 and I['n_plant']==118 and
                                              I['n_mil']==56 and I['n_both']==2 and
                                              round(I['expected_both'],1)==2.2)(mm['independence'])
                                   and tex.count('plant and 56 a top-decile installation, '
                                                 'and only two received both --- against')==2,
                                   f"{mm['independence']}; stated "
                                   f"{tex.count('plant and 56 a top-decile installation, and only two received both --- against')}x"),
 ('Fisher\nexact $p = 1.00$', round(mm['independence']['fisher_p'],2)==1.00,
                                   f"{mm['independence']['fisher_p']}"),
 ('52 of the 54 match to 152 controls, and\nthe treated counties are spread across 27 states with at most four in any one',
                                   mm['n_matched_controls']==152 and mm['states_treated']==27 and
                                   mm['max_treated_per_state']==4,
                                   f"{mm['n_matched_controls']} controls, {mm['states_treated']} states, "
                                   f"max {mm['max_treated_per_state']}"),

 # ---- Oster sensitivity bounds --------------------------------------------
 ('$\\delta$ is $3.50$ for the manufacturing share and $1.51$ for family income',
                                   abs(_ob('plant','manufacturing share 1970','delta_13')-3.50)<0.005 and
                                   abs(_ob('plant','log family income 1970','delta_13')-1.51)<0.005,
                                   f"{_ob('plant','manufacturing share 1970','delta_13')} / "
                                   f"{_ob('plant','log family income 1970','delta_13')}"),
 ('but $0.98$ for population and\n$0.86$ for manufacturing employment',
                                   abs(_ob('plant','log population 1970','delta_13')-0.98)<0.005 and
                                   abs(_ob('plant','log manufacturing employment 1970','delta_13')-0.86)<0.005,
                                   f"{_ob('plant','log population 1970','delta_13')} / "
                                   f"{_ob('plant','log manufacturing employment 1970','delta_13')}"),
 ('Under the stricter\n$R^2_{\\max}=1$ only the manufacturing share survives',
                                   sum(1 for r in OB['plant']
                                       if r['outcome'] != 'homeownership 1970'
                                       and r['delta_1'] > 1) == 1 and
                                   _ob('plant','manufacturing share 1970','delta_1') > 1,
                                   f"{[(r['outcome'], r['delta_1']) for r in OB['plant']]}"),
 ('raw plant-county gap in 1970 log population is $1.78$, and the prewar vector\nalone takes it to $0.23$',
                                   abs(_ob('plant','log population 1970','beta_uncontrolled')-1.78)<0.005 and
                                   abs(_ob('plant','log population 1970','beta_controlled')-0.23)<0.005,
                                   f"{_ob('plant','log population 1970','beta_uncontrolled')} -> "
                                   f"{_ob('plant','log population 1970','beta_controlled')}"),
 ('For population ($-19.9$) and family income ($-26.4$) $\\delta$ is\nnegative',
                                   abs(_ob('military','log population 1970','delta_1')+19.9)<0.05 and
                                   abs(_ob('military','log family income 1970','delta_13')+26.4)<0.05,
                                   f"{_ob('military','log population 1970','delta_1')} / "
                                   f"{_ob('military','log family income 1970','delta_13')}"),
 ('$\\delta$ is $4.70$ and $23.25$, and remains above one at $R^2_{\\max}=1$ ($1.66$\nand $4.32$)',
                                   all(abs(_ob('military',o,k)-v)<0.005 for o,k,v in [
                                       ('manufacturing share 1970','delta_13',4.70),
                                       ('homeownership 1970','delta_13',23.25),
                                       ('manufacturing share 1970','delta_1',1.66),
                                       ('homeownership 1970','delta_1',4.32)]),
                                   f"{_ob('military','manufacturing share 1970','delta_13')} "
                                   f"{_ob('military','homeownership 1970','delta_13')} "
                                   f"{_ob('military','manufacturing share 1970','delta_1')} "
                                   f"{_ob('military','homeownership 1970','delta_1')}"),

 # ---- the shift-share instrument and why it fails -------------------------
 ('gives a materially stronger instrument, $F = 45.1$ against $19.7$ and',
                                   abs(SSA['F']-45.1)<0.15 and abs(SSI['F']-19.7)<0.15,
                                   f"{SSA['F']} vs {SSI['F']}"),
 ('a partial $R^2$ of $0.039$ against $0.014$',
                                   abs(SSA['partial_r2']-0.0385)<0.0006 and
                                   abs(SSI['partial_r2']-0.0141)<0.0006,
                                   f"{SSA['partial_r2']} vs {SSI['partial_r2']}"),
 ('still fails all three level\nplacebos at $p<0.001$',
                                   max(SSA['placebo'][k] for k in
                                       ('1940 mfg share','1940 urban share','1940 log population'))<0.001,
                                   f"max p = {max(SSA['placebo'][k] for k in ('1940 mfg share','1940 urban share','1940 log population'))}"),
 ('textiles at a partial $R^2$ of $0.037$ and machine tools at $0.032$',
                                   abs(ROT['textiles']['partial_r2']-0.0366)<0.0015 and
                                   abs(ROT['machinetool']['partial_r2']-0.0316)<0.0015,
                                   f"{ROT['textiles']['partial_r2']} {ROT['machinetool']['partial_r2']}"),
 ('\\$51.9 billion the largest class in the file, contributes $0.0001$',
                                   abs(ROT['aircraft']['national_bn']-51.85)<0.1 and
                                   ROT['aircraft']['partial_r2']<0.0005 and
                                   ROT['aircraft']['national_bn']==max(r['national_bn'] for r in SS['rotemberg']),
                                   f"{ROT['aircraft']['national_bn']}bn r2={ROT['aircraft']['partial_r2']}"),
 ('Forty-three counties held an aircraft establishment in 1940\nand 317 received aircraft contracts',
                                   GF['aircraft']['prewar_counties']==43 and
                                   GF['aircraft']['counties_receiving']==317,
                                   f"{GF['aircraft']['prewar_counties']} / {GF['aircraft']['counties_receiving']}"),
 ('27.9 percent of aircraft dollars went to\ncounties with no prewar aircraft plant at all, 77.2 percent of ammunition\ndollars, 78.7 percent of small-arms dollars and 89.0 percent of explosives\ndollars',
                                   all(abs(100*GF[k]['greenfield_dollar_share']-v)<0.1 for k,v in
                                       [('aircraft',27.9),('ammunition',77.2),('firearms',78.7),('explosives',89.0)]),
                                   ' '.join(f"{k}={100*GF[k]['greenfield_dollar_share']:.1f}" for k in
                                            ('aircraft','ammunition','firearms','explosives'))),
 ('5.3\npercent of machine-tool dollars and 14.2 percent of textile dollars went to\ncounties without a plant of the kind',
                                   abs(100*GF['machinetool']['greenfield_dollar_share']-5.3)<0.1 and
                                   abs(100*GF['textiles']['greenfield_dollar_share']-14.2)<0.1,
                                   f"{100*GF['machinetool']['greenfield_dollar_share']:.1f} / {100*GF['textiles']['greenfield_dollar_share']:.1f}"),

 ('The 278\npanel counties that received aircraft contracts without an aircraft plant',
                                   GF['aircraft']['greenfield_counties_in_panel']==278,
                                   f"{GF['aircraft']['greenfield_counties_in_panel']} in panel, "
                                   f"{GF['aircraft']['greenfield_counties']} on the contract frame"),
 ('median 1940 manufacturing share of $0.069$ against a national $0.012$',
                                   round(GF['aircraft']['gf_median_mfgshare1940'],3)==0.069 and
                                   round(SS['national_medians']['mfgshare1940'],3)==0.012,
                                   f"{GF['aircraft']['gf_median_mfgshare1940']} vs "
                                   f"{SS['national_medians']['mfgshare1940']}"),
 ('median thirty-two war-related establishments against four',
                                   GF['aircraft']['gf_median_warestabs']==32.0 and
                                   SS['national_medians']['warestabs']==4.0,
                                   f"{GF['aircraft']['gf_median_warestabs']} vs "
                                   f"{SS['national_medians']['warestabs']}"),

 # ---- the allocation function, year by year -------------------------------
 ('fixed set of 1{,}490 counties',       BY['n_ever']==1490, f"{BY['n_ever']}"),
 ('manufacturing share is $0.497$ in 1940 and $0.588$',
                                   abs(BY['rho_mfg_fixed_sample'][0]-0.497)<0.001 and
                                   abs(BY['rho_mfg_fixed_sample'][-1]-0.588)<0.001,
                                   f"{BY['rho_mfg_fixed_sample']}"),
 ('rises from $0.493$ to $0.653$',
                                   abs(BY['rho_mfg_all_counties'][0]-0.493)<0.001 and
                                   abs(BY['rho_mfg_all_counties'][-1]-0.653)<0.001,
                                   f"{BY['rho_mfg_all_counties'][0]} -> {BY['rho_mfg_all_counties'][-1]}"),
 ('15.0 percent of counties received a',
                                   abs(100*BY['coverage'][0]-15.0)<0.1 and
                                   abs(100*max(BY['coverage'])-40.1)<0.1,
                                   f"{100*BY['coverage'][0]:.1f} / {100*max(BY['coverage']):.1f}"),
 ('($p = 0.69$, $0.27$, $0.38$, $0.97$, $0.44$, $0.83$)',
                                   all(abs(a-b)<0.006 for a,b in
                                       zip(BY['b_enlistee']['p'],[0.691,0.275,0.381,0.969,0.443,0.832])),
                                   f"{BY['b_enlistee']['p']}"),
 ('in every year the same small positive',
                                   all(c>0 and p<0.01 for c,p in
                                       zip(BY['b_civic']['coef'],BY['b_civic']['p'])),
                                   f"min coef {min(BY['b_civic']['coef'])}, max p {max(BY['b_civic']['p'])}"),

 # ---- the continuous specification's employment levels -------------------
 ('($+0.042$ against $+0.041$, plant\n$+0.021$)',
                                    abs(RO['log total employment 1970']['coef']['W_M']-0.0422)<0.0006 and
                                    abs(RO['log total employment 1970']['coef']['W_C']-0.0410)<0.0006 and
                                    abs(RO['log total employment 1970']['coef']['W_F']-0.0210)<0.0006,
                                    f"{RO['log total employment 1970']['coef']}"),
 ('contracts enter\nat $+0.060$ and plant at $+0.027$, both at $p<0.001$, while installations enter at\n$+0.014$ and reach only ten percent',
                                    abs(RO['log manufacturing employment 1970']['coef']['W_C']-0.0595)<0.0006 and
                                    abs(RO['log manufacturing employment 1970']['coef']['W_F']-0.0274)<0.0006 and
                                    abs(RO['log manufacturing employment 1970']['coef']['W_M']-0.0139)<0.0006 and
                                    max(RO['log manufacturing employment 1970']['p'][k] for k in ('W_C','W_F'))<0.001 and
                                    0.05<RO['log manufacturing employment 1970']['p']['W_M']<0.10,
                                    f"{RO['log manufacturing employment 1970']['coef']} "
                                    f"p_M={RO['log manufacturing employment 1970']['p']['W_M']}"),

 # The Conley claim used to say the spatial errors were "as tight as or tighter"
 # than the clustered ones. Two of the eight are not, which the table shows.
 ('Six of the eight spatial standard errors are\ntighter than the state-clustered ones',
                                    (lambda C: sum(1 for c,s in C if c<s)==6 and len(C)==8)(_conley()),
                                    f"{sum(1 for c,s in _conley() if c<s)} of {len(_conley())} tighter"),

 # ---- prose that quotes Table 4 by column; each of these was unchecked -----
 ('($+0.049$ against $+0.035$ for\ncontracts and $+0.020$ for plant)',
                                   abs(_t4('Military',2)-0.0493)<0.0006 and
                                   abs(_t4('Contracts',2)-0.0346)<0.0006 and
                                   abs(_t4('War plant',2)-0.0197)<0.0006,
                                   f"{_t4('Military',2)} {_t4('Contracts',2)} {_t4('War plant',2)}"),
 ('contracts enter at $+0.33$\nand industrial plant at $+0.29$, while military installations enter at $-0.59$',
                                   abs(_t4('Contracts',4)-0.3325)<0.005 and
                                   abs(_t4('War plant',4)-0.2851)<0.005 and
                                   abs(_t4('Military',4)+0.5945)<0.005,
                                   f"{_t4('Contracts',4)} {_t4('War plant',4)} {_t4('Military',4)}"),
 ('$+0.0009$ log points per additional death per thousand',
                                   abs(_t4('Fatal burden',1)-0.0009)<0.00005,
                                   f"{_t4('Fatal burden',1)}"),

 # ---- the neighbour coefficient, read from the table the reader sees ------
 ('($+0.180$, $p = 0.002$)',       abs(_adj_tab()[0]-0.180)<0.0006 and
                                   abs(_adj_tab()[1]-0.002)<0.0006,
                                   f"table shows {_adj_tab()[0]} / p {_adj_tab()[1]}"),
 ('111 of the 118 treated counties find a\nmatch inside it',
                                   aj['log pop 1970']['n_treated']==111,
                                   f"{aj['log pop 1970']['n_treated']}"),

 # ---- overlap decomposition: the percentage, not only the share -----------
 ('gives $0.408$ and\n$0.032$, which together account for only 82 percent',
                                  abs(100*(ACD['share_from_contract_concentration']
                                           +ACD['share_from_death_deviation'])-82.4)<0.6,
                                  f"{100*ACD['share_from_contract_concentration']:.1f}%"),
 ('places 44.0 percent of dollars in the top twenty counties',
                                  abs(VAL['top20_recon']-44.0)<0.05, fmt(VAL['top20_recon'],2)),

 # ---- employment levels behind the manufacturing share --------------------
 ('by 41 log\npoints for an installation and 22 for a plant',
                                  abs(me['log total employment 1970']['coef']-0.414)<0.005 and
                                  abs(pe['log total employment 1970']['matched']-0.223)<0.005,
                                  f"{me['log total employment 1970']['coef']:.3f} / {pe['log total employment 1970']['matched']:.3f}"),
 ('39 log points under a plant ($p < 0.001$) and by 22 under an installation',
                                  abs(pe['log manufacturing employment 1970']['matched']-0.388)<0.005 and
                                  pe['log manufacturing employment 1970']['p']<0.001 and
                                  abs(me['log manufacturing employment 1970']['coef']-0.215)<0.005,
                                  f"{pe['log manufacturing employment 1970']['matched']:.3f} / {me['log manufacturing employment 1970']['coef']:.3f}"),
 ('it is imprecise rather than zero ($p = 0.10$)',
                                  abs(me['log manufacturing employment 1970']['p']-0.103)<0.005,
                                  fmt(me['log manufacturing employment 1970']['p'])),
 # ---- the abstract, number by number ---------------------------------------
 ('raised county manufacturing employment by 39 log\npoints, an industrial workforce 47 percent larger',
                                  round(100*pe['log manufacturing employment 1970']['matched'])==39 and
                                  round(100*(math.exp(pe['log manufacturing employment 1970']['matched'])-1))==47,
                                  f"{pe['log manufacturing employment 1970']['matched']:.4f} = "
                                  f"{100*(math.exp(pe['log manufacturing employment 1970']['matched'])-1):.1f}%"),
 ('raised total employment\nby more --- 41 log points against 22',
                                  round(100*me['log total employment 1970']['coef'])==41 and
                                  round(100*pe['log total employment 1970']['matched'])==22,
                                  f"{me['log total employment 1970']['coef']:.4f} vs "
                                  f"{pe['log total employment 1970']['matched']:.4f}"),
 ('whose pairwise overlap runs from 0.22 to 0.59, against 0.87 for deaths and\npopulation on the same scale',
                                  round(min(v['A'] for k,v in tg['pairwise'].items() if 'D' not in k),2)==0.22 and
                                  round(max(v['A'] for k,v in tg['pairwise'].items() if 'D' not in k),2)==0.59 and
                                  round(ACD['contracts_prop_to_pop'],2)==0.87,
                                  f"{min(v['A'] for k,v in tg['pairwise'].items() if 'D' not in k):.4f}-"
                                  f"{max(v['A'] for k,v in tg['pairwise'].items() if 'D' not in k):.4f} "
                                  f"vs {ACD['contracts_prop_to_pop']}"),
 ('0.69, their strongest tie to anything prewar, with the urban share at 0.65',
                                  round(ACR['1940 manufacturing share']['W_C']['rho'],2)==0.69 and
                                  round(ACR['1940 urban share']['W_C']['rho'],2)==0.65 and
                                  ACR['1940 manufacturing share']['W_C']['rho']==max(
                                      ACR[r]['W_C']['rho'] for r in ACR),
                                  f"mfg {ACR['1940 manufacturing share']['W_C']['rho']} "
                                  f"urban {ACR['1940 urban share']['W_C']['rho']}"),
 ('fatal burden at $-0.03$; plant and installations behave the same way,\nat $+0.01$ and $-0.05$',
                                  round(ACR['fatal burden, per resident']['W_C']['rho'],2)==-0.03 and
                                  round(ACR['fatal burden, per resident']['W_F']['rho'],2)==0.01 and
                                  round(ACR['fatal burden, per resident']['W_M']['rho'],2)==-0.05,
                                  ' '.join(f"{ACR['fatal burden, per resident'][k]['rho']:+.4f}"
                                           for k in ('W_C','W_F','W_M'))),
 ('all\nthree exclude any association above 0.09 in either direction',
                                  max(abs(b) for k in ('W_C','W_F','W_M')
                                      for b in ACR['fatal burden, per resident'][k]['ci'])<=0.09,
                                  f"widest bound {max(abs(b) for k in ('W_C','W_F','W_M') for b in ACR['fatal burden, per resident'][k]['ci']):.3f}"),
 ('lowered measured homeownership\nby seven and a half points',
                                  abs(me['homeownership 1970']['coef']+7.49)<0.005,
                                  f"{me['homeownership 1970']['coef']:.4f}"),

 # ---- tenure: timing, placebo, and the price response --------------------
 ('$-5.57$ points already in 1950, $-6.35$ in 1960 and',
                                  abs(me['homeownership 1950']['coef']+5.574)<0.01 and
                                  abs(me['homeownership 1960']['coef']+6.353)<0.01 and
                                  abs(me['homeownership 1970']['coef']+7.489)<0.01,
                                  f"{me['homeownership 1950']['coef']:.2f}/{me['homeownership 1960']['coef']:.2f}/{me['homeownership 1970']['coef']:.2f}"),
 ('a 1970 median house value 15 percent \\emph{higher} than',
                                  abs(100*(np.exp(me['log median house value 1970']['coef'])-1)-15)<1.0,
                                  f"{100*(np.exp(me['log median house value 1970']['coef'])-1):.1f}%"),
 ('the 1940 home-ownership rate\n($+0.53$ points, $p = 0.70$)',
                                  abs(MILP['homeownership 1940']['coef']-0.529)<0.01 and
                                  abs(MILP['homeownership 1940']['p']-0.697)<0.01,
                                  f"{MILP['homeownership 1940']['coef']:.3f} p={MILP['homeownership 1940']['p']:.3f}"),
]

# ---- staleness guard ----------------------------------------------------
# A JSON older than the script that writes it silently freezes an obsolete
# result. That is exactly how the neighbour-comparison p-values reached the
# manuscript from a run that predated the treatment redefinition.
# Derived, not hand-listed. A hand-maintained map silently omits whatever was
# added last, which is the newest and least-checked result: six of the 24 JSONs
# in data/analysis were missing from it, including regression_results.json,
# which carries Table 6 and the theta_C / theta_F interactions.
def _producers():
    out = {}
    for f in sorted((ROOT / 'src').glob('*.py')):
        src = f.read_text()
        for m in re.finditer(r"""['"]([A-Za-z0-9_]+\.json)['"]""", src):
            j = m.group(1)
            # only count a mention that is being written, not read
            line = src[src.rfind('\n', 0, m.start()) + 1: src.find('\n', m.end())]
            if 'write_text' in line or 'json.dump' in line or 'AN/' in line or "AN /" in line:
                if 'json.load' in line or "J(" in line: continue
                out.setdefault(j, f.name)
    return out
PRODUCERS = _producers()
stale=[j for j,s in PRODUCERS.items()
       if (AN/j).exists() and (ROOT/'src'/s).exists()
       and (AN/j).stat().st_mtime < (ROOT/'src'/s).stat().st_mtime]
if stale:
    print('STALE ARTIFACTS (older than the script that writes them):')
    for j in stale: print('   !',j,'<-',PRODUCERS[j])
    print()
else:
    print(f'artifact freshness: all {len(PRODUCERS)} results newer than their scripts\n')

# ---- orphan-exhibit guard -----------------------------------------------
# tabA_milrobust.tex sat in the repository for a month with no script writing
# it, so re-running the pipeline could not correct it, and it drifted from
# audit_military.json by 0.63 points on the ownership row while the prose --
# which read the JSON -- stayed right. Any exhibit no committed script writes
# is unfixable by construction, so fail the audit on one.
_srcs='\n'.join(f.read_text() for f in sorted((ROOT/'src').glob('*.py'))
                 if f.name!='audit_paper_vs_data.py')
orphans=[f.stem for f in sorted((ROOT/'paper/tables').glob('*.tex'))
         if not f.stem.startswith('_') and f.stem not in _srcs]
if orphans:
    print('ORPHAN EXHIBITS (no committed script writes these):')
    for o in orphans: print('   !',o+'.tex')
    print()
else:
    print(f'exhibit producers: all {len(list((ROOT/"paper/tables").glob("tab*.tex")))} '
          'tables are written by a script in src/\n')

# The same test for the tracked result files. illinois_robustness.json survived
# here with neither a producer nor a consumer, which is how a dead artifact
# starts looking like a live one.
_dead=[f.name for f in sorted(AN.glob('*.json'))
       if f.name not in PRODUCERS and f.name not in _srcs]
if _dead:
    print('ORPHAN RESULT FILES (no committed script writes these):')
    for d in _dead: print('   !',d)
    print()

# ---- range guard --------------------------------------------------------
# Folding independent cities into their parent county summed every numeric
# column, rates included, which put twenty counties above 100 percent on every
# tenure variable and Henry County above 100 on the 1970 manufacturing share.
# The values are population-weighted now; this asserts they stay that way.
RATE_COLS=['urbrate1940','blackshare1940','mfgshare1940']            # shares in [0,1]
PCT_COLS=['ownrate1940','ownrate1950','ownrate1960','ownrate1970',
          'mfgshare1960','mfgshare1970']                              # percentages in [0,100]
bad_range=[]
for c in RATE_COLS:
    if c in m.columns:
        v=pd.to_numeric(m[c],errors='coerce')
        n=int(((v<0)|(v>1)).sum())
        if n: bad_range.append((c,n,float(v.max())))
for c in PCT_COLS:
    if c in m.columns:
        v=pd.to_numeric(m[c],errors='coerce')
        n=int(((v<0)|(v>100)).sum())
        if n: bad_range.append((c,n,float(v.max())))
if bad_range:
    print('OUT-OF-RANGE RATE VARIABLES (a merge is summing rates again):')
    for c,n,mx in bad_range: print(f'   ! {c}: {n} counties out of range, max {mx:.1f}')
    print()
else:
    print(f'rate variables: all {len(RATE_COLS)+len(PCT_COLS)} within bounds\n')

CHECKS.extend(_load_extra())

print(f'{"claim in manuscript":42s}{"in text":>9}{"matches data":>14}   value now')
bad=0; missing=0
for s,ok,val in CHECKS:
    intext = s in tex
    if not intext: missing+=1
    if not ok: bad+=1
    flag='' if (intext and ok) else ('  <-- NOT IN TEXT' if not intext else '  <-- MISMATCH')
    print(f'{s[:40]!s:42s}{str(intext):>9}{str(ok):>14}   {val}{flag}')
print(f'\nclaims checked {len(CHECKS)}  not found in text {missing}  mismatched {bad}')

# ---- forbidden literals ---------------------------------------------------
# A positive check finds its own sentence and stops looking. That is how
# "fixed set of 1,481 counties" survived in a table note while the body said
# 1,490, and how the conclusion kept "30.8 percent of aircraft dollars" after
# Section 5.2 was corrected to 27.9. Every value a correction retires goes here,
# and the audit fails if it reappears anywhere in the manuscript.
FORBIDDEN = [
    ('1{,}481',  'pre-independent-city-merge count of ever-contracted counties; now 1,490'),
    ('30.8 percent of aircraft', 'pre-merge aircraft greenfield share; now 27.9'),
    ('The 272\ncounties', 'miscounted aircraft greenfield counties; now 278 in panel'),
    ('The two that do not are\nlatitude', 'inverted balance sentence; the two named DO exceed 0.10'),
    ('$-8.956$', 'IV coefficient no artifact produces'),
    ('$-7.69$',  'IV coefficient no artifact produces'),
    ('the 481',  'neighbour-pool size that no run produces; the rule gives 475'),
    ('$\\rho = +0.101$', 'mobilisation/B_civic correlation; the valid sample gives +0.094'),
    ('falls to $11.2$', 'conditioned shift-share F; the stored row gives 11.3'),
    ('the four departments the parser', 'three departments were emitted twice, not four'),
    ('thirty-two counties that', 'thirty-one fail to match; a further one lacks a 1920 figure'),
    ('Positive values identify investment-heavy', 'sign inverted relative to make_maps.py and the figure note'),
    ('sqrt{2', 'equation (7) normalisation that make_maps.py never applies'),
    ('over 40 state clusters', 'the plant design clusters on 44'),
    ('Test score for every soldier', 'AGCT is on 5.4 percent of records, not all'),
    ('test score for 7.2 million soldiers', 'AGCT is on 447,464 records, not 7.2 million'),
]
_stale = [(lit, why) for lit, why in FORBIDDEN if lit in tex]
if _stale:
    print('\nFORBIDDEN LITERALS PRESENT IN THE MANUSCRIPT:')
    for lit, why in _stale:
        print(f'   ! {lit!r} -- {why}')
else:
    print(f'forbidden literals: none of {len(FORBIDDEN)} retired values reappear')

# ---- coverage ------------------------------------------------------------
# "356 checks, 0 mismatched" is a statement about 356 checks. The number that
# decides whether the next sweep will find something new is what fraction of the
# manuscript's claims any check looks at. It was 53.5 percent when four
# consecutive sweeps each turned up fresh defects.
def _coverage():
    spans = []
    for _s, _ok, _v in CHECKS:
        i = tex.find(_s)
        while i != -1:
            spans.append((i, i + len(_s))); i = tex.find(_s, i + 1)
    a = tex.find(r'\begin{abstract}')
    b = tex.find(r'\begin{thebibliography}', a)
    if b < a: b = len(tex)
    blank = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}',
                   lambda m: ' ' * len(m.group(0)), tex, flags=re.S)
    blank = re.sub(r'(?m)^%.*$', lambda m: ' ' * len(m.group(0)), blank)
    for pat in [r'\\needlines\{[^}]*\}',
                r'\\(?:ref|eqref|cite\w*|label|input)\{[^}]*\}',
                r'\\[a-zA-Z]+\{[-0-9.]+(?:pt|em|ex|in|cm|mm)?\}',
                r'(?:Section|Sections|Table|Tables|Figure|Figures|equation|Equation)~?\s?\\?[A-Za-z]*\{?\s?\d+',
                r'\d+(?:pt|em|ex|in|cm|mm)\b']:
        blank = re.sub(pat, lambda m: ' ' * len(m.group(0)), blank)
    tot = cov = 0
    for m_ in re.finditer(r'-?\d[\d,{}\\.]*\d|\b\d\b', blank):
        q = m_.start()
        if not (a <= q < b): continue
        v = m_.group(0).replace('{,}', '').replace(',', '')
        try: float(v)
        except ValueError: continue
        if re.fullmatch(r'(19|20)\d\d', v): continue
        tot += 1
        if any(x <= q < y for x, y in spans): cov += 1
    return cov, tot

_cov, _tot = _coverage()
print(f'claim coverage: {_cov} of {_tot} numeric claims in body prose '
      f'fall inside a checked span ({100*_cov/_tot:.1f}%)')

if bad or missing or _stale or orphans:
    sys.exit(1)
