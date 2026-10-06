#!/usr/bin/env python3
"""
Does the GI Bill run through the plant and installation treatments?

Between treatment (1940-45) and outcome (1970) sits the largest veteran-specific
federal intervention in American history. Fetter (2013) attributes 7.4 percent
of the 1940-60 rise in home ownership to VA loan guarantees, and 25 percent for
affected cohorts; Bound and Turner (2002) find moderate schooling gains. Both
outcomes -- home ownership and family income -- are outcomes this paper
estimates. A referee should ask whether the estimated treatment effects are
partly GI Bill effects.

The benefits flowed to veterans, so the channel is open only if treatment
predicts a county's veteran population. This script tests exactly that, on the
matched samples themselves, using the county enlistment count as the veteran
proxy: enlistees are the population from which returning veterans are drawn.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; AN=ROOT/'data/analysis'

b=pd.read_parquet(AN/'matched_sample_raw.parquet')
m=pd.read_parquet(AN/'master_panel_v3.parquet')
b=b.merge(m[['fips','ds2_enlist','deaths_all']],on='fips',how='left',suffixes=('','_m'))
b['statefip']=(b.fips//1000).astype(int)
CTRL=['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040',
      'PCTILL3','PCTFRM3','LATITUDE','LONGITUD']
X0=CTRL+['sq_logpop1940','sq_urbrate1940','sq_mfgshare1940','sq_blackshare1940','mfg_suppressed']

# veteran intensity: enlistees per 1940 resident, and deaths per enlistee
P=b.pop1940.replace(0,np.nan)
b['enlist_rate']=1000*b.ds2_enlist/P
b['death_per_enlistee']=1000*b.deaths_all/b.ds2_enlist.replace(0,np.nan)

def test(frame,tvar,ylab,y):
    Zr=frame[X0].astype(float); Zr=Zr.loc[:,Zr.std()>1e-10]
    Zs=(Zr-Zr.mean())/Zr.std()
    q=pd.concat([frame[[y,tvar,'statefip']],Zs],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    r=sm.OLS(q[y],sm.add_constant(q[[tvar]+list(Zs.columns)].astype(float))
             ).fit(cov_type='cluster',cov_kwds={'groups':q.statefip})
    return {'outcome':ylab,'coef':round(float(r.params[tvar]),4),
            'se':round(float(r.bse[tvar]),4),'p':round(float(r.pvalues[tvar]),4),
            'n':int(r.nobs),'mean':round(float(q[y].mean()),2)}

res={}
print('='*84)
print('DOES TREATMENT PREDICT VETERAN INTENSITY?  (full prewar controls, state-clustered SE)')
print('='*84)
res['plant']=[test(b,'treat','enlistees per 1,000 residents','enlist_rate'),
              test(b,'treat','deaths per 1,000 enlistees','death_per_enlistee')]
print('\nLarge public plant:')
for r in res['plant']:
    print(f"  {r['outcome']:34s} {r['coef']:+8.3f} ({r['se']:.3f})  p={r['p']:.3f}   mean {r['mean']}")

# The military treatment is defined inside matched_military.py; rebuild it here
# on the same rule (top decile of per-capita military facility dollars, with
# counties receiving both treatments dropped) rather than duplicating a file.
mil=b.copy()
mil['mil_pc']=mil.cdb_fac_military/mil.pop1940.replace(0,np.nan)
cut=mil.loc[mil.mil_pc>0,'mil_pc'].quantile(0.90)
mil['treat_mil']=((mil.mil_pc>=cut)&(mil.mil_pc>0)).astype(int)
mil=mil[~((mil.treat==1)&(mil.treat_mil==1))].copy()
res['military']=[test(mil,'treat_mil','enlistees per 1,000 residents','enlist_rate'),
                 test(mil,'treat_mil','deaths per 1,000 enlistees','death_per_enlistee')]
print(f'\nTop-decile military installation ({int(mil.treat_mil.sum())} treated):')
for r in res['military']:
    print(f"  {r['outcome']:34s} {r['coef']:+8.3f} ({r['se']:.3f})  p={r['p']:.3f}   mean {r['mean']}")

(AN/'gi_bill_channel.json').write_text(json.dumps(res,indent=2))
print(f'\n-> {AN/"gi_bill_channel.json"}')
