#!/usr/bin/env python3
"""
Assemble the county analysis panel on 1940 geography.

Treatments   W^C reconstructed contracts, W^F publicly financed facilities,
             G   large-public-plant indicator, D^A Army/AAF deaths
Benchmarks   the 1947 County Data Book war series (Fishback-Cullen legacy)
Controls     1930 and 1940 census, Fishback-Horrace-Kantor prewar vector
Outcomes     population, manufacturing share, family income, homeownership
             at 1940, 1950, 1960, 1970
"""
import json
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat

ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'data/raw/haines_icpsr2896'; AN=ROOT/'data/analysis'; GR=ROOT/'data/raw/garin_rothbaum/Data/RawData'

# Independent cities are folded into their surrounding county. The wartime
# sources split them: contracts recorded at the city, deaths at the county.
# See src/merge_independent_cities.py for how the parent is identified.
_IC=pd.read_csv(ROOT/'data/raw/crosswalks/independent_city_merge.csv')
IC_MAP=dict(zip(_IC.city_fips.astype(int), _IC.parent_fips.astype(int)))
def fold(s):
    v=pd.to_numeric(s,errors='coerce')
    return v.map(lambda x: IC_MAP.get(int(x),int(x)) if pd.notna(x) else np.nan)
def _pop_lookup(part):
    """Unfolded fips -> total population, for weighting rates across a merge.

    Read before folding, because the whole point is to know how much of the
    merged unit each side contributes.
    """
    df,_=pyreadstat.read_dta(str(H/f'02896-{part}-Data.dta'), usecols=['county','fips','totpop'])
    df['fips']=pd.to_numeric(df.fips,errors='coerce')
    df=df[(pd.to_numeric(df.county,errors='coerce')!=0)&df.fips.notna()]
    df['fips']=df.fips.astype(int)
    df['totpop']=pd.to_numeric(df.totpop,errors='coerce')
    # a few fips repeat within a part -- Alaska's four judicial districts share
    # 2900 -- and a duplicated index cannot be used as a lookup
    return df.groupby('fips').totpop.sum()

def haines(n, cols=None, rate_cols=(), wpart=None):
    """Load one Haines part and fold independent cities into their parent county.

    Counts are summed. Rates and medians must not be: adding Richmond city's
    home-ownership rate to Henrico County's produced 120 percent, and the same
    fault put twenty counties above 100 on every tenure variable and Henry
    County above 100 on the 1970 manufacturing share. Pass those columns in
    `rate_cols` and they are averaged with population weights taken from
    `wpart` before the fold, which is the only point at which the two sides of
    the merge are still distinguishable.
    """
    df,_=pyreadstat.read_dta(str(H/f'02896-{n}-Data.dta'), usecols=cols)
    df['fips']=pd.to_numeric(df.fips,errors='coerce')
    df=df[(pd.to_numeric(df.county,errors='coerce')!=0)&df.fips.notna()]
    rate_cols=[c for c in rate_cols if c in df.columns]
    if rate_cols:
        w=_pop_lookup(wpart if wpart else n)
        df['_w']=df.fips.astype(int).map(w).astype(float)
        # a unit with no population match still has to carry its own value
        df['_w']=df['_w'].fillna(df['_w'].median() if df['_w'].notna().any() else 1.0)
    df['fips']=fold(df.fips)
    df=df[df.fips.notna()].copy(); df['fips']=df.fips.astype(int)
    # Continental United States only. Alaska (02), Hawaii (15), and the
    # territories are excluded: statehood timing and administrative
    # comparability make them non-analogous, and Alaska's four judicial
    # districts share a single Haines FIPS (2900), which duplicates rows.
    df=df[~(df.fips//1000).isin([2,15,60,66,69,72,78])]
    num=[c for c in df.columns if c not in ('fips','state','county','name','_w')]
    for c in num: df[c]=pd.to_numeric(df[c],errors='coerce')
    if rate_cols:
        for c in rate_cols: df[c+'_wx']=df[c]*df['_w']
    agg={c:'sum' for c in num if c not in rate_cols}
    for c in rate_cols: agg[c+'_wx']='sum'
    if rate_cols: agg['_w']='sum'
    for c in ('state','county','name'):
        if c in df.columns: agg[c]='first'
    g=df.groupby('fips',as_index=False).agg(agg)
    for c in rate_cols:
        g[c]=np.where(g['_w']>0, g[c+'_wx']/g['_w'], np.nan)
        g=g.drop(columns=[c+'_wx'])
    if rate_cols: g=g.drop(columns=['_w'])
    return g

# ---------- spine: 1940 county universe -----------------------------------
p=haines('0032',['state','county','name','fips','totpop','totpop30','urb940',
                 'mtot','ftot','negtot','m14lf','f14lf','m14wage','mfgestab',
                 'mfgavear','mfgwages','dwell','dwellown','pctdwown'],
          rate_cols=['pctdwown'], wpart='0032')
p=p.rename(columns={'totpop':'pop1940','totpop30':'pop1930','urb940':'urban1940',
                    'negtot':'black1940','mfgavear':'mfgemp1940','mfgwages':'mfgwage1940',
                    'pctdwown':'ownrate1940','m14lf':'mlf1940','f14lf':'flf1940'})
print(f'spine: {len(p):,} counties, {p.pop1940.sum()/1e6:.1f}M pop')

# ---------- treatments ----------------------------------------------------
con=pd.read_parquet(AN/'contracts_geocoded.parquet')
con['v']=pd.to_numeric(con.ValueThousandsDollars,errors='coerce')
con['fips']=fold(con.fips)
con=con[con.fips.notna()]
cagg=(con[con.fips.notna()].assign(fips=lambda d:d.fips.astype(int))
        .groupby('fips').agg(contract_k=('v','sum'), n_contracts=('v','size'),
                             n_firms=('NameofManufacturer','nunique')).reset_index())

fac=pd.read_parquet(AN/'facilities_geocoded.parquet')
fac=fac[fac.assignable & fac.fips.notna()].copy(); fac['fips']=fold(fac.fips).astype(int)
fac=fac[fac.fips.notna()]
fac['is_big_public']=(fac.pub_total>=1000)&(fac.pub_total>fac.priv_total)
fagg=(fac.groupby('fips').agg(fac_total_k=('total_cost','sum'), fac_public_k=('pub_total','sum'),
                              fac_private_k=('priv_total','sum'), n_plants=('total_cost','size'),
                              n_big_public=('is_big_public','sum')).reset_index())

dea=pd.read_parquet(AN/'casualties_county.parquet')
# DS2 county aggregates: enlistment denominator and soldier composition
try:
    ds2=pd.read_parquet(AN/'ds2_county.parquet')
except FileNotFoundError:
    ds2=None
dea['fips']=fold(dea.fips); dea=dea.dropna(subset=['fips'])
dea['fips']=dea.fips.astype(int); dea=dea.groupby('fips',as_index=False).sum()

# ---------- 1947 County Data Book legacy war series -----------------------
cdb47=haines('0070',['state','county','fips','var88','var89','var90','var91'])
cdb47=cdb47.rename(columns={'var88':'cdb_contracts_combat','var89':'cdb_contracts_other',
                            'var90':'cdb_fac_industrial','var91':'cdb_fac_military'})
for c in ['cdb_contracts_combat','cdb_contracts_other','cdb_fac_industrial','cdb_fac_military']:
    cdb47[c]=pd.to_numeric(cdb47[c],errors='coerce')
cdb47['cdb_contracts_k']=cdb47.cdb_contracts_combat.fillna(0)+cdb47.cdb_contracts_other.fillna(0)
cdb47['cdb_facilities_k']=cdb47.cdb_fac_industrial.fillna(0)+cdb47.cdb_fac_military.fillna(0)

# ---------- outcomes ------------------------------------------------------
c50=haines('0072',['state','county','fips','var20','var36','var40','var57','var63'],
           rate_cols=['var20','var57','var63'], wpart='0035')
c50=c50.rename(columns={'var20':'medfaminc1950','var36':'emp1950','var40':'mfgemp1950',
                        'var57':'ownrate1950','var63':'medhomeval1950'})
c60=haines('0075',['state','county','fips','var23','var24','var28','var36','var37'],
           rate_cols=['var24','var28','var36','var37'], wpart='0038')
c60=c60.rename(columns={'var23':'emp1960','var24':'mfgshare1960','var28':'medfaminc1960',
                        'var36':'ownrate1960','var37':'medhomeval1960'})
c70=haines('0076',['state','county','fips','var38','var39','var58','var87','var88'],
           rate_cols=['var39','var58','var87','var88'], wpart='0041')
c70=c70.rename(columns={'var38':'emp1970','var39':'mfgshare1970','var58':'medfaminc1970',
                        'var87':'ownrate1970','var88':'medhomeval1970'})
pop50=haines('0035',['state','county','fips','totpop']).rename(columns={'totpop':'pop1950'})
pop60=haines('0038',['state','county','fips','totpop']).rename(columns={'totpop':'pop1960'})
pop70=haines('0041',['state','county','fips','totpop']).rename(columns={'totpop':'pop1970'})

# ---------- prewar controls ----------------------------------------------
fhk,_=pyreadstat.read_dta(str(GR/'fishbackhorracekantor.dta'))
xw,_ =pyreadstat.read_dta(str(GR/'crosswalk_statefip_stateicp_1910.dta'))
fhk=fhk.merge(xw,left_on='STATE',right_on='stateicp',how='left')
fhk['fips']=fhk.statefip*1000+(pd.to_numeric(fhk.NDMTCODE,errors='coerce')/10).round()
fhk=fhk[fhk.fips.notna()].copy(); fhk['fips']=fhk.fips.astype(int)
fhk['fips']=fold(fhk.fips)
fhk=fhk[fhk.fips.notna()].copy(); fhk['fips']=fhk.fips.astype(int)
fhk=fhk[['fips','LATITUDE','LONGITUD','PCTBLK3','PCTURB3','PCTFRM3','PCTILL3',
         'MANEMP3A','AREA','DRPCAAA','DRPCPBRE']].drop_duplicates('fips')

# ---------- merge ---------------------------------------------------------
def L(a,b,cols=None):
    b=b.drop(columns=[c for c in ['state','county','name'] if c in b.columns])
    return a.merge(b,on='fips',how='left')
m=p
for t in [cagg,fagg,dea]+([ds2] if ds2 is not None else [])+[cdb47.drop(columns=['cdb_contracts_combat','cdb_contracts_other']),
          c50,c60,c70,pop50,pop60,pop70,fhk]:
    m=L(m,t)

for c in ['contract_k','fac_total_k','fac_public_k','fac_private_k',
          'n_contracts','n_plants','n_big_public','deaths_all','deaths_battle']:
    m[c]=m[c].fillna(0)

# ---------- derived quantities -------------------------------------------
# Haines ships many numerics as Stata strings; coerce everything but the labels.
for c in m.columns:
    if c in ('fips','state','county','name'): continue
    m[c]=pd.to_numeric(m[c],errors='coerce')

def ihs(x): return np.arcsinh(x)
P=m.pop1940.replace(0,np.nan)
m['W_C']       = ihs(m.contract_k/P*1000)          # contract $ per 1,000 residents
m['W_F']       = ihs(m.fac_public_k/P*1000)
m['G']         = (m.n_big_public>0).astype(int)
m['B_civic']   = 1000*m.deaths_all/P
m['mfgshare1940']=m.mfgemp1940/m.pop1940
m['mfgshare1950']=pd.to_numeric(m.mfgemp1950,errors='coerce')/pd.to_numeric(m.emp1950,errors='coerce')
for y in [1940,1950,1960,1970]:
    m[f'logpop{y}']=np.log(pd.to_numeric(m[f'pop{y}'],errors='coerce').replace(0,np.nan))
m['popgrowth_3040']=np.log(m.pop1940/m.pop1930.replace(0,np.nan))
m['urbrate1940']=m.urban1940/P
m['blackshare1940']=m.black1940/P

m.to_parquet(AN/'master_panel.parquet',index=False)
print(f'\nmaster panel: {len(m):,} counties x {m.shape[1]} vars -> {AN/"master_panel.parquet"}')
cov={c:round(float(m[c].notna().mean()),3) for c in
     ['pop1940','pop1950','pop1960','pop1970','contract_k','fac_public_k','deaths_all',
      'cdb_contracts_k','medfaminc1950','medfaminc1960','medfaminc1970',
      'mfgshare1960','mfgshare1970','ownrate1950','ownrate1960','ownrate1970','LATITUDE']}
print('\ncoverage:'); print(json.dumps(cov,indent=2))
