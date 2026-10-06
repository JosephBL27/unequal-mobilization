#!/usr/bin/env python3
"""Structured data-quality profile of every primary source. Writes data/docs/validation.json."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent.parent; RAW=ROOT/'data/raw'; GR=RAW/'garin_rothbaum/Data/RawData'
R={}

def prof(df, name, keys=None):
    d={'rows':int(len(df)),'cols':int(df.shape[1]),'columns':{}}
    for c in df.columns:
        s=df[c]; nn=int(s.notna().sum())
        e={'null_rate':round(1-nn/len(df),4),'distinct':int(s.nunique(dropna=True))}
        if pd.api.types.is_numeric_dtype(s) and nn:
            q=s.dropna().astype(float)
            e.update(min=float(q.min()),max=float(q.max()),mean=round(float(q.mean()),3),
                     p50=float(q.median()),p99=float(q.quantile(.99)),
                     zeros=int((q==0).sum()),negatives=int((q<0).sum()))
        else:
            v=s.dropna().astype(str)
            if len(v):
                e['top']= {str(k):int(x) for k,x in v.value_counts().head(4).items()}
                e['blank']=int((v.str.strip()=='').sum())
                e['ws_pad']=int((v!=v.str.strip()).sum())
        d['columns'][c]=e
    if keys:
        d['key_dupes']={'|'.join(keys):int(df.duplicated(subset=keys).sum())}
    R[name]=d
    print(f'  {name:28s} {len(df):>10,} x {df.shape[1]:>3}')
    return d

print('=== PROFILING ===')
c,_=pyreadstat.read_dta(str(RAW/'contracts/WWII_contracts_clean.dta')); prof(c,'contracts_brunet')
d1,_=pyreadstat.read_dta(str(RAW/'casualties_icpsr38927/38927-0001-Data.dta')); prof(d1,'ds1_army_casualties')
d3,_=pyreadstat.read_dta(str(RAW/'casualties_icpsr38927/38927-0003-Data.dta')); prof(d3,'ds3_navy_casualties')
gc,_=pyreadstat.read_dta(str(GR/'WWII_draft_volunteer_casualties_Army_AirForce.dta')); prof(gc,'gr_county_casualties',['stateicp','county'])
h40,_=pyreadstat.read_dta(str(RAW/'haines_icpsr2896/02896-0032-Data.dta'),usecols=['state','county','name','fips','totpop','totpop30','urb940','mtot','ftot','negtot'])
prof(h40,'haines_1940_subset',['fips'])

# ---- targeted integrity checks -------------------------------------------
chk={}
# contracts: value distribution + exact-duplicate contract rows
v=pd.to_numeric(c.ValueThousandsDollars,errors='coerce')
chk['contracts']={
 'value_null':int(v.isna().sum()),'value_zero':int((v==0).sum()),'value_neg':int((v<0).sum()),
 'total_k':float(v.sum()),'p50_k':float(v.median()),'p99_k':float(v.quantile(.99)),'max_k':float(v.max()),
 'gini_like_top1pct_share':round(float(v.nlargest(int(len(v)*.01)).sum()/v.sum()),4),
 'full_row_duplicates':int(c.duplicated().sum()),
 'dupe_on_contractnumber':int(c.ContractNumber.duplicated().sum()),
 'award_year_range':[float(pd.to_numeric(c.award_year,errors='coerce').min()),
                     float(pd.to_numeric(c.award_year,errors='coerce').max())],
 'award_year_null':int(pd.to_numeric(c.award_year,errors='coerce').isna().sum()),
 'distinct_manufacturers':int(c.NameofManufacturer.nunique()),
 'distinct_cities':int(c.city_name.nunique()),
 'agency_counts':{str(k):int(x) for k,x in c.Agency.astype(str).value_counts().head(8).items()},
}
# DS1: duplicate soldiers?
chk['ds1']={'dupe_full_row':int(d1.duplicated().sum()),
 'dupe_name_ssid':int(d1.duplicated(subset=['NAME','SSID']).sum()),
 'ssid_blank':int((d1.SSID.astype(str).str.strip()=='').sum()),
 'county_blank':int((d1.COUNTYNAME.astype(str).str.strip()=='').sum()),
 'status_blank':int((d1.STATUS.astype(str).str.strip()=='').sum())}
# DS3 fips validity
f3=pd.to_numeric(d3.FIPS,errors='coerce')
chk['ds3']={'fips_null':int(f3.isna().sum()),'fips_zero':int((f3==0).sum()),
 'counties':int(f3[f3>0].nunique()),'dupe_full_row':int(d3.duplicated().sum())}
# Haines 1940 universe
h=h40.copy(); h['fips']=pd.to_numeric(h.fips,errors='coerce')
cty=h[(h.county!=0)&h.fips.notna()]
chk['haines1940']={'total_rows':int(len(h)),'state_rows':int((h.county==0).sum()),
 'county_rows':int(len(cty)),'fips_dupes':int(cty.fips.duplicated().sum()),
 'pop_total':float(cty.totpop.sum()),'pop_zero':int((cty.totpop==0).sum()),
 'pop30_null':int(cty.totpop30.isna().sum())}
R['integrity']=chk
(ROOT/'data/docs/validation.json').write_text(json.dumps(R,indent=2,default=str))
print('\n=== INTEGRITY ===')
print(json.dumps(chk,indent=2,default=str))
