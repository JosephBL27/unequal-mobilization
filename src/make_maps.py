#!/usr/bin/env python3
"""Choropleth maps of the four wartime allocations on 1940 county boundaries.

Figures carry no titles: captions belong in the manuscript, not in the image
file, so that the exhibit reads correctly wherever a typesetter places it.
Panels are lettered (a)-(d) so the text can reference them individually.

Colour grammar is shared across both figures. Human loss is rendered on a red
sequential ramp, federal dollars on a blue one, both running pale-to-dark so
that counties receiving nothing recede rather than dominate. Figure 2's
diverging red-blue scale then inherits the same association: its red pole is
the loss map's hue, its blue pole the investment maps'.
"""
import warnings
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parent.parent
FIG=ROOT/'paper/figures'; FIG.mkdir(parents=True,exist_ok=True)

plt.rcParams.update({
    'font.family':'serif', 'font.serif':['DejaVu Serif'],
    'axes.titlesize':10, 'figure.dpi':150,
})

MISSING='#d9d9d9'      # counties suppressed as too small to yield a credible rate
STATE_EDGE='#9a9a9a'   # state outlines, drawn over the fill for orientation

g=gpd.read_file(ROOT/'data/raw/geo/counties_1940.gpkg')
g['fips']=pd.to_numeric(g.fips,errors='coerce').astype('Int64')
d=pd.read_parquet(ROOT/'data/analysis/master_panel_v3.parquet')
gd=g.merge(d,on='fips',how='inner').to_crs('EPSG:5070')      # Albers equal-area
states=gd.dissolve(by='STATE_TERR').geometry.boundary
# A handful of very small counties produce impossible rates (Armstrong SD:
# 21 recorded deaths against a 1940 population of 42). They are plotted grey
# rather than allowed to set the colour scale.
SMALL = gd.pop1940 < 1000
gd.loc[SMALL, ['deaths_all','contract_k','fac_public_k','cdb_fac_military']] = np.nan
print(f'mapped counties: {len(gd):,}  (suppressed as too small: {int(SMALL.sum())})')

P=gd.pop1940.replace(0,np.nan)
gd['burden']    = 1000*gd.deaths_all/P
gd['contracts'] = gd.contract_k/P
gd['plant']     = gd.fac_public_k/P
gd['military']  = gd.cdb_fac_military/P


def panel(ax, col, letter, title, unit, cmap):
    """One choropleth panel with a lettered title and a unit-labelled colorbar.

    The colorbar is placed as a horizontal inset inside the map's own axes.
    Letting geopandas append it steals width from the map and leaves each
    panel a different size, which is what produced the ragged first draft.
    """
    v=gd[col].replace([np.inf,-np.inf],np.nan)
    hi=v.quantile(.98)                      # trim the top 2% so the map is readable
    gd.plot(column=v.clip(upper=hi), cmap=cmap, ax=ax, linewidth=0,
            edgecolor='none', missing_kwds={'color':MISSING}, legend=False)
    states.plot(ax=ax, color=STATE_EDGE, linewidth=.28)
    ax.set_title(f'({letter}) {title}', fontsize=16, pad=5)
    ax.axis('off'); ax.set_aspect('equal')

    # Seated in the empty southwest of the frame, label above the bar so that
    # nothing descends past the axes and collides with the row below.
    cax=ax.inset_axes([0.035,0.13,0.30,0.026])
    sm=plt.cm.ScalarMappable(cmap=cmap,
                             norm=plt.Normalize(vmin=float(v.min()),vmax=float(hi)))
    cb=ax.get_figure().colorbar(sm,cax=cax,orientation='horizontal')
    cb.ax.xaxis.set_label_position('top')
    cb.set_label(unit,fontsize=12,labelpad=4)
    cb.ax.tick_params(labelsize=11,length=3,pad=2)
    cb.outline.set_linewidth(.4)


fig,axes=plt.subplots(2,2,figsize=(14,8.2))
DOLLARS='\\$ thousands per 1940 resident'
panel(axes[0,0],'burden',   'a','Army/AAF deaths',
      'Deaths per 1,000 residents','Reds')
panel(axes[0,1],'contracts','b','Major war supply contracts', DOLLARS,'Blues')
panel(axes[1,0],'plant',    'c','Publicly financed war plant', DOLLARS,'Blues')
panel(axes[1,1],'military', 'd','Military installations',      DOLLARS,'Blues')
fig.legend(handles=[Patch(facecolor=MISSING,edgecolor='#b0b0b0',
                          label='1940 population under 1,000 (rate suppressed)')],
           loc='lower center', frameon=False, fontsize=12,
           bbox_to_anchor=(.5,.004))
fig.subplots_adjust(left=.005,right=.995,top=.965,bottom=.05,wspace=.01,hspace=.06)
fig.savefig(FIG/'fig_four_geographies.pdf',bbox_inches='tight')
fig.savefig(FIG/'fig_four_geographies.png',dpi=200,bbox_inches='tight')
plt.close(fig)
print('-> fig_four_geographies')

# residualised imbalance: where does loss exceed investment, conditional on prewar X?
import statsmodels.api as sm
def resid(y,X):
    s=pd.concat([y,X],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    r=sm.OLS(s.iloc[:,0],sm.add_constant(s.iloc[:,1:])).fit()
    return pd.Series(r.resid,index=s.index)
X=gd[['logpop1940','urbrate1940','blackshare1940','mfgshare1940','popgrowth_3040']].apply(
    pd.to_numeric,errors='coerce').fillna(0)
# cap burden at the 99th percentile before residualising, so a few
# transcription errors cannot dominate the imbalance surface
bcap=gd.burden.quantile(.99)
zb=resid(np.arcsinh(gd.burden.clip(upper=bcap)),X)
zw=resid(np.arcsinh(gd.contracts+gd.plant),X)
gd['imbalance']=((zb-zb.mean())/zb.std())-((zw-zw.mean())/zw.std())

fig,ax=plt.subplots(figsize=(10,6.2))
lim=gd.imbalance.abs().quantile(.97)
gd.plot(column=gd.imbalance.clip(-lim,lim),cmap='RdBu_r',ax=ax,linewidth=0,
        norm=TwoSlopeNorm(vcenter=0,vmin=-lim,vmax=lim),
        missing_kwds={'color':MISSING},legend=False)
states.plot(ax=ax, color=STATE_EDGE, linewidth=.28)
ax.axis('off'); ax.set_aspect('equal')

cax=ax.inset_axes([0.035,0.13,0.27,0.028])
sm=plt.cm.ScalarMappable(cmap='RdBu_r',
                         norm=TwoSlopeNorm(vcenter=0,vmin=-lim,vmax=lim))
cb=fig.colorbar(sm,cax=cax,orientation='horizontal')
cb.set_label('$I_i$, standard deviations',fontsize=12,labelpad=3)
cb.ax.tick_params(labelsize=11,length=3,pad=2)
cb.outline.set_linewidth(.4)
# Anchor the two poles for the reader without repeating the caption's text.
cb.ax.text(-.03,.5,'investment\nexceeds loss',transform=cb.ax.transAxes,
           ha='right',va='center',fontsize=11,color='#1f4b7a',linespacing=1.25)
cb.ax.text(1.03,.5,'loss exceeds\ninvestment',transform=cb.ax.transAxes,
           ha='left',va='center',fontsize=11,color='#7f2a20',linespacing=1.25)
fig.subplots_adjust(left=.005,right=.995,top=.995,bottom=.005)
fig.savefig(FIG/'fig_imbalance.pdf',bbox_inches='tight')
fig.savefig(FIG/'fig_imbalance.png',dpi=200,bbox_inches='tight')
plt.close(fig)
print('-> fig_imbalance')
print(f'\nmost imbalanced counties (highest sacrifice relative to investment):')
print(gd.nlargest(8,'imbalance')[['name','fips','burden','contracts','imbalance']].to_string(index=False))
