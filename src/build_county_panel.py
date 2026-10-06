#!/usr/bin/env python3
"""
Build the county-level analysis inputs for the Unequal Mobilization paper.

Outputs (data/analysis/):
  contracts_county.parquet   county procurement  W_i^C
  casualties_county.parquet  Army/AAF deaths     D_i^A  (from DS1)
  enlistment_county.parquet  Army/AAF enlistment E_i^A  (from DS2)
  match_report.json          coverage diagnostics

Every step reports what it dropped. Nothing is silently discarded.
"""
import json, re
from pathlib import Path
import pandas as pd, pyreadstat

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT/'data/raw', ROOT/'data/analysis'
GR = RAW/'garin_rothbaum/Data/RawData'
OUT.mkdir(parents=True, exist_ok=True)
report = {}

# ---------------------------------------------------------------- helpers
def norm_city(s):
    s = str(s).lower().strip()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    for pat, rep in [(r'\bft\b','fort'), (r'\bst\b','saint'), (r'\bmt\b','mount'),
                     (r'\bn\b','north'), (r'\bs\b','south'),
                     (r'\be\b','east'), (r'\bw\b','west')]:
        s = re.sub(pat, rep, s)
    return re.sub(r'\s+', ' ', s).strip()

# City aliases the crosswalk cannot resolve: NYC boroughs, LA neighborhoods,
# named plant sites, and spelling errors in the CPA source documents.
ALIAS = {
    ('brooklyn','NY'):36047, ('long island city','NY'):36081, ('flushing','NY'):36081,
    ('jamaica','NY'):36081, ('astoria','NY'):36081, ('corona','NY'):36081,
    ('woodside','NY'):36081, ('college point','NY'):36081, ('maspeth','NY'):36081,
    ('elmhurst','NY'):36081, ('staten island','NY'):36085, ('bronx','NY'):36005,
    ('manhattan','NY'):36061,
    ('wilmington','CA'):6037, ('san pedro','CA'):6037, ('north hollywood','CA'):6037,
    ('van nuys','CA'):6037, ('venice','CA'):6037, ('hollywood','CA'):6037,
    ('canoga park','CA'):6037,
    ('witchita','KS'):20173, ('fort crook','NE'):31153, ('bendix','NJ'):34003,
    ('sparrows point','MD'):24005, ('essington','PA'):42045, ('johnsville','PA'):42017,
    ('east chicago','IN'):18089, ('pittsburg','PA'):42003, ('cincinatti','OH'):39061,
    ('detriot','MI'):26163, ('phillidelphia','PA'):42101, ('milwaukie','WI'):55079,
}

# ------------------------------------------------- 1. contracts -> county
def build_contracts():
    c, _  = pyreadstat.read_dta(str(RAW/'contracts/WWII_contracts_clean.dta'))
    cw, _ = pyreadstat.read_dta(str(GR/'cw-city-county.dta'))

    c['cn'] = c.city_name.map(norm_city)
    c['st'] = c.state.map(lambda x: str(x).strip().upper())
    cw['cn'] = cw.city.map(norm_city)
    cw['st'] = cw.state.map(lambda x: str(x).strip().upper())
    cwu = cw.drop_duplicates(['cn','st'])[['cn','st','cty_fips','county_name']]

    m = c.merge(cwu, on=['cn','st'], how='left')
    al = pd.DataFrame([(k[0], k[1], v) for k, v in ALIAS.items()],
                      columns=['cn','st','alias_fips'])
    m = m.merge(al, on=['cn','st'], how='left')
    m['fips'] = m.cty_fips.fillna(m.alias_fips)
    m['value_k'] = pd.to_numeric(m.ValueThousandsDollars, errors='coerce')

    ok = m.fips.notna()
    tot = m.value_k.sum()
    report['contracts'] = {
        'rows_total': int(len(m)), 'rows_matched': int(ok.sum()),
        'row_match_rate': round(float(ok.mean()), 4),
        'dollars_total_k': float(tot),
        'dollar_match_rate': round(float(m.value_k[ok].sum()/tot), 4),
        'counties_covered': int(m.loc[ok,'fips'].nunique()),
        'unmatched_dollars_k': float(m.value_k[~ok].sum()),
        'unmatched_distinct_city_states': int(
            m.loc[~ok].groupby(['city_name','state']).ngroups),
    }

    agg = (m[ok].assign(fips=m.fips[ok].astype(int))
             .groupby('fips')
             .agg(contract_value_k=('value_k','sum'),
                  n_contracts=('value_k','size'),
                  n_manufacturers=('NameofManufacturer','nunique'))
             .reset_index())
    agg.to_parquet(OUT/'contracts_county.parquet', index=False)

    # keep the residual visible, not deleted
    (m.loc[~ok].groupby(['city_name','state'])
       .agg(value_k=('value_k','sum'), n=('value_k','size'))
       .sort_values('value_k', ascending=False)
       .to_csv(OUT/'contracts_unmatched.csv'))
    print(f"contracts -> {len(agg):,} counties "
          f"({report['contracts']['dollar_match_rate']:.1%} of dollars)")
    return agg

# ------------------------------------------------- 2. DS1 deaths -> county
def build_casualties():
    d, _  = pyreadstat.read_dta(str(RAW/'casualties_icpsr38927/38927-0001-Data.dta'))
    xw, _ = pyreadstat.read_dta(str(GR/'crosswalk_statefip_stateicp_1910.dta'))

    d['stateicp'] = pd.to_numeric(d.STATEICP, errors='coerce')
    d['cty3']     = pd.to_numeric(d.COUNTYID, errors='coerce')
    d = d.merge(xw, on='stateicp', how='left')
    d['fips'] = (d.statefip * 1000 + d.cty3)

    ok = d.fips.notna()
    report['casualties_ds1'] = {
        'rows_total': int(len(d)), 'rows_with_fips': int(ok.sum()),
        'fips_rate': round(float(ok.mean()), 4),
        'counties': int(d.loc[ok,'fips'].nunique()),
        'status_counts': {str(k): int(v) for k, v in d.STATUS.value_counts().items()},
    }

    d = d[ok].copy()
    d['fips'] = d.fips.astype(int)
    # STATUS: KIA killed in action, DOW died of wounds, DOI died of injuries,
    # DNB non-battle death, FOD finding of death, M missing.
    d['is_battle_death'] = d.STATUS.isin(['KIA','DOW'])
    d['is_death']        = d.STATUS.isin(['KIA','DOW','DOI','DNB','FOD'])
    # Every record between the honor list and the panel is accounted for, so
    # that the paper's death total can be reconciled to the source count
    # rather than asserted.
    report['casualties_ds1'].update({
        'rows_unassigned': int((~ok).sum()),
        'assigned_deaths': int(d.is_death.sum()),
        'assigned_battle_deaths': int(d.is_battle_death.sum()),
        'assigned_missing': int((d.STATUS == 'M').sum()),
        'assigned_no_status': int((d.STATUS.astype(str).str.strip() == '').sum()),
        'status_coded': int(report['casualties_ds1']['rows_total']
                            - report['casualties_ds1']['status_counts'].get('', 0)),
    })

    agg = (d.groupby('fips')
             .agg(deaths_all=('is_death','sum'),
                  deaths_battle=('is_battle_death','sum'),
                  records=('is_death','size'))
             .reset_index())
    agg.to_parquet(OUT/'casualties_county.parquet', index=False)
    print(f"DS1 casualties -> {len(agg):,} counties, "
          f"{int(agg.deaths_all.sum()):,} deaths")
    return agg

# ------------------------------------------ 3. DS2 enlistment -> county
def build_enlistment():
    p = ROOT/'data/interim/ds2_enlistment.parquet'
    if not p.exists():
        print('DS2 parquet absent — run src/ds2_to_parquet.py first'); return None
    df = pd.read_parquet(p, columns=['ENL_STATE','ENL_COUNTY','KILLED','RACE','YOB'])
    df['st'] = pd.to_numeric(df.ENL_STATE, errors='coerce')
    df['ct'] = pd.to_numeric(df.ENL_COUNTY, errors='coerce')
    df['killed'] = pd.to_numeric(df.KILLED, errors='coerce').fillna(0)

    agg = (df.dropna(subset=['st','ct'])
             .groupby(['st','ct'])
             .agg(enlistments=('killed','size'), killed=('killed','sum'))
             .reset_index())
    agg.to_parquet(OUT/'enlistment_county.parquet', index=False)
    report['enlistment_ds2'] = {
        'rows_total': int(len(df)),
        'rows_with_geo': int(df[['st','ct']].notna().all(axis=1).sum()),
        'state_county_cells': int(len(agg)),
        'total_killed_flag': int(agg.killed.sum()),
        'note': 'ENL_STATE/ENL_COUNTY are NARA codes, NOT FIPS. '
                'A NARA->FIPS crosswalk is required before merging to counties.',
    }
    print(f"DS2 enlistment -> {len(agg):,} state-county cells, "
          f"{int(agg.enlistments.sum()):,} records")
    return agg

if __name__ == '__main__':
    build_contracts(); build_casualties(); build_enlistment()
    (OUT/'match_report.json').write_text(json.dumps(report, indent=2))
    print(f"\nreport -> {OUT/'match_report.json'}")
