#!/usr/bin/env python3
"""
Parse the WWII war-manufacturing facilities database (29 sheets) into
plant-level records.

Source: United States War Production Board, "War Manufacturing Facilities
Authorized through October 1944 by General Type of Product of Operator in 1939",
Program and Statistics Bureau, March 1945. Digitized from Harvard Library scans
by E Records USA for Garin and Rothbaum (2025) and distributed in their
replication package as FacilitiesRaw/FacilitiesDatabase.xls. This is NOT the
Civilian Production Administration's 1946 facilities volume.

Source layout, per row:
  '$Name'      begins a plant OPERATOR record
  '@City St'   gives the LOCATION of a facility
  blank        continuation line (extra products for the same facility)
Costs sit on the row that opens a facility; the location is the nearest '@'
at or after that row, before the next facility opens.

Yields one row per (operator, location) facility with public/private cost split.
"""
import re
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT/'data/raw/garin_rothbaum/Data/RawData/FacilitiesRaw/FacilitiesDatabase.xls'
OUT  = ROOT/'data/analysis'; OUT.mkdir(parents=True, exist_ok=True)

COLS = ['page','operator_loc','product','capacity','capsym','date_avail','pub_source',
        'total_cost','pub_total','pub_struct','pub_equip',
        'priv_total','priv_struct','priv_equip','priv_other']
MONEY = ['total_cost','pub_total','pub_struct','pub_equip',
         'priv_total','priv_struct','priv_equip','priv_other']

# CPA uses period-era state abbreviations, not USPS.
STATE = {
 'ala':'AL','ariz':'AZ','ark':'AR','calif':'CA','colo':'CO','conn':'CT','del':'DE',
 'dc':'DC','fla':'FL','ga':'GA','idaho':'ID','ill':'IL','ind':'IN','iowa':'IA',
 'kans':'KS','ky':'KY','la':'LA','maine':'ME','md':'MD','mass':'MA','mich':'MI',
 'minn':'MN','miss':'MS','mo':'MO','mont':'MT','nebr':'NE','nev':'NV','nh':'NH',
 'nj':'NJ','nmex':'NM','ny':'NY','nc':'NC','ndak':'ND','ohio':'OH','okla':'OK',
 'oreg':'OR','pa':'PA','ri':'RI','sc':'SC','sdak':'SD','tenn':'TN','tex':'TX',
 'utah':'UT','vt':'VT','va':'VA','wash':'WA','wva':'WV','wis':'WI','wyo':'WY',
 'ariz.':'AZ','n mex':'NM','n dak':'ND','s dak':'SD','n car':'NC','s car':'SC',
 'w va':'WV','n h':'NH','n j':'NJ','n y':'NY','r i':'RI','s c':'SC','n c':'NC',
 'alaska':'AK','hawaii':'HI','pr':'PR','canada':'XX',
 # the volume also spells states out in full
 'alabama':'AL','arizona':'AZ','arkansas':'AR','california':'CA','colorado':'CO',
 'connecticut':'CT','delaware':'DE','d c':'DC','florida':'FL','georgia':'GA',
 'illinois':'IL','indiana':'IN','kansas':'KS','kentucky':'KY','louisiana':'LA',
 'maryland':'MD','massachusetts':'MA','michigan':'MI','minnesota':'MN',
 'mississippi':'MS','missouri':'MO','montana':'MT','nebraska':'NE','nevada':'NV',
 'new hampshire':'NH','new jersey':'NJ','new mexico':'NM','new york':'NY',
 'north carolina':'NC','north dakota':'ND','oklahoma':'OK','oregon':'OR',
 'pennsylvania':'PA','rhode island':'RI','south carolina':'SC','south dakota':'SD',
 'tennessee':'TN','texas':'TX','vermont':'VT','virginia':'VA','washington':'WA',
 'west virginia':'WV','wisconsin':'WI','wyoming':'WY',
}

def money(x):
    """CPA cells carry footnote markers ('14,275B/'), dashes for zero, and stray $."""
    if pd.isna(x): return np.nan
    s = str(x).strip().replace(',','').replace('$','')
    s = re.sub(r'[A-Za-z]+/?$', '', s).strip()      # drop trailing footnote letters
    if s in {'-','','--','nan','.'}: return 0.0
    try: return float(s)
    except ValueError: return np.nan

# Locations the source itself declines to specify. These are NOT parse
# failures: the CPA volume records some facilities as multi-site, or credits
# them to a federal agency rather than a place. They are unassignable in
# principle and must be reported separately, never counted as missing data.
NONGEO = {'various','various various','undesignated','not reported','n a',
          'us govt','u s govt','navy dept','war dept','agriculture dept'}

def split_loc(s):
    """'@Phoenix AriZ' -> ('phoenix','AZ'). Returns (None,None) if unassignable."""
    t = re.sub(r'^@','',str(s)).strip()
    t = re.sub(r'\(\s*cont\.?\s*\)','',t, flags=re.I)   # continuation-page marker
    t = re.sub(r'[,\.]',' ', t)
    t = re.sub(r'\s+',' ', t).strip()
    if t.lower() in NONGEO or t.lower().startswith('various'):
        return '__NONGEO__', None
    parts = t.split(' ')
    for n in (2,1):                       # try two-word then one-word state token
        if len(parts) > n:
            cand = ' '.join(parts[-n:]).lower().strip('.')
            if cand in STATE:
                return ' '.join(parts[:-n]).lower(), STATE[cand]
    return t.lower(), None

def parse_sheet(name):
    df = pd.read_excel(SRC, sheet_name=name, header=None, skiprows=4)
    df = df.iloc[:, :len(COLS)]; df.columns = COLS
    for c in MONEY: df[c] = df[c].map(money)
    txt = df.operator_loc.astype(str).str.strip()
    df['kind'] = np.where(txt.str.startswith('$'), 'operator',
                 np.where(txt.str.startswith('@'), 'location',
                 np.where(txt.str.startswith('&'), 'division',
                 np.where(txt.str.startswith('!'), 'newflag', 'cont'))))

    recs, op, cur_loc = [], None, None
    rows = df.to_dict('records')
    for i, r in enumerate(rows):
        if r['kind'] == 'operator':
            op = re.sub(r'^\$','',str(r['operator_loc'])).strip()
            cur_loc = None                      # a new operator clears the location
        if r['kind'] == 'location':
            cur_loc = r['operator_loc']         # carry forward within the block
        if pd.isna(r['total_cost']):
            continue

        # Resolve this facility's place, most specific rule first.
        loc, how = None, None
        if r['kind'] == 'location':
            loc, how = r['operator_loc'], 'own_row'
        else:
            # the '@' that follows, before the next facility opens
            for j in range(i+1, min(i+15, len(rows))):
                if rows[j]['kind'] == 'operator': break
                if not pd.isna(rows[j]['total_cost']): break
                if rows[j]['kind'] == 'location':
                    loc, how = rows[j]['operator_loc'], 'next_at'; break
        if loc is None and cur_loc is not None:
            loc, how = cur_loc, 'carried'       # inherit the block's last location
        if loc is None:
            # last resort: the nearest preceding '@' anywhere above
            for j in range(i-1, max(i-25, -1), -1):
                if rows[j]['kind'] == 'location':
                    loc, how = rows[j]['operator_loc'], 'lookback'; break

        # '!New Plant' is the volume's explicit new-construction designation.
        # It sits on its own line after the facility's location, before the
        # next facility opens. 338 appear across the 29 sheets.
        is_new = False
        for j in range(i+1, min(i+8, len(rows))):
            if rows[j]['kind'] == 'operator': break
            if not pd.isna(rows[j]['total_cost']): break
            if rows[j]['kind'] == 'newflag': is_new = True; break

        city, st = split_loc(loc) if loc is not None else (None, None)
        recs.append({'sheet':name,'page':r['page'],'operator':op,'city':city,'state':st,
                     'loc_rule':how,'newplant':is_new,
                     'product':r['product'],'date_avail':r['date_avail'],
                     'pub_source':r['pub_source'],
                     **{c:r[c] for c in MONEY}})
    return pd.DataFrame(recs)


# ---------------------------------------------------------------------------
# Group 29 is government-OPERATED facilities and is the only sheet with a
# hierarchy: a "$U. S. Govt" grand total, then eight "$<agency>" department
# subtotals, then the individual facilities under each. Groups 1-28 have no
# such headers. Parsing all three levels as if they were facilities counts the
# sheet's $1.596bn exactly three times, and two of the department subtotals
# ("War Department", "Interior, Dept of" and others) pick up the location of
# the first facility beneath them and so reach the county panel as phantom
# plants -- $307m of it landing in Colbert County, Alabama alone.
#
# Garin and Rothbaum sidestep this by looping over sheets 1-28 only. Dropping
# the whole sheet would also discard $1.596bn of genuine arsenals and navy
# yards, so the aggregate rows are removed and the facilities kept.
GROUP29_GRAND_TOTAL = 1596130
GROUP29_SUBTOTALS = {          # agency header -> its printed subtotal, $000s
    'War Department': 307465, 'Navy Dept': 1240758, 'Interior, Dept of': 15870,
    'Agriculture, Dept of': 15492, 'Tennessee Valley Authority': 15309,
    'Commerce, Dept of': 336, 'Defense Plant Corp': 823,
    'Federal Security Agency': 77,
}

def drop_group29_aggregates(df):
    """Remove the grand-total and department-subtotal rows from Group 29."""
    if sum(GROUP29_SUBTOTALS.values()) != GROUP29_GRAND_TOTAL:
        raise AssertionError('Group 29 subtotals no longer sum to the grand total; '
                             'the sheet layout has changed -- re-derive before trusting.')
    g29 = df.sheet.astype(str).str.contains('29')
    op  = df.operator.astype(str).str.strip()
    cost = pd.to_numeric(df.total_cost, errors='coerce')
    is_grand = g29 & op.eq('U. S. Govt') & cost.eq(GROUP29_GRAND_TOTAL)
    is_sub   = g29 & pd.concat(
        [op.eq(k) & cost.eq(v) for k, v in GROUP29_SUBTOTALS.items()], axis=1).any(axis=1)
    drop = is_grand | is_sub
    if drop.sum():
        print(f'  Group 29: dropped {int(drop.sum())} aggregate rows '
              f'(${cost[drop].sum()/1e6:.3f}bn) -- grand total and department subtotals')
    return df[~drop].reset_index(drop=True)


if __name__ == '__main__':
    xl = pd.ExcelFile(SRC)
    out = pd.concat([parse_sheet(s) for s in xl.sheet_names], ignore_index=True)
    out = drop_group29_aggregates(out)
    out['pub_total']  = out.pub_total.fillna(0)
    out['priv_total'] = out.priv_total.fillna(0)
    out['public_share'] = np.where(out.total_cost > 0, out.pub_total/out.total_cost, np.nan)

    nongeo = out.city.eq('__NONGEO__')
    out.loc[nongeo,'city'] = None
    out['assignable'] = ~nongeo
    print(f'facilities parsed      : {len(out):,}')
    print(f'  explicitly "New Plant": {int(out.newplant.sum()):,} '
          f'(${out.loc[out.newplant,"total_cost"].sum()/1e6:.2f}bn)')
    print(f'  source gives no place: {int(nongeo.sum()):,} rows, '
          f'${out.loc[nongeo,"pub_total"].sum()/1e6:.2f}bn public  <- unassignable in principle')
    print(f'  with a location      : {out.state.notna().sum():,} '
          f'({out.state.notna().sum()/max(1,(~nongeo).sum()):.1%} of assignable)')
    print(f'  total cost           : ${out.total_cost.sum()/1e6:.2f}bn (thousands of 1940s $)')
    print(f'  publicly financed    : ${out.pub_total.sum()/1e6:.2f}bn '
          f'({out.pub_total.sum()/out.total_cost.sum():.1%})')
    print(f'  privately financed   : ${out.priv_total.sum()/1e6:.2f}bn')
    print(f'  distinct operators   : {out.operator.nunique():,}')
    big = out[(out.pub_total >= 1000) & (out.public_share > .5)]
    print(f'\n  large public plants (>=$1M public, majority-public): {len(big):,}')
    print(f'    their public $      : ${big.pub_total.sum()/1e6:.2f}bn '
          f'({big.pub_total.sum()/out.pub_total.sum():.1%} of all public plant spending)')
    out.to_parquet(OUT/'facilities_plant_level.parquet', index=False)
    print(f'\n-> {OUT/"facilities_plant_level.parquet"}')

    # Geocode here rather than in a separate step. facilities_geocoded.parquet
    # was previously an orphan: five scripts read it and none produced it, so a
    # correction to this parser could not reach the county panel.
    from geocode import resolve
    geo, diag = resolve(out, 'city', 'state', weight_col='pub_total')
    print(f'\ngeocoded: {diag["matched"]:,}/{diag["rows"]:,} rows '
          f'({diag["row_rate"]:.1%}), {diag["weight_rate"]:.1%} of public dollars, '
          f'{diag["counties"]:,} counties')
    print(f'  by stage: {diag["by_stage"]}')
    geo.to_parquet(OUT/'facilities_geocoded.parquet', index=False)
    print(f'-> {OUT/"facilities_geocoded.parquet"}')
