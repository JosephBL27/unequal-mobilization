# Research Audit — Unequal Mobilization

**Date:** 2026-08-28 · **Scope:** data collection, construction, analysis, and the
paper's empirical claims. **Partly superseded 2026-08-31** — see the note at the
head of `DATA_ANALYSIS_AUDIT.md`. Everything below was verified by running code against
the files on disk. Numbers are reported as computed, including the unfavourable
ones.

---

## 1. Verdict

The data is sound and the core empirical claim is stronger than the draft states.
Three things need action before submission: one citation error that leaves a
load-bearing premise unsourced, one adverse pre-trend result that changes how the
outcome estimates may be described, and one finding the draft does not contain
that is probably the paper's best contribution.

---

## 2. What the audit found in the data

### 2.1 Contracts — clean, and externally validated

190,693 rows, no missing values, no negative or zero contract values. Thirty
exact-duplicate rows (0.0055% of dollars) were dropped. `ContractNumber` is not a
key — 1.6% blank, 180,373 distinct values over 187,576 non-blank rows — but
inspection shows repeated numbers are line items on multi-product contracts, not
double counting.

The decisive check: the reconstructed county series was compared against
`var88`+`var89` of the 1947 County Data Book, the contemporaneous official series
Fishback and Cullen used.

| | Reconstructed | 1947 County Data Book |
|---|---|---|
| National total | $178.2 bn | $180.4 bn |
| Top-20 county share | 44.0% | 42.7% |
| Top-100 county share | 81.4% | 80.9% |
| Counties with zero | 1,583 | 1,506 |

Pearson correlation in levels **0.992**, in logs 0.943, Spearman 0.941. Only 112
counties have County Data Book spending that the reconstruction records as zero.

This is as good an external validation as this literature offers, and it retires
any worry that the city→county assignment introduced systematic error. It also
independently reproduces Fishback and Cullen's "roughly two-fifths to the top
twenty counties" from a different source through a different crosswalk.

### 2.2 Casualties — clean

DS1: 300,131 records, zero duplicate rows, zero blank service IDs, 44 blank county
names, 184 blank status codes. `COUNTYID` is the county FIPS code, confirmed
against a 2,980-county reference at 96% (the 4% miss is Virginia independent
cities, absent from the reference itself). Status distribution: KIA 171,530 ·
DNB 82,479 · DOW 24,786 · FOD 18,888 · M 1,352 · DOI 912.

DS3 (Navy/USMC/USCG) carries full FIPS but has 6,368 null FIPS (9.7%) and, more
importantly, a different universe. It is not additive with DS1 and is used
nowhere in estimation.

### 2.3 Facilities — built from scratch, with a documented ceiling

The CPA facilities volume had never been parsed in this project. It is now:
14,693 plant records across 29 sheets, $24.01 bn total, **79.7% publicly
financed**. Public and private cost columns reconcile to the total to within
0.00% (6 rows off).

Three parsing bugs were found and fixed, each material:

1. **Footnote markers.** Values like `14,275B/` failed numeric parsing and were
   silently zeroed. This alone understated public financing by $1.19 bn and hit
   the largest plants hardest.
2. **Location attachment.** The volume marks operators with `$`, divisions with
   `&`, and places with `@`, and a single operator block can hold several plants
   in different counties. Naive lookahead lost 15.6% of locations. The final rule
   takes the union of four resolution paths and recovers 98.7%.
3. **Continuation markers.** `detroit mich (cont)` did not match `detroit`.

**A measurement fact that belongs in the paper, not a bug:** 184 facilities
holding **$1.84 bn — 9.6% of all publicly financed plant dollars** — are recorded
by the source with no place at all. They are credited to "various" locations or
to a federal agency (`U. S. Govt`, `Navy Dept`). These are unassignable in
principle. Any county-level $W^F$ measures *locatable* plant investment, and the
paper should say so.

Within the assignable universe, 88.7% of public dollars geocode to a county
across 1,419 counties. Validated against County Data Book `var90` (industrial
facilities): $15.0 bn vs $16.3 bn, Pearson 0.958, Spearman 0.862.

### 2.4 Place→county assignment

One resolver serves both volumes, in four named stages, so every assignment is
attributable:

| | Contracts (by $) | Facilities (by public $) |
|---|---|---|
| Exact city+state | 93.2% | 66.0% |
| Curated alias | 5.2% | 10.1% |
| Fuzzy, within state, ≥0.88 | 0.15% | 0.5% |
| **Total** | **98.5%** | **88.7%** (of assignable) |

The 176-entry alias table is not fuzzy matching. Each entry is a historical
identification of a borough, company town, or unincorporated plant site —
Wilson Dam to Colbert County, Geneva to Utah County, Mare Island to Solano. These
matter disproportionately because unincorporated sites are where the large
publicly financed plants sat.

Two fuzzy matches were caught crossing county lines and are now explicitly
blocked: Wood-Ridge NJ (Bergen, Curtiss-Wright) was matching to Woodbridge
(Middlesex), and Hanover MA (Plymouth) to Andover (Essex).

### 2.5 A sample-selection problem that would have biased the results

The 1940 manufacturing control is missing for 370 counties because the Census of
Manufactures suppresses county wage-earner counts where there is little or no
manufacturing. Listwise deletion dropped those counties, cutting the sample from
3,107 to 2,686 and removing **10.3% of 1940 population and 9.5% of Army/AAF
deaths** — systematically the small, rural, zero-contract counties.

Since the selection is on the treatment-relevant margin, this biases the sample
toward exactly the industrial places that received war investment. Missing values
are now coded to zero (their substantive meaning) with a suppression indicator,
restoring the full 3,107-county sample. This changed results: the estimated
association between fatal burden and contract receipt moved from 0.031 (p=0.041)
to 0.011 (p<0.001) — smaller, better identified, and on the full universe.

---

## 3. What the analysis found

### 3.1 The paper's existing claim holds and gets sharper

Overlap coefficient $\mathcal{A} = 0.455$ between the county distribution of
Army/AAF deaths and the distribution of contract dollars. 97.8% of counties
recorded a death; 48.0% received any contract; **1,579 counties lost men and
received no major contract at all.**

Per-capita rank correlation between fatal burden and contract dollars:
**−0.031**. Effectively zero.

### 3.2 The finding the draft does not contain

The paper models wartime investment as a two-element vector: procurement $W^C$
and durable capital $W^F$. **There is a third allocation, and it is nearly
orthogonal to the other two.**

The 1947 County Data Book separates war facilities into *industrial* (`var90`,
$16.7 bn) and *military* (`var91`, $9.8 bn) — camps, air bases, depots, proving
grounds. Their correlation with each other is Pearson 0.234, Spearman 0.311. 436
counties got industrial facilities only; 334 got military only; 292 got both.

Pairwise geography of all four wartime allocations:

| Pair | Overlap $\mathcal{A}$ | JS (bits) | Spearman |
|---|---|---|---|
| $W^C \times W^F$ | 0.584 | 0.220 | 0.615 |
| $W^C \times W^M$ | 0.206 | 0.661 | 0.332 |
| $W^F \times W^M$ | 0.222 | 0.661 | 0.299 |
| $W^C \times D$ | 0.456 | 0.350 | 0.615 |
| $W^F \times D$ | 0.409 | 0.431 | 0.481 |
| $W^M \times D$ | 0.278 | 0.551 | 0.323 |

**Per capita, all three investment types are uncorrelated with fatal burden:**
contracts −0.031, industrial plant +0.008, military installations −0.039. Three
separate allocation mechanisms, three near-zero associations with sacrifice. That
is a systemic result, not noise.

And the two kinds of federal capital left **opposite structural legacies**
(3,107 counties, prewar controls, state fixed effects, SE clustered on state):

| Outcome | $W^C$ contracts | $W^F$ plant | $W^M$ military | $B$ burden |
|---|---|---|---|---|
| Log population 1970 | +0.034*** | +0.021*** | **+0.050*** | −0.002 |
| Manufacturing share 1970 | +0.438*** | +0.355*** | **−0.630*** | −0.096 |
| Log family income 1970 | +0.015*** | +0.011*** | +0.009*** | −0.001 |
| Homeownership 1970 | −0.014 | +0.117 | **−0.340*** | −0.112 |

Military installations produced the **largest** population gain of the three and
a large **negative** effect on manufacturing share and homeownership. Industrial
plant grew population, manufacturing, income, and ownership together. On the
extensive margin the contrast is starker still: merely having a war plant is
associated with a 2.15 pp higher 1970 manufacturing share, merely having a
military installation with 3.84 pp lower.

The obvious sharper question — *did casualty-heavy counties get bases rather than
plants?* — was tested and is **null** once prewar controls enter (coefficient
−0.0002, p=0.94, n=736). The raw quartile gap (34.8% → 54.9% receiving a plant)
is confounded by prewar urbanization and industrial structure. Reported as a null.

### 3.3 Robustness

- **Conley spatial standard errors** (200 km uniform kernel) are as tight as or
  tighter than state-clustered. $W^M$ on 1970 manufacturing share: $t = -6.72$.
- **Dropping the 20 largest contract recipients** moves no coefficient in the
  third decimal.
- **Four burden denominators** — residents, males, men in the labour force,
  battle deaths only — all null on 1970 population ($p$ from 0.30 to 0.59).

---

## 4. Three things to fix before submission

### 4.1 A load-bearing premise is unsourced — act on this first

`brunetReplication2025` is cited in four places (lines 67, 75, 149, 264) as the
source of the reconstructed contract data, including the empirical premise that
the reconstruction finds more true-zero counties than the County Data Book. But
that bibitem is the replication package for **"War Bonds and Household Saving in
WWII"** — a different paper on a different subject.

Direct inspection of `WWII_contracts_clean.dta` confirms only what the data
itself proves: `volume` ∈ {1,2,3,4} and `PageNo` to 3,521 identify it as a
digitization of the four-volume CPA *Alphabetic Listing of Major War Supply
Contracts* (`cpaContracts1946`). The file carries no embedded provenance label
and was created 2025-05-25.

**Action:** cite `cpaContracts1946` for the underlying record, and add a correct
citation for whoever produced the digitization. Do not guess the attribution.

*Incidental benefit:* the reconstruction's true-zero claim, previously asserted
on a wrong citation, is now verified in-house — 1,583 zero counties against the
County Data Book's 1,531 (§2.1).

### 4.2 Pre-trends are partly adverse and must be reported

Wartime exposure was assigned in 1940–45, so it should not predict 1930–40
outcomes. It partly does:

| Placebo outcome | $W^C$ | $W^F$ | $W^M$ | $B$ |
|---|---|---|---|---|
| Log population growth 1930→40 | +0.0031** | +0.0008 | +0.0050*** | −0.0012*** |
| Manufacturing share 1940 (level) | +0.0044*** | +0.0012** | −0.0006 | +0.0001 |

Contracts and military installations went disproportionately to counties already
growing; contracts and plant to counties already industrial. Fatal burden was
*negatively* associated with prewar growth — casualty-heavy counties were already
losing population.

This does not sink the design, but it does bound the language. The outcome
estimates should be described as **conditional associations on a rich prewar
control set**, not as causal effects, unless a quasi-experimental design is added.
The $W^F$ pre-trend is the mildest, which is a point in favour of the
Garin–Rothbaum-style plant specification the paper already proposes.

### 4.3 Citation gaps

An independent review of all 24 sources ( `docs/SOURCE_APPARATUS.md` ) found
three substantive gaps. Summarised here; the full argument is in that file.

1. **Selective Service is entirely absent.** $E_i^A$ is the output of an
   administrative screening process — local-board discretion, occupational and
   agricultural deferments, regionally varying 4-F rates — that correlates with
   both prewar county characteristics and $W^C$. The denominator of the preferred
   exposure measure is itself an outcome, and nothing in the bibliography
   addresses it.
2. **Kriner and Shen, *The Casualty Gap* (2010)** and the casualty-inequality
   literature. Half this paper's question already has a literature. Not engaging
   it is a risk to the novelty claim.
3. **The GI Bill and Cold War procurement.** Homeownership and income run to 1970
   with no citation to the Servicemen's Readjustment Act — the largest mediator
   between service and postwar housing and income, allocated in proportion to
   veteran population and administered in racially differential ways. Cold War
   procurement continued along the same plant geography and is a live threat to
   $G_i$.

A fourth, structural: the Garin–Rothbaum replication package supplies **seven of
the eleven** core quantities. That concentration should be disclosed.

---

## 4.4 Two further defects found on the second pass

**DS1 county coverage is incomplete.** Matched against the 1940 census the honour
list leaves 56 counties with no recorded death, and that figure is concentrated in Illinois, which
appears with 80 of its 102 counties and an implied rate of 1.91 deaths per thousand
residents against a national 2.27. Independent cities are split inconsistently
between city and county in Maryland, Missouri, and Virginia — Baltimore appears as
both `BALTIMORE` (188) and `BALTIMORE CITY` (178). Dropping Illinois entirely moves
no coefficient beyond the third decimal and shifts the overlap coefficient from
0.455 to 0.442, so nothing rests on it, but it belongs in the paper and now is.

**$B_i^A$ is defined on 2,976 of 3,107 counties.** 91 counties are absent from the
enlistment source (including Baltimore City and St Louis City, 4.6% of contract
dollars but only 0.12% of deaths) and 40 record impossible values — more deaths
than enlistments, or a mobilisation rate above one. Four of those are Michigan
counties with a systematic enlistment undercount. The 131 excluded counties hold
4.0% of 1940 population. Exclusion applies to $B_i^A$ specifications only.

## 5. Open work

| Item | Status |
|---|---|
| $E_i^A$ enlistment | **Built.** DS2's NARA codes remain unmapped (the ICPSR codebook lists codes without labels; NARA and CenSoc technical documents do not publish the mapping). Solved by a different route: G&R's county file tabulates volunteer and drafted counts from the same NARA universe with ICPSR codes, which map to FIPS through Haines at 99.9%. 6,942,188 enlistments across 3,070 counties |
| $B_i^A$ (equation 2) | **Built** on 2,976 counties. National rate 42.9 deaths per 1,000 enlisted; 90/10 county ratio 3.58. Under $B_i^A$ the allocation regressions are null on all three investment types ($p$ = 0.40, 0.82, 0.84) and per-enlistee rank correlations turn negative |
| $G_i$ large-plant indicator | Built (1,306 plants ≥$1M, majority-public, 94.4% of public plant dollars) but not yet used in a Garin–Rothbaum-style specification |
| Boundary harmonization | Crosswalks are on disk (`data/raw/crosswalks/ftz_1940/`); the panel currently uses raw FIPS, which is fine 1940–1970 outside Virginia |
| Facilities residual | $1.95 bn across 1,023 rows within the assignable universe |
| Maps | Needs `geopandas` and NHGIS 1940 boundaries |

---

## 6. Reproduction

```bash
./.venv/bin/python src/validate_sources.py      # quality profile
./.venv/bin/python src/parse_facilities.py      # CPA facilities -> plant level
./.venv/bin/python src/build_master_panel.py    # 3,107-county panel
./.venv/bin/python src/three_geographies.py     # overlap statistics
./.venv/bin/python src/regressions.py           # allocation + outcomes
./.venv/bin/python src/robustness.py            # pre-trends, Conley, placebos
./.venv/bin/python src/make_tables.py           # 4 main tables
./.venv/bin/python src/make_appendix.py         # 8 appendix tables
```

All twelve tables compile: `paper/tables/_check.pdf`.

Significance: * p<0.10, ** p<0.05, *** p<0.01.
