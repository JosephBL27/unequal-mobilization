# Formal Audit of the Data Analysis

**Paper:** *Unequal Mobilization* · **Audit date:** 2026-08-28
**Superseded in part on 2026-08-31.** A later pass found that
`paper/tables/tabA_milrobust.tex` had no producing script and had drifted from
its artifact, and that the matched designs' manufacturing-*share* contrast is a
denominator effect — manufacturing employment under a military installation is
indistinguishable from zero. Section 1's verdict on the postwar outcome
associations stands; its reading of the two treatments as opposite on
manufacturing does not. See the 2026-08-31 entries in my project notes.
**Scope:** every construction step, every estimate, and every claim in the paper.
**Standard applied:** a claim is *supported* only if a named script produces it
from a named artifact and the acceptance test passes. Claims that fail are
reported as failing.

Machine-checked provenance for 22 headline numbers, with SHA-256 prefixes of
both the producing script and the artifact, is in
`data/analysis/audit_trace.json`. It currently reports **0 missing artifacts**.

---

## 1. Verdict

The descriptive and conditional-association results are supported. The IV route
to causal identification is **not** supported and the paper says so explicitly.
A second causal design --- matching on large publicly financed plants --- **is**
supported, but for a narrower set of outcomes than its headline estimates
license. Both the success and the boundary are reported.

| Claim class | Status |
|---|---|
| Sample construction and coverage | **Supported** |
| External validation of the wartime measures | **Supported** |
| Distributional alignment ($\mathcal{A}$, JS, rank correlations) | **Supported** |
| Three distinct allocations | **Supported** |
| Postwar outcome associations | **Supported as conditional associations** |
| Composition-adjusted exposure | **Supported** |
| Causal effect via the 1938 IMP instrument | **NOT supported — exclusion fails** |
| Causal effect via the matched-plant design | **Supported, with stated scope limits** |

---

## 2. Construction audit

### 2.1 Sample

3,073 continental counties on 1940 boundaries, 131.7M residents.
Built by `src/build_master_panel.py`.

Three exclusions, each deliberate and each tested:

1. **Alaska, Hawaii, territories.** Statehood timing and administrative
   comparability. They held 0.40% of population, **zero** deaths and **zero**
   contracts, so exclusion cannot move any estimate. Alaska's four judicial
   districts also shared a single Haines FIPS (2900), which duplicated rows.
2. **Independent cities merged into parent counties.** Not cosmetic. Fourteen
   units held \$6.83bn in contracts and 2.26M residents but only 251 recorded
   deaths — 0.11 per 1,000 against a national 2.26 — because the CPA recorded
   contracts at the city and the Army recorded residence at the county. Left
   unmerged they manufacture high-investment, zero-sacrifice counties and
   deflate every alignment statistic. All 26 parents identified by longest
   shared border on the 1940 boundary file (`src/merge_independent_cities.py`);
   every assignment checked against the historical record.
3. **Counties under 1,000 population suppressed in maps only**, never in
   estimation. Armstrong County SD records 21 deaths against a 1940 population
   of 42.

### 2.2 Place-to-county assignment

`src/geocode.py`, four named stages so every assignment is attributable.

| | Contracts (by \$) | Facilities (by public \$) |
|---|---|---|
| Exact city+state | 93.2% | 66.0% |
| Curated alias | 5.2% | 10.1% |
| Fuzzy, within state, ≥0.88 | 0.15% | 0.5% |
| **Total** | **98.5%** | **88.7%** of assignable |

Two errors found and fixed during audit:

- The crosswalk resolved `new york, NY` to **Kings County**, placing \$3.64bn of
  Manhattan's contracts in Brooklyn. Aliases now override the crosswalk rather
  than only filling gaps.
- Two fuzzy matches crossed county lines — Wood-Ridge NJ (Bergen,
  Curtiss-Wright) matching Woodbridge (Middlesex), Hanover MA (Plymouth)
  matching Andover (Essex). Both blocked explicitly.

**Documented ceiling:** 184 facilities holding \$1.84bn — 9.6% of all publicly
financed plant dollars — are recorded by the source with no place, credited to
"various" locations or to a federal agency. Unassignable in principle. $W^F$
measures *locatable* plant investment and the paper says so.

### 2.3 Parsing

`src/parse_facilities.py`. Three bugs found and fixed, each material:

- Footnote markers (`14,275B/`) failed numeric parsing and silently zeroed the
  largest public plants — \$1.19bn understated.
- Location attachment across multi-plant operator blocks lost 15.6% of places;
  the final rule takes the union of four resolution paths and recovers 98.7%.
- Continuation markers (`detroit mich (cont)`) did not match.

**Acceptance test:** public + private = total to within 0.004%.

### 2.4 Missingness

`mfgshare1940` is suppressed by the Census of Manufactures for 370 small rural
counties. Listwise deletion removed **10.3% of population and 9.5% of deaths**,
systematically the zero-contract places — selection on the treatment-relevant
margin. Recoded to zero (the substantive meaning) with a suppression indicator.
This changed results: the burden–contract coefficient moved from 0.031
(p = 0.041) to 0.011 (p < 0.001) on the full universe.

---

## 3. Validation audit

Three independent checks, all passed.

| Check | Result |
|---|---|
| Reconstructed contracts vs 1947 County Data Book | \$177.3bn vs \$180.4bn; Pearson 0.992 (levels), 0.957 (rank); top-20 share 44.0% vs 42.7% |
| Publicly financed plant vs County Data Book industrial series | \$15.0bn vs \$16.3bn; Pearson 0.958 |
| DS2 county enlistment vs Garin–Rothbaum tabulation | Pearson **0.990** |

The first is the strongest available: the two series were built from different
documents through different geographies, and the reconstruction independently
reproduces the published "roughly two-fifths to the top twenty counties."

**One validation failure, reported:** DS2's own `KILLED` flag correlates with
DS1 deaths at 0.945 but undercounts by 32% (enlistment-to-casualty match
failure). DS1 is therefore authoritative for deaths; DS2 supplies only the
denominator and composition.

---

## 4. Known source defects

Not repairable, quantified, and disclosed.

- **DS1 county coverage is incomplete.** 56 counties carry no recorded death against
  the 1940 census, concentrated in Illinois (80 of 102 counties present;
  implied rate 1.91 per 1,000 against 2.27 national). Eighteen Illinois
  counties over 20,000 population record **zero** deaths.
- **Baltimore and St Louis remain under-recorded** at 0.36 and 0.12 per 1,000
  even after the city–county merge, so the honour list itself is incomplete for
  those metros.
- **93 counties over 20,000 population** have rates below half the national,
  holding 7.7% of population and 12.1% of contract dollars. Flagged in the panel
  as `coverage_ok`.

**Sensitivity:** excluding Illinois entirely moves no coefficient beyond the
third decimal and shifts $\mathcal{A}$ by less than 0.015.

---

## 5. Inference audit

| Test | Result |
|---|---|
| Conley spatial SE (200 km uniform kernel) | As tight as or tighter than state clustering; $W^M$ on 1970 manufacturing share $t = -6.7$ |
| Drop 20 largest contract recipients | No coefficient moves in the third decimal |
| Four burden denominators | All null on 1970 population ($p$ 0.30–0.59) |
| Extensive vs intensive margin | Effect is on the extensive margin: hosting a plant $+2.15$pp manufacturing share, hosting a base $-3.84$pp |
| Composition adjustment | Strengthens rather than weakens the null: adjusted $\rho = -0.182$ vs raw $-0.170$ |

**Adverse finding, disclosed in the paper:** contracts and military
installations significantly predict 1930–40 population growth, and contracts
predict the prewar manufacturing share. Wartime investment went to counties
already growing and already industrial. All outcome estimates are therefore
reported as conditional associations, not causal effects.

---

## 6. Causal audit — the instrument fails

`src/iv_analysis.py`, `src/iv_single.py`, `src/iv_validity.py`.

**Instrument:** the 1938 Industrial Mobilization Plan allocation of named
establishments to procurement branches, plus prewar Army and Navy
establishments and bases. 8,810 allocated facilities across 833 counties.

**Relevance passes.** First-stage $F$: 23.5 (contracts on allocated facilities),
63.6 (plant on industrial allocation), 17.2 (military on prewar bases).

**Validity fails, on three independent grounds:**

1. **Weak joint identification.** Partial $R^2$ of the excluded instruments is
   0.016–0.031 after controls and state effects. The 2SLS coefficients are
   implausibly large and reverse the OLS signs.
2. **A common confounder, not three effects.** Instrumenting each treatment
   separately gives 1970 homeownership coefficients of $-7.05$ (plant),
   $-11.92$ (contracts), and $-8.02$ (military). Three different treatments
   instrumented by three different prewar measures do not have three nearly
   identical large negative effects.
3. **The placebo test identifies the confounder.** The instrument strongly
   predicts the 1940 manufacturing share ($p < 0.001$) and the 1940 urban share
   ($p < 0.001$), while being unrelated to 1930–40 population growth
   ($p = 0.72$). It marks prewar industrial and urban **level**, not trend. The
   Munitions Board allocated plants that were already capable, in places that
   were already industrial — precisely the confounder a causal claim must
   overcome.

**Conclusion:** no instrumented estimate is reported as causal. Sargan does not
reject ($p = 0.69$), but an over-identification test cannot rescue an instrument
whose exclusion restriction fails on a direct placebo, since all instruments in
the set share the same defect.

This is a substantive result about the setting, not a technical failure. The
placement of wartime industrial investment was not a lottery, and the best
prewar predictor of placement is prewar capacity itself.

---

## 6b. Causal audit — the matched-plant design succeeds

`src/matched_plant_design.py`, `src/matched_estimates.py`, `src/matched_robustness.py`.

**Design.** Not an instrument. Counties receiving a large, new, wholly publicly
financed plant are compared against counties that received public plant
investment which was smaller, older, or partly private. Both were chosen by the
same wartime siting process, so selection into "the Defense Plant Corporation
built here" is held approximately fixed.

**Classification replicated.** Reading the classification out of the Garin and
Rothbaum replication code — structure share above 0.40 marks a new build,
private structure share at or below 1 percent marks a public plant, total cost
at or above \$1 million marks a large one — yields **364 large new public
plants** against their published 353. A three percent difference from the same
source volume is a successful replication of the classification, not a
coincidence.

**Sample.** After dropping the hundred largest manufacturing counties and 1940
metropolitan counties: 82 treated, 269 comparison.

**Acceptance tests, stated before running and all passed:**

| Test | Threshold | Result |
|---|---|---|
| Covariate balance | all $|$SMD$| \le 0.25$ | raw fails 4 of 9; after propensity weighting **0 of 9**, max 0.053 |
| Common support | no treated outside comparison range | **0 outside** |
| Pre-trend falsification | no effect on pre-war outcomes | **4 of 4 null**, $p$ = 0.61–0.98 |
| Effect accumulation | effects grow, not present at once | population $+0.052 \to +0.139 \to +0.211$; income null in 1950, emerges by 1960 |
| Weighting dependence | weighted $\approx$ unweighted | 0.211 vs 0.206 |
| Sensitivity | stable to trimming and subsetting | 0.188–0.211 across four specifications |

**Estimates.** By 1970, log population $+0.211$ ($p = 0.002$) and log median
family income $+0.056$ ($p < 0.001$). Manufacturing share $+1.56$ ($p = 0.21$)
and homeownership $-0.34$ ($p = 0.72$) are not distinguishable from zero.

**Scope limits, disclosed in the paper.** The comparison group is other plant
counties, so the estimand is the effect of a large new public plant *relative to
a smaller or partly private one*, not relative to no federal investment. With 82
treated counties the design has limited power, and the manufacturing and
homeownership nulls are consistent with modest effects it cannot resolve.

**Why this succeeds where the instrument failed.** The instrument had to assume
prewar capacity was excludable from postwar outcomes, and the placebo showed it
was not. This design makes no such assumption: it conditions on having been
selected and exploits variation in scale, then verifies with the same placebo
that the remaining variation is unrelated to prewar trajectory.

---

## 6b. Causal audit — the matched design works, within limits

`src/matched_plant_design.py`, `src/matched_estimates.py`, `src/matched_robustness.py`.

**Design.** Treatment is receipt of at least one plant that was publicly
financed (private structure share at most 5%), newly built (structures above
40% of cost), and large (at least $10 million): 181 plants worth $7.13bn in 144
counties. The 100 largest manufacturing counties of 1940 are dropped, leaving
2,973 counties of which 106 are treated. Propensity score on the prewar vector
with squares; at most three matches per treated unit within a 0.2 sd caliper on
common support. 105 of 106 treated counties match, to 237 distinct controls.

**Balance — passes.** Six of nine covariates are imbalanced beyond |SMD| > 0.10
before matching (log population differs by 1.43 sd). **After matching, zero of
nine exceed 0.10.**

**Placebo — passes.** No effect on 1930–40 population growth (p = 0.52), the
1940 manufacturing share (p = 0.66), or 1940 homeownership (p = 0.12). This is
precisely the test the IMP instrument failed.

**Estimates.** Log population 1970 +0.221 (p<0.01); manufacturing share 1970
+2.26 (p=0.010); log family income 1970 +0.087 (p<0.01); homeownership 1970
+1.97 (p=0.048). IPW agrees in sign and is slightly larger.

**Robustness — split verdict, and this is the important part.** Estimates are
stable across 3:1 and 5:1 matching and calipers of 0.1–0.5 sd, and across three
sample restrictions. One-to-one matching is unstable with 106 treated units
(manufacturing coefficient of +14.4) and is not relied upon; it is reported.

Against the demanding comparison — treated counties versus **their own
untreated neighbours**, sharing labour market, climate, and state — the
population effect (+0.132, p=0.012) and the manufacturing effect (+1.75,
p=0.031) survive. The income effect (p=0.30) and the homeownership effect
(p=0.50) **do not**.

### The "new plant" flag, recovered

The CPA volume marks new construction with a fourth line prefix, `!New Plant`,
printed beneath a facility's location. The parser originally treated those 338
lines as continuation text and discarded them. With the flag attached (319 of
338 resolve to a facility), Garin and Rothbaum's actual rule --- new = explicitly
designated OR structures above 40% of cost --- can be applied. Treatment rises
from 181 plants in 144 counties to **226 qualifying plants worth \$8.61bn**, of
which **214 resolve to a county, worth \$8.08bn across 164 counties** once
independent cities are folded into their parents. (An intermediate draft
reported 217 plants in 165 counties and \$8.42bn; that count predates the
independent-city merge and the Group 29 subtotal correction.)

Our 226 large new public plants capture **72.1%** of the \$11.94bn spent on all
new wartime plants; Garin and Rothbaum report their 353 plants capturing roughly
70% on the same base. (Two earlier figures were wrong on the denominator, not
the numerator: 89.4% divided by public plants only, and 93.9% is the share of
the *qualifying* dollars that resolve to a county, which is a coverage rate and
not comparable to their figure at all. The manuscript now names the base beside
each number, and `audit_paper_vs_data.py` checks all three.) The
count differs because our records are cost-rows while theirs are deduplicated
plant identifiers, so a plant split across products appears once for them and
several times for us. On the dimension that matters for treatment --- dollar
coverage --- ours is the tighter set.

### Military installations: a second, new causal design

`src/matched_military.py`. Treatment is the top decile of per-capita 1947 County
Data Book military facility spending: 56 counties, $2.15bn, 26% of national
military facility investment. Counties receiving both treatments are dropped.
52 of 56 match to 152 controls. **Imbalance falls from 8 of 9 covariates to 1.**
Placebo clean on 1930–40 population growth (p = 0.66) and the 1940
manufacturing share (p = 0.63).

| Outcome, 1970 | Large public plant | Military installation |
|---|---|---|
| Log population | +0.186*** | **+0.551*** |
| Manufacturing share | +3.14*** | **−4.72*** |
| Log family income | +0.087*** | +0.105*** |
| Homeownership | +1.81** | **−7.49*** |

No published estimate of the long-run effect of WWII military installations
exists; Garin and Rothbaum study industrial plants only. This is the paper's
novel causal contribution.

**Verdict.** Causal identification is claimed for population and manufacturing
structure only. The income and homeownership results hold against matched
controls drawn nationally but not against adjacent counties, consistent with
their reflecting regional rather than plant-level variation. The paper states
this boundary rather than reporting the four matched estimates as uniformly
causal.

---

## 6c. Adversarial validation of the two causal designs

Run after the designs were built, with the explicit aim of breaking them.

| Test | Result |
|---|---|
| **Threshold sensitivity (military)** | Re-estimated at the top 5%, 10%, 20%, 30% of per-capita military spending and at an absolute $10M cutoff. All five give the same signs at p<0.01, with magnitudes declining monotonically as the threshold relaxes (pop +0.87→+0.38, mfg −9.09→−4.04). Dose–response, not a threshold artefact |
| **Randomization inference (military)** | 500 permutations of treatment. Permutation p = 0.000 (population), 0.004 (manufacturing share), 0.000 (homeownership). Correct inference given 52 treated units, and it passes |
| **Residual imbalance** | Plant design: only `LONGITUD` exceeds 0.10 (0.111). Military design: only `popgrowth_3040` (0.106). Neither is outcome-relevant industrial structure |
| **Treatment contamination** | 119 plant-treated, 56 military-treated, only 2 both — against 2.2 expected under independence (Fisher exact p=1.00). The two treatments are statistically independent, which *corroborates* the orthogonality claim rather than threatening it |
| **Effect magnitude** | −7.49pp on homeownership is 0.84 sd. The raw treated-untreated gap is −9.4pp, so matching moves the estimate *toward* zero. Plausible |
| **Multiple testing** | 9 of 11 headline causal estimates survive Bonferroni at α = 0.05/11 = 0.0045. The two that fail are plant homeownership (p=0.013) and military 1960 manufacturing share (p=0.075) |

**Errors found and corrected during this audit:**

1. **Coverage figure was inflated.** "89.4% of new plant spending" used a
   public-plants-only denominator; on the base Garin and Rothbaum quote it is
   **72.1%**. Corrected in the paper and above.
2. **Two plant counts were both reported without reconciliation.** 226 is the
   count of qualifying plants (\$8.61bn); 214 is the subset that also resolves
   to a county (\$8.08bn). The twelve unresolved plants hold \$0.53bn. Both
   figures are now defined where used and checked against the records.
3. **19 of 338 `!New Plant` markers do not attach** to a facility (94.4%
   attach). Upper bound on the omission is 19 additional treated plants; the
   effect on the treated-county count is bounded and small.

---

## 6d. Manuscript audit

Structural defects found and fixed on a full pass of the LaTeX source.

| Defect | Evidence | Fix |
|---|---|---|
| **Duplicate section** | Two `\subsection` blocks both claiming `\label{sec:matched}`; the stale one carried numbers (7.44, 0.053, 21.1) no current script produces | 70-line block removed |
| **Duplicate table environments** | `tab:matched`, `tab:balance`, `tab:matchedplacebo` each defined twice; LaTeX silently numbered the second copy separately | Later duplicates removed |
| **Orphan tables** | `tabA_eventpath.tex`, `tabA_matchedsens.tex` existed on disk but no script in the pipeline generates them | Both removed from the manuscript |
| **Float placement** | 17 of 28 tables appeared more than one page from first mention; the worst gap was 25 pages | All floats moved to ordered end matter |
| **Numbering out of order** | Table 1 was referenced on p28 and printed on p5 | Tables renumbered by first mention; verified 1–23 in order |
| **Unreferenced tables** | 5 tables never cited in the body | References written into the relevant passages |
| **Stale conclusion** | The conclusion predated both causal designs and stated none of the findings | Rewritten, including an explicit statement of what is *not* claimed |
| **Typography** | 1 overfull hbox (28.9pt), in `tab:sources` | Wrapped in `resizebox`; now 0 overfull, 1 underfull (a long bibliography title) |

**Verification after the fix:** body text pp 1–27, tables pp 28–37, all 23
numbered in first-mention order, every table referenced, 0 LaTeX errors,
0 undefined references, 0 overfull boxes. Prose scores **0 / Clean** on the
`avoid-ai-writing` detector.

**The causal boundary is now stated in the conclusion**, not only in the results
section: the plant design's income and homeownership effects do not survive the
neighbour comparison (p = 0.30 and p = 0.50) and are labelled as associations
holding across regions rather than as effects of the plant.

---

## 6e. Manuscript-against-data audit

`src/audit_paper_vs_data.py`. Every quantitative claim in the manuscript is
checked twice: that the string appears in the source, and that it still equals
what the current artifacts produce. **38 claims checked, 0 not found, 0
mismatched.** Re-run it after any pipeline change.

**One stale claim found and corrected.** The manuscript stated that after
matching "none of the nine [covariates] exceeds 0.10". That was true when the
plant treatment held 106 counties; recovering the `!New Plant` flag expanded it
to 119, and longitude moved to $0.111$. The text now says eight of nine fall
below the threshold and names the ninth as a geographic coordinate rather than a
measure of economic structure. Every covariate describing prewar population,
urbanisation, racial composition, industrial structure, and growth remains
balanced.

### Exhibit placement

Essential exhibits sit in the body next to the passage that discusses them;
supporting material is in the appendix. Verified mechanically:

| Check | Result |
|---|---|
| Tables in body / appendix | 8 / 15 |
| Figures in body | 2 (pp 12–13) |
| Numbered in first-mention order | yes, 1–23 |
| Body exhibits >2 pages from first mention | 0 |
| Exhibits never referenced | 0 (both figures were uncited; now cited) |
| LaTeX errors / undefined refs / overfull boxes | 0 / 0 / 0 |

---

## 7. What a referee should still press on

1. **No causal design.** Section \ref{sec:iv} is honest about this, but the paper
   claims correspondence rather than effect and must be read that way. The
   Garin–Rothbaum matched-plant comparison is the credible route; $G_i$ is built
   (1,306 large public plants, 94.4% of public plant dollars) but not exploited.
3. **Selective Service is uncited.** $E_i^A$ is the output of an administrative
   screening process — local-board discretion, occupational and agricultural
   deferments, regionally varying rejection rates — that correlates with both
   prewar characteristics and $W^C$. The denominator is itself an outcome.
4. **Source concentration.** The Garin–Rothbaum replication package supplies
   seven of the eleven core quantities. The paper should disclose this.
5. **The digitisation of the contract volumes needs a citation.** The underlying
   record (`cpaContracts1946`) is verified from the file's own volume and page
   fields; the person who digitised it is not credited.

---

## 8. Reproduction

```bash
./.venv/bin/python src/validate_sources.py        # source quality profile
./.venv/bin/python src/parse_facilities.py        # CPA facilities -> plant level
./.venv/bin/python src/merge_independent_cities.py
./.venv/bin/python src/build_ds2_county.py        # NARA decode, 7.28M records
./.venv/bin/python src/build_master_panel.py      # 3,073-county panel
./.venv/bin/python src/build_instruments.py       # 1938 IMP instrument set
./.venv/bin/python src/three_geographies.py
./.venv/bin/python src/analysis_exposure.py
./.venv/bin/python src/composition.py
./.venv/bin/python src/regressions.py
./.venv/bin/python src/robustness.py
./.venv/bin/python src/iv_analysis.py
./.venv/bin/python src/iv_single.py
./.venv/bin/python src/iv_validity.py
./.venv/bin/python src/matched_plant_design.py   # treatment + sample
./.venv/bin/python src/matched_estimates.py      # balance, matching, effects
./.venv/bin/python src/matched_robustness.py     # parameters, samples, neighbours
./.venv/bin/python src/audit_trace.py             # provenance table
./.venv/bin/python src/make_tables.py && ./.venv/bin/python src/make_appendix.py
./.venv/bin/python src/make_iv_tables.py && ./.venv/bin/python src/make_maps.py
```

Significance throughout: * p<0.10, ** p<0.05, *** p<0.01.
