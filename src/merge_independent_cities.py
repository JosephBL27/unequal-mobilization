#!/usr/bin/env python3
"""
Merge independent cities into their surrounding county.

Virginia's independent cities, Baltimore City, and St Louis City are county
equivalents in FIPS but were not treated consistently by the wartime sources:
the Civilian Production Administration recorded contracts at the city, while
the Army honour list recorded residence at the surrounding county. The result
is 14 units holding $6.83bn of contracts and 2.26M residents but only 251
recorded deaths -- a rate of 0.11 per 1,000 against a national 2.27. Left
alone this manufactures high-investment, zero-sacrifice counties and deflates
the measured alignment between the two distributions.

The parent county is identified spatially from the 1940 Newberry boundaries:
for each city polygon, the county polygon sharing the longest boundary with it.
Writes data/raw/crosswalks/independent_city_merge.csv.
"""
from pathlib import Path
import geopandas as gpd, pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parent.parent
g=gpd.read_file(ROOT/'data/raw/geo/counties_1940.gpkg').to_crs('EPSG:5070')
g['fips']=pd.to_numeric(g.fips,errors='coerce').astype('Int64')
g=g[g.fips.notna()].copy()

def is_indep(f):
    f=int(f)
    return ((f//1000==51 and f%1000>=510) or f in (24510,29510))
cities=g[g.fips.map(is_indep)].copy()
counties=g[~g.fips.map(is_indep)].copy()
print(f'independent cities in the 1940 layer: {len(cities)}')

rows=[]
sidx=counties.sindex
for _,c in cities.iterrows():
    cand=counties.iloc[list(sidx.query(c.geometry.buffer(2000), predicate='intersects'))]
    if cand.empty:
        cand=counties.iloc[list(sidx.nearest(c.geometry, max_distance=100000)[1])]
    best,blen=None,-1
    for _,k in cand.iterrows():
        try: L=c.geometry.buffer(1).intersection(k.geometry.buffer(1)).length
        except Exception: L=0
        if L>blen: blen,best=L,k
    if best is not None:
        rows.append({'city_fips':int(c.fips),'city_name':c.NAME,
                     'parent_fips':int(best.fips),'parent_name':best.NAME,
                     'shared_boundary_m':round(float(blen),1)})
cw=pd.DataFrame(rows).sort_values('city_fips')
out=ROOT/'data/raw/crosswalks/independent_city_merge.csv'
cw.to_csv(out,index=False)
print(cw.to_string(index=False))
print(f'\n-> {out}')
