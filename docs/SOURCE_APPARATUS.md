# Source Apparatus — *Unequal Mobilization*

**Paper:** Joseph Blumberg, "Unequal Mobilization: Military Loss, Federal War
Investment, and the Geography of Postwar Development"
(`paper/War_Divergence.tex`, dated 27 August 2026).
**Apparatus compiled:** 28 August 2026.
**Scope:** all 24 `\bibitem` entries in the paper's `thebibliography`
environment, plus three synthesis sections.

This is a working document, not a defense. It exists so that (a) every citation
in the paper can be audited for whether it can actually bear the weight placed
on it, (b) the technical vocabulary the paper inherits from its sources is
written down in one place, and (c) the places where the citation set is thinner
than the argument are visible before a reader finds them.

Where I could not verify something from the `.tex` file or `DATA_LEDGER.md`, I
say so explicitly rather than inferring. Those flags are marked **[unverified]**.

---

## Table of Contents

- [Conventions](#conventions)
- [Equation index](#equation-index)
- **Part I — The 24 sources**
  - [A. Military exposure: records and universes](#a-military-exposure-records-and-universes)
    - [1. Ferrara, *WWII Enlistment and Casualty Records* (ICPSR 38927), 2024](#1-ferrara-wwii-enlistment-and-casualty-records-icpsr-38927-2024)
    - [2. War Department, *WWII Honor List of Dead and Missing Army and AAF Personnel*, RG 407, 1946](#2-war-department-wwii-honor-list-of-dead-and-missing-army-and-aaf-personnel-rg-407-1946)
    - [3. Navy Department, *State Summary of War Casualties*, RG 24, 1946](#3-navy-department-state-summary-of-war-casualties-rg-24-1946)
    - [4. U.S. Department of Veterans Affairs, *America's Wars*, 2025](#4-us-department-of-veterans-affairs-americas-wars-2025)
  - [B. Casualties as a labor-market and demographic shock](#b-casualties-as-a-labor-market-and-demographic-shock)
    - [5. Acemoglu, Autor & Lyle, "Women, War, and Wages" (2004)](#5-acemoglu-autor--lyle-women-war-and-wages-2004)
    - [6. Brodeur & Kattan, "World War II, the Baby Boom, and Employment" (2022)](#6-brodeur--kattan-world-war-ii-the-baby-boom-and-employment-2022)
    - [7. Ferrara, "World War II and Black Economic Progress" (2022)](#7-ferrara-world-war-ii-and-black-economic-progress-2022)
  - [C. War investment: the primary record](#c-war-investment-the-primary-record)
    - [8. CPA, *Alphabetic Listing of Major War Supply Contracts* (1946)](#8-cpa-alphabetic-listing-of-major-war-supply-contracts-1946)
    - [9. CPA, *War Industrial Facilities Authorized July 1940–August 1945* (1946)](#9-cpa-war-industrial-facilities-authorized-july-1940august-1945-1946)
    - [10. Brunet, Hilt & Jaremski, *Replication Data* (2025)](#10-brunet-hilt--jaremski-replication-data-2025)
  - [D. War investment: the econometric literature](#d-war-investment-the-econometric-literature)
    - [11. Fishback & Cullen, "Second World War Spending and Local Economic Activity" (2013)](#11-fishback--cullen-second-world-war-spending-and-local-economic-activity-2013)
    - [12. Garin & Rothbaum, "The Long-Run Impacts of Public Industrial Investment" (2025)](#12-garin--rothbaum-the-long-run-impacts-of-public-industrial-investment-2025)
    - [13. Jaworski, "World War II and the Industrialization of the American South" (2017)](#13-jaworski-world-war-ii-and-the-industrialization-of-the-american-south-2017)
    - [14. Jaworski & Yang, "Did War Mobilization Cause Aggregate and Regional Growth?" (2025)](#14-jaworski--yang-did-war-mobilization-cause-aggregate-and-regional-growth-2025)
    - [15. Brunet, "Stimulus on the Home Front" (2026)](#15-brunet-stimulus-on-the-home-front-2026)
  - [E. Civilian mobilization and household finance](#e-civilian-mobilization-and-household-finance)
    - [16. Brunet, Hilt & Jaremski, "War Bonds and Household Saving in WWII" (2025)](#16-brunet-hilt--jaremski-war-bonds-and-household-saving-in-wwii-2025)
  - [F. County outcomes and spatial harmonization](#f-county-outcomes-and-spatial-harmonization)
    - [17. Haines & ICPSR, *Historical, Demographic, Economic, and Social Data* (ICPSR 2896)](#17-haines--icpsr-historical-demographic-economic-and-social-data-icpsr-2896)
    - [18. Ferrara, Testa & Zhou, "New Area- and Population-based Geographic Crosswalks" (2024)](#18-ferrara-testa--zhou-new-area--and-population-based-geographic-crosswalks-2024)
  - [G. Rhetoric, propaganda, and the political history of sacrifice](#g-rhetoric-propaganda-and-the-political-history-of-sacrifice)
    - [19. Roosevelt, "Fireside Chat: On Sacrifice," 28 April 1942](#19-roosevelt-fireside-chat-on-sacrifice-28-april-1942)
    - [20. Winkler, *The Politics of Propaganda* (1978)](#20-winkler-the-politics-of-propaganda-1978)
    - [21. Sparrow, *Warfare State* (2011)](#21-sparrow-warfare-state-2011)
    - [22. American Historical Association, *GI Roundtable 13* (1945)](#22-american-historical-association-gi-roundtable-13-1945)
    - [23. NARA, *World War II Posters, 1942–1945* (Series 44-PA)](#23-nara-world-war-ii-posters-19421945-series-44-pa)
    - [24. NMAH, *Princeton University Poster Collection* (NMAH.AC.0433)](#24-nmah-princeton-university-poster-collection-nmahac0433)
- **Part II — Synthesis**
  - [S1. How the sources compose](#s1-how-the-sources-compose)
  - [S2. Dependency map](#s2-dependency-map)
  - [S3. Where the citation set is thin](#s3-where-the-citation-set-is-thin)
  - [S4. Corrections and open verification items](#s4-corrections-and-open-verification-items)

---

## Conventions

Each entry has five fields.

| Field | What it answers |
|---|---|
| **Citation** | Verbatim from the paper's bibliography, plus the cite key. |
| **Type** | The epistemic category. This governs what the source can prove. |
| **Key terms** | Vocabulary the source introduces that a reader must hold precisely to evaluate the paper's use of it. |
| **Function** | Which claim, variable, equation, or design decision rests on it — labelled **DATA**, **IDENTIFICATION**, **CONTEXT**, or **BENCHMARK**. |
| **Limits** | What the source cannot support; where a referee would push. |

The four function labels:

- **DATA** — the source supplies observations that enter a variable.
- **IDENTIFICATION** — the source supplies a research design, an exclusion
  argument, or a reason to prefer one estimator or sample over another.
- **CONTEXT** — the source supplies historical or rhetorical interpretation that
  frames the question but does not enter the estimation.
- **BENCHMARK** — the source supplies a number the paper's own construction must
  reproduce, or against which the paper's construction is validated.

A source can carry more than one label. Several do, and where a source carries
both DATA and IDENTIFICATION the entry says which claim rests on which.

Citation-frequency counts below (body vs. appendix) were taken by grepping the
`.tex` file; the appendix is the "Prospectus Supplement," which is explicitly
labelled as not part of the article.

---

## Equation index

The paper's equations are unnumbered in the source except for `eq:baseline`;
this apparatus refers to them by their compiled positions.

| Eq. | Content |
|---|---|
| (1) | $B_i^{\mathrm{civic}} = 1000\, D_i / P_{i,1940}$ — community loss |
| (2) | $B_i^{A} = 1000\, D_i^{A} / E_i^{A}$ — exposure-conditioned burden |
| (3) | $W_i^{C} = \operatorname{arsinh}(\text{contract dollars}_i / P_{i,1940})$ |
| (4) | $W_i^{F} = \operatorname{arsinh}(\text{facility dollars}_i / P_{i,1940})$ |
| (5) | $\mathbf{Y}_{it} = (\log P, M, \log w^{M}, H, \log y)$ |
| (6) | $p_i^D$, $p_i^W$ — county shares of national deaths and investment |
| (7) | $\mathcal{A} = \sum_i \min(p_i^D, p_i^W) = 1 - \tfrac12\sum_i \lvert p_i^D - p_i^W \rvert$ — overlap coefficient |
| (8) | Jensen–Shannon divergence between $p^D$ and $p^W$ |
| (9) | $I_i$ — standardized conditional imbalance index |
| (10) | `eq:baseline` — long-difference joint-treatment regression |

---

# Part I — The 24 sources

## A. Military exposure: records and universes

These four sources jointly determine what a "wartime death" is in this paper.
Because they do not agree on that definition, the paper's most consequential
sample decision — Army/AAF only for inference — is a direct consequence of
reading them against each other.

---

### 1. Ferrara, *WWII Enlistment and Casualty Records* (ICPSR 38927), 2024

**Citation.** A. Ferrara, *World War II Enlistment and Casualty Records, United
States, 1941–1945*, Inter-university Consortium for Political and Social
Research, 2024. doi:10.3886/ICPSR38927.v1. `[ferrara2024data]`
Cited 2× in the body (§2 Data availability, §3 Data), 2× in the appendix.

**Type.** Restricted-access research data deposit — a curated digitization of
federal administrative records, not a survey and not a sample. It is a
*derivative* of the NARA record series at entries 2 and 3, which is why those
two appear separately in the bibliography: the archival series define the
universe, the ICPSR deposit supplies the machine-readable rows.

**Key terms.**

- **DS1 / DS2 / DS3.** ICPSR's dataset numbering within a single study. DS1 is
  the Army/AAF fatality file (300,131 × 11); DS2 is the Army/AAF enlistment file
  (8,293,187 × 24); DS3 is the Navy/Marine Corps/Coast Guard casualty-list file
  (65,507 × 18). They are three different universes in one deposit, not three
  views of one universe.
- **Fallen.** The deposit's term for a person appearing on a service fatality
  list. It is broader than "killed in action": it includes non-battle deaths and
  administrative findings of death.
- **`STATUS` codes.** The fatality-type field in DS1. Verified distribution:
  KIA 171,530 (killed in action), DNB 82,479 (death, non-battle), DOW 24,786
  (died of wounds), FOD 18,888 (finding of death), M 1,352 (missing), DOI 912
  (died of injuries), blank 184.
  - **KIA** — died as a direct result of enemy action, at or near the point of
    injury.
  - **DOW** — wounded by enemy action, survived to reach medical care, died
    subsequently. Battle death for statistical purposes.
  - **DOI** — died of injuries not attributable to enemy action (vehicle
    accidents, industrial accidents in theater). Non-battle.
  - **DNB** — non-battle death: disease, accident, drowning, homicide, suicide,
    while in service. In WWII this is a large category, 27% of DS1.
  - **FOD** — *finding of death*: an administrative determination, under the
    Missing Persons Act of 1942, that a person missing for twelve months or more
    is presumed dead. The date attached to an FOD record is the date of the legal
    finding, not the date of death. This matters for any time-varying analysis.
  - **M** — still carried as missing at the time the list was closed.
- **`STATEICP` and `COUNTYID`.** DS1's geographic keys. `STATEICP` is the ICPSR
  state code (a numbering scheme predating and distinct from FIPS); `COUNTYID`
  is a three-digit county code that the ledger verified *is* the FIPS county
  code (Morgan IL→137, Bristol MA→005, Douglas WI→031). Combining them requires
  an ICPSR-state→FIPS-state crosswalk, which is why `crosswalk_statefip_stateicp_1910.dta`
  from the Garin–Rothbaum package is on the critical path.
- **ICPSR county code vs. FIPS county code.** Not the same numbering. ICPSR
  county codes are sequential within state in the Historical Census files; FIPS
  codes are the federal standard. Conflating them silently mis-assigns counties.
  A related trap: in Haines files, ICPSR county code `0` is the *state aggregate
  row*, not a county, and must be dropped — `src/overlap_analysis.py` does this.
- **`ENL_STATE` / `ENL_COUNTY`.** DS2's geographic keys. These are **NARA
  enlistment codes**, not FIPS, and they do not currently resolve: aggregation
  yields 11,410 state-county cells against roughly 3,100 real counties. This is
  the single open blocker on $E_i^A$.
- **`AGCT`.** Army General Classification Test score, recorded in DS2. It is not
  a clean numeric field — it contains coded values such as `"U5"`, so a naive
  numeric read fails. AGCT is the natural covariate for the paper's proposed
  "predicted fatality risk" decomposition.
- **County of residence at enlistment/induction.** The geographic concept in
  both files. It is *not* county of birth, county of family residence at death,
  or county the death notice was delivered to. A man who moved to a war-boom
  county for a defense job in 1941 and enlisted there is attributed to the boom
  county, not his origin. This is an endogeneity channel discussed under Limits.

**Function — DATA (primary), plus one IDENTIFICATION decision.**
This is the paper's military-exposure backbone. DS1 supplies $D_i^{A}$, the
numerator of both burden measures (Eq. 1 and Eq. 2). DS2 supplies $E_i^{A}$, the
denominator of Eq. 2. DS3 is used descriptively only. The deposit also supplies
the *identification* decision announced in §1 and defended in §2: because the
service-specific lists have non-identical universes, causal work is confined to
DS1 ∪ DS2 and the all-service map is descriptive. Every number in the ledger's
computed overlap result — $\mathcal{A}=0.455$, JS = 0.351 bits, Spearman
$\rho=0.612$ raw and $-0.034$ per capita — has DS1 on one side of it.

**Limits.**

- **The universes do not compose.** DS1 and DS3 must never be summed (ledger §2.1,
  trap 4). The paper states this; the reader should be told again wherever an
  all-service map appears.
- **DS2 geography is unresolved.** Until `ENL_STATE`/`ENL_COUNTY` are crosswalked
  to FIPS, Eq. 2 — the paper's *preferred* inferential burden measure — cannot be
  computed. The paper presents $B_i^A$ as the preferred measure while the panel
  actually computed so far uses $B_i^{\mathrm{civic}}$. That gap should be stated
  in the paper, not just in the ledger.
- **Enlistment records are not a census of service.** DS2 covers Army/AAF
  enlistments; it will not capture every path into service (e.g. transfers,
  certain officer commissions, National Guard federalization) uniformly.
  Using it as a denominator assumes coverage is not differentially incomplete
  across counties. That assumption is testable against Garin–Rothbaum's
  independent 3,073-county draft/volunteer file and should be tested.
- **Residence-at-enlistment is post-treatment for boom counties.** War
  production drew migrants into exactly the counties with high $W_i^C$. Those
  migrants then enlisted from the boom county. This mechanically correlates
  $D_i^A$ and $E_i^A$ with $W_i^C$ through migration rather than through
  sacrifice, and it biases $\mathcal{A}$ upward. The paper does not currently
  discuss this. It should.
- **FOD dating.** 18,888 records carry an administrative finding date. Any
  specification that uses death timing must treat these separately.
- **Restricted access.** The paper's §5 explicitly declines to report estimates
  because "the restricted or institutionally authenticated microdata required
  for that merge are not reproduced here." A reader cannot independently
  reproduce the merge from the article alone.

---

### 2. War Department, *WWII Honor List of Dead and Missing Army and AAF Personnel*, RG 407, 1946

**Citation.** United States War Department, *World War II Honor List of Dead and
Missing Army and Army Air Forces Personnel*, Record Group 407, National Archives
and Records Administration, 1946. `[naraArmy1946]` Cited 1× in the body (§2).

**Type.** Archival record series — the federal source document underlying DS1.
The paper cites it not to read it but to establish the *definition* of the DS1
universe from the record's own terms.

**Key terms.**

- **Honor list.** The War Department's published state-by-state, county-by-county
  roster of Army and Army Air Forces personnel who died or were carried as
  missing. Its purpose was commemorative and informational, addressed to the
  public and to next of kin; it was not designed as a statistical instrument.
  That origin explains both its county-level granularity (which is what makes
  this paper possible) and its definitional looseness.
- **Record Group 407.** The NARA record group of the Adjutant General's Office,
  the Army's personnel-records office. Record groups are NARA's top-level
  provenance unit, organized by the creating agency, not by subject.
- **"Dead and missing."** The list's own universe statement. It is inclusive of
  battle deaths, non-battle deaths, and persons whose deaths were established by
  administrative finding, and it retains persons still carried as missing. This
  is the sentence in the paper's §2 that does the work: "Army/AAF honor lists
  include battle and non-battle dead and missing."
- **County of residence.** The list's geographic organization is by state and
  county of record — in practice, the address of record at entry into service.
  See entry 1 on why that is not the same as home county.

**Function — IDENTIFICATION (definitional).**
This citation supports one sentence in §2, but it is a load-bearing sentence:
it establishes that the Army list is *broad*. Paired with entry 3, it produces
the non-comparability finding that determines the paper's inferential sample.
It contributes no rows to any variable; DS1 does that.

**Limits.**

- **Not a statistical publication.** The honor list has no methodology statement,
  no coverage audit, and no revision history in the way a Census product does.
  Claims about its completeness are inferences from its administrative purpose.
- **Compiled while cases were open.** Published in 1946, before all missing-person
  cases resolved. Later corrections exist in Army casualty files and are not
  reflected in the 1946 list.
- **The paper does not cite a specific published volume, edition, or NARA entry
  number.** For an archival citation this is thin. A referee working in
  military-records history will expect at minimum the series title as NARA
  catalogs it and, ideally, the specific state volumes consulted. **[unverified]**
  I cannot tell from the `.tex` whether Blumberg consulted the physical series or
  is citing it as the provenance of the ICPSR deposit. If the latter — which the
  usage pattern suggests — the entry should say so, e.g. "as digitized in
  [ferrara2024data]."

---

### 3. Navy Department, *State Summary of War Casualties*, RG 24, 1946

**Citation.** United States Department of the Navy, *State Summary of War
Casualties from World War II for Navy, Marine Corps, and Coast Guard Personnel*,
Record Group 24, National Archives and Records Administration, 1946.
`[naraNavy1946]` Cited 1× in the body (§2).

**Type.** Archival record series — the source document underlying DS3.

**Key terms.**

- **State summary.** The Navy's published compilation, organized by state, of
  casualties among Navy, Marine Corps, and Coast Guard personnel. "Summary" is
  literal: it is a roster within a state frame, not a national statistical table.
- **Record Group 24.** The record group of the Bureau of Naval Personnel
  (BuPers), the Navy's counterpart to the Army's Adjutant General.
- **The exclusion rule.** The critical fact, stated in the paper's §2 and the
  ledger's §2.1: these lists **exclude deaths occurring inside the United States**
  and **deaths from disease, homicide, or suicide**. The Army honor list excludes
  neither. Consequently the Navy series is closer to a battle-and-theater-death
  concept while the Army series is an all-cause in-service concept.
- **Next-of-kin residence.** The Navy summaries were organized around the address
  of next of kin, a different geographic concept again from the Army's address of
  record. DS3 carries full `FIPS`, `STATEFIPS`, `COUNTYFIPS`, `PLACEFIPS`, which
  makes it *geographically* easier to use than DS1 — and that convenience is
  exactly the trap, because its universe is narrower.

**Function — IDENTIFICATION (definitional), and a negative constraint.**
This is the source that forbids the obvious move. Because DS3's universe is
narrower than DS1's by two independent exclusions (place of death and cause of
death), summing them produces an "all-service total" whose implied definition is
"Army all-cause worldwide plus Navy battle-cause overseas" — a quantity that
corresponds to nothing. The paper's §2 sentence, "An all-service total created by
simple addition would therefore manufacture comparability that the sources do not
possess," is the cleanest statement of the constraint and it rests here.

**Limits.**

- Being a *constraint* source, its main risk is under-use rather than over-use.
  The paper states the exclusion rule once, in §2. If any figure in the final
  draft plots an all-service casualty map, the caption must repeat it.
- The paper does not quantify how large the excluded categories are. If Navy
  disease/accident/domestic deaths are, say, a fifth of Navy fatalities, a reader
  can calibrate the bias; without a number the warning is qualitative. The VA
  fact sheet (entry 4) gives an all-service other-deaths total of 113,842 and
  could be used to bound this.
- **[unverified]** Whether DS3's 65,507 observations equal the full Navy summary
  count or a digitized subset. The ledger reports the row count but not a
  reconciliation against the published Navy totals.

---

### 4. U.S. Department of Veterans Affairs, *America's Wars*, 2025

**Citation.** U.S. Department of Veterans Affairs, *America's Wars*, Veterans Day
Teachers Resource Guide, 2025. `[va2025]` Cited 1× in the body (§2, opening).

**Type.** Reference statistic — a government fact sheet, not a research product.
It compiles official casualty totals for public and educational use.

**Key terms.**

- **Battle deaths.** VA's category for deaths resulting from hostile action:
  291,557 for WWII. Corresponds roughly to KIA + DOW across all services.
- **Other deaths in service.** VA's category for non-hostile deaths during the
  service period: 113,842 for WWII. Corresponds roughly to DNB + DOI.
- **In-theater vs. worldwide.** VA's WWII figures are worldwide in-service
  counts, not theater-restricted. This is why they exceed any theater-based
  tally and why they are *not* directly comparable to the Navy state summaries.

**Function — BENCHMARK.**
This is the paper's opening scale-setting sentence and its only external
arithmetic check on the ICPSR deposit. It anchors the reader before the paper
disaggregates. It also supports an internal consistency test the paper does not
currently run but should: DS1's battle-type statuses (KIA 171,530 + DOW 24,786 =
196,316) plus the Navy/USMC/USCG battle deaths should approximately reconcile to
VA's 291,557; DS1's DNB + DOI (83,391) should sit inside VA's 113,842. Running
and reporting that reconciliation would materially strengthen §2.

**Limits.**

- **It is a teaching resource, not a statistical series.** It has no methodology
  appendix and no county or state breakdown. It cannot validate anything about
  geography — only about national totals.
- **Category mismatch with DS1.** VA's 291,557 is all-service battle deaths;
  DS1's 300,131 is Army/AAF all-status. These two numbers appear within three
  sentences of each other in §2 and a careless reader will compare them. The
  paper should insert one clause making the non-comparability explicit at the
  point of juxtaposition, not only later in the paragraph.
- **VA totals have themselves been revised over decades**, and the 2025 guide is
  a snapshot. Citing a dated resource guide rather than a stable series (e.g. the
  Congressional Research Service's *American War and Military Operations
  Casualties*, RL32492, which the ledger notes is already filed in
  `data/docs/literature/`) is a weaker choice. **The CRS report is on disk and
  uncited.** That is an easy fix.

---

## B. Casualties as a labor-market and demographic shock

These three establish that military death is not a demographic subtraction with
a single sign. They supply the mechanisms the paper's outcome vector is built to
detect, and two of them supply county-level design precedent.

---

### 5. Acemoglu, Autor & Lyle, "Women, War, and Wages" (2004)

**Citation.** D. Acemoglu, D. H. Autor, and D. Lyle, "Women, War, and Wages: The
Effect of Female Labor Supply on the Wage Structure at Midcentury," *Journal of
Political Economy*, 112(3), 2004, 497–551. `[acemoglu2004]`
Cited 1× in the body (§1 only). Not cited in the Data or Empirical Strategy
sections.

**Type.** Peer-reviewed article — the canonical labor-economics use of WWII
mobilization as a source of quasi-experimental variation.

**Key terms.**

- **Mobilization rate.** The share of a state's registered men of military age
  who were drafted or enlisted. Acemoglu–Autor–Lyle exploit its large
  cross-state variation (roughly 41% to 54% across states) as a shifter of male
  labor supply. This is *the* precedent for treating wartime military withdrawal
  as a spatially varying treatment.
- **Labor supply shifter / instrument.** The mobilization rate is used to
  instrument for postwar female labor supply, on the argument that state
  mobilization differences were driven by Selective Service administration and
  demographic composition rather than by local labor demand.
- **Wage structure.** The full distribution of wages, not the mean — specifically
  the female-male gap and the returns to skill. Their finding is that greater
  female labor supply depressed female wages and, through imperfect
  substitutability, also affected male wages.
- **Imperfect substitutability.** The assumption that men and women (or workers
  of different skill) are not perfect substitutes in production, which is what
  makes a supply shift move relative wages rather than only quantities.

**Function — CONTEXT, with unrealized IDENTIFICATION potential.**
In the paper as written this is a one-sentence literature marker in §1: it
establishes that mobilization has been used as spatial variation before. It does
**not** currently supply a method the paper adopts. This is a missed opportunity
and a soft spot: the paper's $E_i^A$ denominator in Eq. 2 is conceptually a
county-level mobilization rate, and Acemoglu–Autor–Lyle is the natural source for
both the concept and the objections to it. Elevating this citation from §1 into
§4 would strengthen the defense of Eq. 2 considerably.

**Limits.**

- **Wrong unit.** Their variation is across *states* (48 units). The paper works
  across ~3,100 counties. State mobilization rates were shaped by Selective
  Service quota administration at the state level; county variation within a
  state is driven by local draft boards, local occupational deferment patterns,
  and local rejection rates — a different and less well-defended source of
  variation. Borrowing their exogeneity argument at the county level is not
  automatic.
- **Different outcome.** Their outcomes are female labor supply and wages, not
  local development. The paper's $\mathbf{Y}_{it}$ includes female LFP as a
  secondary outcome, so there is partial overlap, but the primary outcomes are
  not theirs.
- **Mobilization ≠ fatality.** Their treatment is men *removed*; the paper's is
  men *killed*. A county could have high mobilization and low fatality
  (concentration in non-combat branches or stateside assignments) or the reverse.
  Conflating them would be an error, and the paper is right to distinguish
  $E_i^A$ from $D_i^A$ — but it should say explicitly that its treatment differs
  from Acemoglu–Autor–Lyle's.

---

### 6. Brodeur & Kattan, "World War II, the Baby Boom, and Employment" (2022)

**Citation.** A. Brodeur and L. Kattan, "World War II, the Baby Boom, and
Employment: County-Level Evidence," *Journal of Labor Economics*, 40(2), 2022,
437–471. `[brodeur2022]` Cited 3× in the body (§1, §2, §5), 1× in the appendix.

**Type.** Peer-reviewed article — the closest existing precedent for the paper's
casualty side, at the paper's own unit of analysis.

**Key terms.**

- **County-level casualty rate.** Their treatment: wartime deaths normalized by
  county population. This is essentially the paper's $B_i^{\mathrm{civic}}$
  (Eq. 1), which makes their paper the direct methodological ancestor of the
  paper's descriptive burden measure.
- **Baby boom.** The sustained rise in US fertility from roughly 1946 to 1964.
  "A smaller baby boom" means a smaller *increase* relative to prewar fertility,
  not a decline.
- **Difference-in-differences (DiD).** Comparing the change in an outcome
  before-to-after treatment in high-treatment units against the same change in
  low-treatment units, so that time-invariant unit differences and common time
  shocks difference out. The identifying assumption is *parallel trends*: absent
  treatment, the two groups' outcomes would have moved together. The paper's
  Eq. 10 is a long-difference variant of this, and its proposed use of 1920 and
  1930 outcomes is a pretrend test of exactly this assumption.
- **Marriage market / sex ratio.** The ratio of men to women of marriageable age.
  Casualties reduce it, which affects marriage rates and hence fertility. This is
  a distinct mechanism from the direct removal of potential fathers.
- **Female employment.** Their positive 1950s result. It is what makes a signed
  prediction for casualties impossible: the same shock lowers fertility and
  raises women's employment and household income.

**Function — CONTEXT and IDENTIFICATION.**
Three distinct jobs. In §1 it establishes that county casualty variation predicts
demographic and labor outcomes. In §2 it is one of the two sources
(with Ferrara 2022) supporting the theoretical claim that "a single signed
casualty effect" is implausible — which is the justification for the
multidimensional $\mathbf{Y}_{it}$ in Eq. 5. In §5 it is empirical premise three.
It also supplies design precedent: a referee asking "can county casualty rates
be used as a treatment?" is answered by pointing at a *JOLE* paper that did it.

**Limits.**

- **Their casualty source may differ from DS1.** **[unverified]** I have not
  confirmed which casualty file Brodeur–Kattan use or whether it shares DS1's
  universe. If they use an all-service or a battle-death-only universe, then
  their estimates and the paper's $B_i^A$ are not measuring the same thing, and
  the paper's use of them as a *premise* is looser than it reads. This is worth
  checking directly before the next draft.
- **Population denominator, not exposure denominator.** Their measure is the
  paper's Eq. 1, which the paper itself demotes to descriptive use in favor of
  Eq. 2. The paper cannot simultaneously argue that population-denominated
  burden confounds age–sex composition *and* lean on results built on it without
  comment. One sentence acknowledging this would close the gap.
- **Fertility and employment are not the paper's primary outcomes.** They are
  secondary. Their results constrain interpretation; they do not validate the
  paper's main specification.
- **Endogeneity of casualty rates.** Counties differed in who served, in which
  branch, and with what combat exposure. Brodeur–Kattan face this too; the paper
  proposes to do better via composition-adjusted predicted fatality risk (§4).
  That proposal is currently uncited to any methodological source.

---

### 7. Ferrara, "World War II and Black Economic Progress" (2022)

**Citation.** A. Ferrara, "World War II and Black Economic Progress," *Journal of
Labor Economics*, 40(4), 2022, 1053–1091. `[ferrara2022]`
Cited 3× in the body (§1, §2, §5), 1× in the appendix.

**Type.** Peer-reviewed article. Same author as the ICPSR deposit (entry 1),
which matters: this paper is the research use case the data were built for, and
its measurement choices are the deposit's implicit documentation.

**Key terms.**

- **Semiskilled.** An occupational stratum between unskilled labor and skilled
  craft work — operatives, machine tenders, assembly workers. In the 1940s
  classification these are largely Census "operatives and kindred workers." The
  category matters because it is where wartime industrial expansion created
  openings and where White and Black workers were closest to substitutable.
- **Occupational upgrading.** Movement of a group into higher-paying or
  higher-status occupations, measured here as a shift in the occupational
  distribution rather than a within-occupation wage gain. Distinct from
  wage growth: a worker can upgrade occupation with little immediate pay change.
- **Employer learning.** The mechanism: employers holding pessimistic or
  uninformed priors about Black workers' productivity are forced by labor
  scarcity to hire them, observe actual productivity, and revise. The upgrading
  then persists after the scarcity ends. This is why a *temporary* shock can
  produce a *permanent* compositional change — precisely the logic the paper
  needs for casualties to have 1970 effects.
- **Statistical discrimination.** The prior that employer learning corrects:
  using group membership as a proxy for unobserved individual productivity.
- **Substitution vs. complementarity.** Whether Black workers filled the specific
  slots vacated by White semiskilled casualties (substitution) or benefited from
  general expansion (complementarity). Ferrara's identification turns on the
  former.
- **The 35 percent figure.** Ferrara's estimate that White semiskilled casualties
  plus employer learning account for roughly 35% of Black occupational upgrading
  at midcentury. The paper quotes this in §5 as empirical premise three.

**Function — CONTEXT and mechanism; source of one secondary outcome.**
It supplies the causal story by which casualties change the *distribution* of
opportunity without necessarily moving mean county income — which is the paper's
stated reason for a multidimensional $\mathbf{Y}$ (Eq. 5) and for its "Black
semiskilled employment" secondary outcome. In §5 it is a benchmark the paper's
own casualty-side estimates will be read against.

**Limits.**

- **Casualty composition, not casualty count, is the treatment.** Ferrara's
  variation is deaths *among semiskilled White soldiers* — an interaction of
  fatality with prewar occupation. The paper's $D_i^A$ and $B_i^A$ are
  undifferentiated counts. The paper cannot claim Ferrara's mechanism operates
  in its design unless it also builds the occupational split, which DS2's
  enlistment records (which carry civilian occupation codes) would permit. This
  is a real, buildable extension and it is not currently in the paper.
- **Author overlap is not independence.** Ferrara built the data and wrote the
  paper. Using his estimates to validate a design built on his data is not
  external corroboration. The Garin–Rothbaum `WWII_draft_volunteer_casualties_Army_AirForce.dta`
  file (3,073 counties) is the genuinely independent check and the ledger already
  flags it.
- **The 35% is a decomposition, not a reduced-form treatment effect.** Quoting it
  as an empirical premise is fine; treating it as a coefficient the paper must
  reproduce would be a category error.

---

## C. War investment: the primary record

The two Civilian Production Administration volumes are the origin of essentially
every county war-spending series in the literature, including Fishback–Cullen's,
Garin–Rothbaum's, and the reconstruction this paper prefers. Understanding what
they do and do not record is therefore not archival pedantry — it is the
measurement foundation of $W_i^C$, $W_i^F$, and $G_i$.

---

### 8. CPA, *Alphabetic Listing of Major War Supply Contracts* (1946)

**Citation.** United States Civilian Production Administration, *Alphabetic
Listing of Major War Supply Contracts: Cumulative June 1940 Through September
1945*, Industrial Statistics Division, Washington, DC, 1946.
`[cpaContracts1946]` Cited 2× in the body (§2, §3), 1× in the appendix.

**Type.** Government dataset published as a printed record series — a
contemporaneous administrative compilation, not a retrospective estimate.

**Key terms.**

- **Civilian Production Administration (CPA).** The successor agency to the War
  Production Board, created by executive order in October 1945 to manage
  reconversion from war to civilian production. Its Industrial Statistics
  Division inherited WPB's contract records and published them as the war closed.
  So the *authorship* is CPA but the *records* are WPB's wartime accounting.
- **War supply contract.** A procurement contract for goods or services awarded
  by a federal war agency (principally the War Department, Navy Department,
  Maritime Commission, and Treasury Procurement).
- **Major.** The listing's inclusion threshold. Contracts below the threshold are
  omitted entirely, which is why the derived county series has genuine structural
  zeros rather than merely small values — and why "$W_i^C = 0$" means "no *major*
  contract," not "no federal money." The paper's arsinh transform (Eq. 3) is
  chosen partly to preserve these zeros; the reader must know they are
  threshold-induced.
- **Prime contract vs. subcontract.** A **prime contract** is the award from the
  government to a contractor. A **subcontract** is work that prime contractor
  passes down to another firm. The CPA listing records **prime contracts only.**
  This is the single most important limitation on $W_i^C$: during WWII an
  enormous share of production value flowed through subcontracts — the Smaller
  War Plants Corporation existed precisely to force prime contractors to
  subcontract to small firms — and none of it appears in this series at the
  subcontractor's location.
- **Place of contract vs. place of performance.** The listing records the
  contractor's address. For a multi-plant corporation this can be the corporate
  headquarters or the awarding division, not the factory where the work was
  physically done. Assigning contract dollars to the listed city therefore
  assigns them to an administrative location, which may or may not be the
  production location.
- **Contract value vs. outlay.** The recorded figure is the face value of the
  award. Contracts were routinely renegotiated downward under the Renegotiation
  Act of 1942 (to recapture excess profits), cancelled at war's end, or
  supplemented. Recorded value is therefore an upper-bound intention, not a
  realized cash flow.
- **Industrial Statistics Division.** The WPB/CPA unit responsible for the
  statistical accounting of war production. Its conventions define the series.

**Function — DATA (upstream), via reconstruction.**
The paper cites this volume as the *provenance* of its contract measure. The
actual rows in `data/raw/contracts/WWII_contracts_clean.dta` (190,693 × 22) are a
modern reconstruction from these records — carrying `city_name`, `state`,
`fips_state`, value, product, agency, and dates, with **no county FIPS**, which
is why the city→county crosswalk work in ledger §3.1 exists at all. $W_i^C$
(Eq. 3), the $p_i^W$ share in Eq. 6, and therefore $\mathcal{A}$ in Eq. 7 all
trace back here.

**Limits.**

- **Prime-only measurement is a first-order bias for $\mathcal{A}$.** If
  subcontracting dispersed production far more widely than prime awards suggest,
  then the true geography of war *work* was less concentrated than $W_i^C$ shows,
  and the computed $\mathcal{A}=0.455$ is biased downward. The paper's headline
  divergence result would be partly an artifact of measuring awards rather than
  activity. This deserves an explicit paragraph, not a footnote.
- **Geocoding loss is non-random.** The ledger is admirably candid: the residual
  2.0% of dollars (8,247 rows, $3.61bn of $181.0bn, across 711 city-states)
  "concentrates in dense industrial metros whose plant addresses used
  neighborhood names." So the unmatched dollars are exactly the ones that would
  raise measured concentration. Top-20 and top-100 shares are understated.
- **Nominal dollars, cumulative 1940–45.** No deflation, no timing. A county that
  received its dollars in 1941 and one that received them in 1945 are identical
  in $W_i^C$, though their postwar capital stocks would differ.
- **Per-capita denominator choice.** Eq. 3 divides by 1940 population. For a
  county whose population tripled because of the contract, this is the right
  predetermined denominator — but it also means $W_i^C$ can take enormous values
  for small rural plant counties, which is precisely why the arsinh transform is
  applied. The reader should be told that the transform is doing leverage control,
  not just zero-handling.

---

### 9. CPA, *War Industrial Facilities Authorized July 1940–August 1945* (1946)

**Citation.** United States Civilian Production Administration, *War Industrial
Facilities Authorized July 1940–August 1945: Listed Alphabetically by Company and
Plant Location*, Industrial Statistics Division, Washington, DC, 1946.
`[cpaFacilities1946]` Cited 2× in the body (§2, §3), 1× in the appendix.

**Type.** Government dataset published as a printed record series. Its modern
machine-readable form on disk is `FacilitiesDatabase.xls` (6.2 MB) inside the
Garin–Rothbaum package.

**Key terms.**

- **Industrial facility (as against supply contract).** A *plant* — buildings,
  machinery, and land — rather than an order for goods. This distinction is the
  conceptual spine of the paper's decomposition into $W_i^C$ and $W_i^F$: a
  contract is demand that ends when the war ends; a facility is capital that
  physically remains.
- **Authorized.** The listing's universe term. It records projects *approved* for
  construction, at their approved cost. Some were cancelled, deferred, or
  completed at different cost. "Authorized dollars" is therefore not "capital in
  place in 1946."
- **Publicly financed plant.** A facility built with federal money and owned by
  the federal government — typically through the **Defense Plant Corporation
  (DPC)**, a subsidiary of the **Reconstruction Finance Corporation (RFC)**, or
  directly by the War or Navy Departments. This is the subset the paper's $G_i$
  treatment indicator is meant to capture.
- **GOCO — government-owned, contractor-operated.** The dominant public-plant
  model: the government built and owned the plant; a private firm ran it under
  contract. After the war, many GOCO plants were sold to their operators under
  the Surplus Property Act of 1944, converting public capital into private
  industrial capacity in situ. That disposal process is the actual mechanism by
  which a wartime plant becomes a 1970 manufacturing base.
- **Privately financed facility with a certificate of necessity.** The
  alternative model: a firm built the plant with its own capital but received a
  certificate allowing **accelerated amortization** — writing the investment off
  over five years instead of its normal life, a large tax subsidy. These plants
  appear in the same CPA listing but are *not* public capital. Failing to
  separate them would contaminate $G_i$.
- **Plant location.** Unlike the contracts volume, this listing is organized by
  company *and plant location*, so the geography is closer to the site of
  physical capital. This is why $W_i^F$ is the better-geocoded of the two
  investment measures.

**Function — DATA, and the basis of the paper's central decomposition.**
Supplies $W_i^F$ (Eq. 4) and the large-public-plant indicator $G_i$. The
theoretical argument in §2 — that "the postwar economic legacy of mobilization
depended not only on how much the federal government spent nationally but on
where durable capital remained after military demand collapsed" — is only
testable because this series exists separately from the contracts series.

**Limits.**

- **Not yet parsed.** Ledger §4.2 lists "$W_i^F$ and $G_i$ from
  `FacilitiesDatabase.xls`" as **open**. Both Eq. 4 and $\theta_F$ in Eq. 10 are
  currently unbuilt. The paper describes them as if constructed; the draft should
  either build them or mark them prospective.
- **Public/private split is a construction decision, not a field.** Whoever
  builds $G_i$ must choose the ownership and size criteria. Garin–Rothbaum made
  those choices; if the paper wants to "parallel" them (§3) it must replicate
  their criteria exactly, or its $G_i$ is a different treatment with the same
  name.
- **Authorized cost ≠ realized capital.** Discussed above. A robustness check
  against completed-plant inventories (e.g. RFC/DPC disposal records) would be
  the honest response.
- **Facilities and contracts are correlated by construction.** Plants were built
  where contracts were awarded, and vice versa. Entering $W_i^C$ and $W_i^F$
  jointly in Eq. 10 means the coefficients are partial effects under
  multicollinearity. The paper should report their correlation and the variance
  inflation, or a referee will ask.

---

### 10. Brunet, Hilt & Jaremski, *Replication Data* (2025)

**Citation.** G. Brunet, E. Hilt, and M. Jaremski, *Replication Data for "War
Bonds and Household Saving in WWII"*, Princeton University Data and Statistical
Services, 2025. `[brunetReplication2025]`
Cited 3× in the body (§2, §3, §5), 1× in the appendix.

**Type.** Replication package — a data-and-code deposit accompanying a published
article.

**Key terms.**

- **Replication package.** The archived dataset and code that reproduce a
  published paper's results. Citing one is a *provenance* claim about where data
  came from, distinct from citing the article, which is a claim about a finding.
- **Reconstruction (of the contract series).** Rebuilding the county war-spending
  measure from the original CPA contract records rather than inheriting the
  aggregated 1947 County Data Book figures. The point of reconstruction is that
  the aggregation step in the legacy series introduced error.
- **True zero.** A county that genuinely received no major war supply contract,
  as opposed to a county recorded as zero because of an aggregation or matching
  failure — or recorded as nonzero because of one. The reconstruction's claim is
  that there are *more* true zeros than the legacy series shows, meaning the
  legacy series has spurious positive values.

> **⚠ Provenance flag — this is the most likely citation error in the paper.**
> The paper attributes the contract *reconstruction* to this deposit in three
> places, including §5 empirical premise one. But `DATA_LEDGER.md` §6 records the
> contract file's provenance as "**Brunet–Koustas** WWII Major War Supply
> Contracts (via Goldin–Olivetti–Ferrie replication)" — a different dataset with a
> different coauthor, reached through a different replication archive. The
> war-bonds paper is about Series E bond sales and bank deposits; it is not the
> obvious home of a 190,693-row contract reconstruction. Either the ledger or the
> bibliography is wrong. Resolve this before submission: the correct citation is
> plausibly Brunet (2026) `[brunet2026]` and/or a separate Brunet–Koustas data
> source that is currently **absent from the bibliography entirely**. See §S4.

**Function — DATA (provenance) and BENCHMARK, as currently written.**
It is cited for (a) the source of the reconstructed contract series preferred
over the County Data Book (§3), (b) the claim that reconstruction finds more true
zeros than the legacy series (§2, §5). Claim (b) is a substantive empirical
finding and it is *the* justification for demoting the County Data Book measure
to a robustness check. If the citation is misattributed, that justification is
currently unsourced.

**Limits.**

- A replication package can establish *what data exist*; it cannot by itself
  establish a *finding* about true zeros. That finding belongs to a paper. Even
  if the deposit is the right provenance, claim (b) should cite the article that
  makes the argument.
- The paper never states the reconstruction's own coverage rate or its criteria
  for a match, so a reader cannot judge whether its "more true zeros" reflect
  better measurement or stricter matching. The ledger's 95.7%-of-rows /
  98.0%-of-dollars match statistics are the paper's own, not the source's.
- **[unverified]** I have not opened the replication package and cannot confirm
  its contents. The flag above rests on the ledger's provenance line and on the
  title of the associated article, not on inspection.

---

## D. War investment: the econometric literature

Five articles. Two of them (Fishback–Cullen, Garin–Rothbaum) do heavy structural
work in the paper; three are literature markers cited once or twice.

---

### 11. Fishback & Cullen, "Second World War Spending and Local Economic Activity" (2013)

**Citation.** P. V. Fishback and J. A. Cullen, "Second World War Spending and
Local Economic Activity in US Counties, 1939–58," *Economic History Review*,
66(4), 2013, 975–992. `[fishback2013]`
Cited **6× in the body** — the most-cited source in the paper — plus 1× in the
appendix. Appears in §1, §2 (twice), §4, §5 (twice).

**Type.** Peer-reviewed article. The foundational county-level study of WWII
spending and postwar local outcomes.

**Key terms.**

- **County Data Book (1947).** A Census Bureau reference volume compiling county
  statistics, including a war-supply-contract figure. This is the "legacy county
  series": for decades it was the only readily available county war-spending
  measure, and it is what Fishback–Cullen use. On disk as Haines DS0070.
- **War supply contracts per capita.** Their spending measure, normalized like
  the paper's Eq. 3 though without the arsinh transform.
- **Population growth vs. per-capita activity.** Their central distinction and
  the paper's inheritance: wartime spending is strongly associated with
  *population* growth but weakly with long-run *per-capita* income or activity.
  In other words, war spending moved people more than it made places richer per
  head. This is the single result that most shapes the paper's design.
- **Long differences.** Regressing the change in an outcome between two distant
  dates on a treatment measured in between, with predetermined controls — as
  against a panel with unit fixed effects. Eq. 10 is a long difference.
- **1938 Industrial Mobilization Plan.** A prewar War Department plan identifying
  industrial capacity for potential conversion. Because it predates the war, it
  is a candidate *predetermined predictor or instrument* for contract placement.
  The paper cites Fishback–Cullen and Jaworski jointly for this in §4, and
  correctly restricts its use to cases where the exclusion restriction can be
  defended — prewar industrial capacity plausibly affects postwar outcomes
  directly, which is the standard objection.
- **The top-twenty share.** Their finding that roughly two-fifths (≈40%) of major
  wartime spending accrued to the top twenty counties. Quoted in §2 and §5.

**Function — all four labels at once.**
- **CONTEXT**: establishes the field's baseline understanding (§1).
- **IDENTIFICATION**: their population/per-capita split is the argument for the
  multidimensional $\mathbf{Y}$ (Eq. 5); their treatment of the 1938 IMP is the
  precedent for the paper's instrument discussion (§4).
- **BENCHMARK**: the ≈40% top-twenty share is the external validation target for
  the paper's independently built contract series. The ledger's computed value is
  **43.8%**, built from a different source through a different crosswalk. That
  agreement is the strongest evidence that the city→county match in ledger §3.1
  is sound, and it belongs in the paper as a validation exhibit, not only in the
  ledger.
- **DATA (indirect)**: their series, via the County Data Book, is the robustness
  comparison for $W_i^C$.

**Limits.**

- **Their measure is the one the paper demotes.** The paper simultaneously uses
  Fishback–Cullen's ≈40% as a validation benchmark *and* argues (via entry 10)
  that the series producing that number contains "nontrivial noise among places
  with little or no major federal production spending." Both can be true — the
  top-twenty share is robust to noise in the zero tail — but the paper should say
  so explicitly, because as written the two uses sit uneasily together.
- **1939–58 window.** Their outcome window closes in 1958; the paper's runs to
  1970. Garin–Rothbaum's persistence results are what license the extension, not
  Fishback–Cullen.
- **Aggregate spending, undecomposed.** They pool contracts and facilities. The
  paper's entire $W^C$/$W^F$ split is an argument that this pooling obscures the
  mechanism. That is a legitimate criticism, but it means their coefficients are
  not directly comparable to $\beta_C$ or $\beta_F$ in Eq. 10.
- **Conditional associations, not causal effects.** Their design faces the same
  endogenous-placement problem the paper acknowledges in §4.

---

### 12. Garin & Rothbaum, "The Long-Run Impacts of Public Industrial Investment" (2025)

**Citation.** A. Garin and J. Rothbaum, "The Long-Run Impacts of Public
Industrial Investment on Local Development and Economic Mobility: Evidence from
World War II," *Quarterly Journal of Economics*, 140(1), 2025, 459–520.
`[garin2025]` Cited 5× in the body (§1, §2, §3, §4, §5), 1× in the appendix.

**Type.** Peer-reviewed article **and**, through its Harvard Dataverse
replication package (doi:10.7910/DVN/NGRAWI, 731 MB on disk), the paper's single
largest data dependency. It is worth stating plainly: this one package supplies
the plant data, the city→county crosswalk that makes $W_i^C$ possible at all, an
independent county casualty file, the prewar control vector, county coordinates,
county adjacency, and the combined 1947–77 County Data Books.

**Key terms.**

- **Publicly financed plant.** See entry 9. Garin–Rothbaum's contribution is
  isolating this subset from the CPA facilities universe and treating it as the
  policy object.
- **Quasi-experimental placement.** The identification claim: because plant
  siting was shaped in part by wartime *security* considerations — dispersing
  strategic production away from coasts and away from existing industrial
  concentrations — placement is partly orthogonal to local economic potential.
  The paper adopts this argument verbatim in §4 ("plants whose placement outside
  major industrial centers was shaped partly by wartime security considerations").
- **Matched comparison counties.** Constructing a control group of counties
  similar on observables to plant counties, so that the comparison is not
  plant-counties-vs-everywhere.
- **Incumbent residents vs. in-migrants.** The distinction that separates a
  *place* effect from a *composition* effect. A county can show higher 1970
  income because the people already there did better, or because richer people
  moved in. Garin–Rothbaum can separate these because they link individuals;
  their finding that prewar-born men in plant counties earned ~2.5% more
  annually is an incumbent-resident effect.
- **Economic mobility.** Intergenerational outcomes — whether children raised in
  plant counties did better than comparable children elsewhere.
- **The 1970 benchmark set.** Quoted in §5: plant counties had roughly **30% more
  manufacturing employment, 20% larger populations, 7–8% higher median family
  income**, and prewar-born men earned about **2.5% more annually**.

**Function — IDENTIFICATION (primary), DATA (very large), BENCHMARK.**
- **IDENTIFICATION**: supplies the strongest available exclusion argument on the
  investment side, and it is the design $G_i$ is built to parallel (§3, §4). It
  also supplies the *reason* for the $W^C$/$W^F$ split (§2, §5): durable capital
  persisted where procurement flow did not.
- **DATA**: `cw-city-county.dta` (25,131 rows) is the reason 98.0% of contract
  dollars have a county at all; `fishbackhorracekantor.dta` (3,067 counties × 130
  variables) *is* the $X_i$ vector in Eqs. 9 and 10 and supplies `LATITUDE`/
  `LONGITUD` for Conley spatial errors; `NBER_county_adjacency2010.dta` (22,200
  pairs) supplies spatial weights; `FacilitiesDatabase.xls` will supply $W_i^F$
  and $G_i$; `WWII_draft_volunteer_casualties_Army_AirForce.dta` (3,073 counties)
  is the independent casualty cross-check; `ccdb47_77.dta` supplies the County
  Data Book robustness measure; `cw_cty_czone.dta` supplies commuting zones.
- **BENCHMARK**: the 1970 magnitudes are what any facility-side estimate in this
  paper must be read against.

**Limits.**

- **Concentration risk.** Roughly half the paper's identifying infrastructure
  comes from one replication package. If any of its crosswalks or control
  constructions is wrong, several of the paper's variables move together. Note
  also ledger trap 5: G&R's `Census*.dta` files are **byte-identical** to Haines
  files, so agreement between them is not independent corroboration.
- **The security-siting exclusion restriction is contestable.** Dispersion policy
  was not the only siting criterion — labor availability, power, rail access, and
  political influence all mattered. Adopting the argument requires reproducing
  their sample restrictions, not just citing them. **[unverified]** I have
  summarized their design from the paper's characterization plus general
  knowledge; verify the exact restrictions before claiming to follow them.
- **Their outcome data include restricted administrative records** (linked census
  and earnings). The paper cannot replicate the incumbent-earnings result without
  equivalent access, and §5 already concedes this.
- **Their treatment is binary and large-plant-restricted.** $W_i^F$ as a
  continuous arsinh dollar measure (Eq. 4) is a *different* treatment. The paper
  runs both, which is right, but $\beta_F$ and the $G_i$ coefficient are not
  interchangeable and should not be described as if they were.
- **`countyfips.dta` covers only 2,980 counties** (ledger trap 1) — a DD350
  subset. The 4% failure rate against DS1 is concentrated in Virginia independent
  cities. Do not use it as a validation universe.

---

### 13. Jaworski, "World War II and the Industrialization of the American South" (2017)

**Citation.** T. Jaworski, "World War II and the Industrialization of the
American South," *Journal of Economic History*, 77(4), 2017, 1048–1082.
`[jaworski2017]` Cited 2× in the body (§1, §4). Not in the appendix.

**Type.** Peer-reviewed article — regional economic history with a causal design.

**Key terms.**

- **Industrialization (as an outcome).** Measured as the rise in the
  manufacturing share of employment and in manufacturing capital, not as income
  growth per se. This maps directly onto $M_{it}$ in the paper's Eq. 5.
- **Regional convergence.** The mid-century closing of the South's income and
  industrial gap with the rest of the country. Jaworski's claim is that wartime
  mobilization was a causal contributor, not merely coincident with it.
- **Prewar industrial capacity as a placement determinant.** The mechanism the
  paper invokes in §4 when discussing why Eq. 10 is not by itself causal.

**Function — CONTEXT and a secondary IDENTIFICATION citation.**
In §1 it establishes that mobilization had regionally differentiated
developmental consequences — supporting the paper's premise that treating WWII as
a single national treatment is wrong. In §4 it is cited jointly with
Fishback–Cullen for the 1938 Industrial Mobilization Plan as a potential
predetermined predictor or instrument.

**Limits.**

- **Regional, not county-general.** His identification is about the South. The
  paper generalizes to all continental counties; whether the mechanism (a
  low-industrial-base region receiving disproportionate new capacity) transfers
  to, say, the industrial Midwest is an open question the paper does not address.
- **Under-used relative to its relevance.** With two citations, Jaworski is
  carrying an argument — the regional heterogeneity of investment effects — that
  the paper's four-quadrant typology in §5 depends on. The typology (high/low
  fatality × high/low investment) is essentially a claim about heterogeneous
  treatment effects, and Jaworski is the closest precedent for estimating them.
- **[unverified]** Whether Jaworski's instrument is the 1938 IMP specifically or
  a related prewar-capacity measure. The paper cites him for it; a reader should
  confirm the exact instrument before repeating the claim.

---

### 14. Jaworski & Yang, "Did War Mobilization Cause Aggregate and Regional Growth?" (2025)

**Citation.** T. Jaworski and D. Yang, "Did War Mobilization Cause Aggregate and
Regional Growth?" *Explorations in Economic History*, 97, 2025, 101685.
`[jaworskiyang2025]` Cited 1× in the body (§1 only).

**Type.** Peer-reviewed article — recent work on the aggregate-vs-regional
decomposition of mobilization effects.

**Key terms.**

- **Aggregate vs. regional growth.** Whether mobilization raised the national
  growth path, or merely *reallocated* activity across regions with little
  national effect. A pure reallocation would show large local coefficients and no
  aggregate gain. This is the general-equilibrium objection to every local-effects
  paper in this literature, the present one included.
- **Composition of mobilization spending.** The paper's §1 gloss: that *what* the
  money bought (ordnance vs. shipbuilding vs. aircraft vs. facilities) matters for
  long-run growth, not merely how much. This is a close cousin of the paper's own
  $W^C$/$W^F$ split.

**Function — CONTEXT.**
One sentence in §1, establishing that recent work emphasizes spending
composition. It supports the paper's decomposition move by showing the field is
moving the same way.

**Limits.**

- **Cited once and never returned to.** Given that the paper's core methodological
  claim is a composition claim, a source explicitly about composition should
  appear in §2 or §4, not only in the literature paragraph.
- **Raises an objection the paper does not answer.** If mobilization effects were
  largely reallocative, then $\mathcal{A}$'s interpretation shifts: divergence
  between the death map and the dollar map would describe a zero-sum
  redistribution rather than an unequal distribution of net gains. That is a
  genuinely different historical claim and the paper should engage it.
- **[unverified]** I have not read this article and am characterizing it from the
  paper's one-line description plus its title. Treat the summary above as
  provisional.

---

### 15. Brunet, "Stimulus on the Home Front" (2026)

**Citation.** G. Brunet, "Stimulus on the Home Front: The State-Level Effects of
WWII Spending," *Review of Economics and Statistics*, 108(3), 2026, 628–644.
`[brunet2026]` Cited 1× in the body (§1 only).

**Type.** Peer-reviewed article — macro-oriented, state-level.

**Key terms.**

- **Stimulus / local fiscal multiplier.** The ratio of the change in local output
  or employment to the change in government spending in that locality. A
  cross-regional multiplier is identified from differential spending across
  places and is a *relative* multiplier, not the closed-economy national one.
- **State-level effects.** The unit of analysis. State variation is what makes
  the multiplier literature's identification tractable; it also means the
  estimates are not county estimates.

**Function — CONTEXT.**
A single §1 citation supporting the sentence that recent work emphasizes
mobilization-spending composition.

**Limits.**

- **Almost certainly under-used, and possibly mis-assigned.** This is the Brunet
  article most likely to be the actual home of the contract reconstruction the
  paper attributes to `[brunetReplication2025]`. A state-level WWII spending
  paper is exactly the kind of work that would require rebuilding contract data
  from CPA originals. **Check whether this — not the war-bonds replication
  package — is the correct citation for the reconstruction claim in §2 and §5.**
- **Wrong unit for the paper's purposes.** State-level multipliers cannot
  validate county-level coefficients.
- Cited once, in a sentence it shares with Jaworski–Yang, which means neither
  article's specific contribution is actually stated.

---

## E. Civilian mobilization and household finance

---

### 16. Brunet, Hilt & Jaremski, "War Bonds and Household Saving in WWII" (2025)

**Citation.** G. Brunet, E. Hilt, and M. Jaremski, "War Bonds and Household
Saving in WWII," *Explorations in Economic History*, 97, 2025, 101692.
`[brunetetal2025]` Cited 1× in the body (§5, empirical premise four).

**Type.** Peer-reviewed article — financial and household economic history.

**Key terms.**

- **War bond.** Federal debt marketed to households during the war, principally
  the **Series E** savings bond, sold through payroll deduction plans, banks, and
  mass campaigns. Purchase was voluntary but socially and institutionally
  pressured — which is precisely why it belongs in a paper about the rhetoric of
  sacrifice.
- **Payroll savings plan.** The employer-administered automatic deduction that
  moved most Series E volume. It converted "sacrifice" from an act of will into a
  default.
- **Displacement / crowd-out.** Whether a dollar of bond purchase represents *new*
  saving or merely saving diverted from another vehicle. Their estimate: each
  \$100 in war-bond sales displaced roughly \$70 in bank-deposit inflows, so
  about 30% was new. Total personal saving rose about 7%.
- **Total personal saving.** Household saving across all vehicles, the quantity
  that determines whether the bond campaign changed behavior or only its
  location.

**Function — CONTEXT, with a quantitative edge (BENCHMARK-flavored).**
It is the paper's evidence that the rhetoric of civilian sacrifice had
*measurable behavioral* consequences, not merely symbolic ones (§5, premise
four). This matters for the argument in §6: the paper claims the language of
shared sacrifice "organized measurable household behavior," and this is the only
citation supporting that.

**Limits.**

- **It supplies no variable.** Bond sales are not in $\mathbf{Y}_{it}$, not in
  $W_i$, not in $X_i$. Premise four therefore sits slightly outside the paper's
  own empirical architecture — it is a supporting historical fact, not a premise
  the design must explain.
- **Their unit is not the county.** **[unverified]** I do not know whether their
  bond-sales data are county-level. If they are, this is a missed opportunity:
  county bond-purchase intensity would be a genuinely third dimension of
  wartime burden — civilian financial sacrifice — that could enter $\mathcal{A}$
  or the four-quadrant typology. If they are not, the paper should not imply a
  local claim.
- **A 30% new-saving rate cuts both ways.** It can be read as "bond campaigns
  worked" or as "bond campaigns mostly relabeled existing saving." The paper reads
  it the first way without acknowledging the second.

---

## F. County outcomes and spatial harmonization

Two sources, both invisible in the paper's argument and load-bearing in its
construction. Everything on the left-hand side of Eq. 10 comes from the first;
the ability to put 1920, 1930, 1940, 1950, 1960 and 1970 counties in the same
row comes from the second.

---

### 17. Haines & ICPSR, *Historical, Demographic, Economic, and Social Data* (ICPSR 2896)

**Citation.** M. R. Haines and Inter-university Consortium for Political and
Social Research, *Historical, Demographic, Economic, and Social Data: The United
States, 1790–2002*, ICPSR, 2010. `[haines2010]`
Cited 1× in the body (§3), 1× in the appendix.

**Type.** Government-derived research dataset — a curated county-level compilation
of decennial census aggregates and related series, the standard county panel in
American economic history.

**Key terms.**

- **County-level census aggregate.** Not microdata. Each row is a county-year
  with counts and rates, derived from published census volumes rather than from
  individual returns.
- **DS numbering.** ICPSR's dataset-within-study numbering. The 20 files on disk
  are the ones this paper needs: DS0024 (1920), DS0026–29 (1930 parts I–IV),
  DS0030 (1937 unemployment), DS0032–33 (1940 I–II), DS0035–36 (1950), DS0038–40
  (1960), DS0041 (1970), plus the County Data Books.
- **County Data Book.** A Census Bureau reference volume of county statistics
  published irregularly. On disk: DS0070 (1947), DS0071 (1949), DS0072 (1952),
  DS0074 (1962), DS0075 (1967), DS0076 (1972). **DS0070 (1947) contains the legacy
  war-supply-contract series** — the one Fishback–Cullen use and the one this
  paper demotes to a robustness check. So Haines is not only the outcome source;
  it is also the source of the comparison spending measure.
- **1937 unemployment (DS0030).** The Census of Partial Employment, Unemployment,
  and Occupations — a voluntary registration, not a full enumeration. Useful as a
  prewar labor-slack control but with known undercount.
- **ICPSR county code `0`.** The state aggregate row. It must be dropped or state
  totals enter the county panel as counties. `src/overlap_analysis.py` handles
  this; any new script must too.
- **Homeownership rate ($H$).** Owner-occupied units as a share of occupied
  housing units. Available from 1940 onward in the census housing schedules — 1940
  is the first census with a full housing census, which is why the paper's
  baseline is 1940 and not earlier for this outcome.

**Function — DATA, for the entire left-hand side and part of $X_i$.**
Supplies $\log P_{it}$, $M_{it}$ (manufacturing employment share), $w^M_{it}$
(manufacturing pay), $H_{it}$ (homeownership), $\log y_{it}$ (income) — the whole
outcome vector in Eq. 5 — at 1940, 1950, 1960, 1970; the 1920 and 1930 values for
the pretrend test in §4; the 1940 population that denominates Eqs. 1, 3, and 4;
and the legacy County Data Book contract series for robustness.

**Limits.**

- **Variable definitions are not stable across censuses.** "Manufacturing
  employment," industry classification, income concepts (family vs. household
  income; median vs. mean), and the occupational classification all changed
  between 1940 and 1970. A long difference across those years absorbs definitional
  change into the outcome. The paper's Eq. 5 lists $\log y_{it}$ as "household or
  family income" — the disjunction is doing real work and should be resolved.
- **County boundaries change.** Haines rows are on contemporaneous boundaries.
  Harmonization is entry 18's job, and it is not optional.
- **Published-table provenance.** Because these are aggregates from printed
  volumes, transcription and rounding errors are possible and are not
  systematically documented.
- **No county income before 1950.** Median family income is a 1950-onward census
  item. $\log y_{i,1940}$ as a baseline for a long difference in income does not
  exist in the same form. The paper's $\Delta Y_{i,1940\rightarrow t}$ notation
  implies a 1940 baseline for every element of $\mathbf{Y}$; for income that is
  not straightforwardly available. **This should be checked and the specification
  adjusted or explained.**
- **Ledger trap 5** applies: Garin–Rothbaum's `Census*.dta` are these same files
  renamed. Do not present agreement as corroboration.

---

### 18. Ferrara, Testa & Zhou, "New Area- and Population-based Geographic Crosswalks" (2024)

**Citation.** A. Ferrara, P. A. Testa, and L. Zhou, "New Area- and Population-based
Geographic Crosswalks for U.S. Counties and Congressional Districts, 1790–2020,"
*Historical Methods*, 57(2), 2024, 67–79. `[ferraracrosswalk2024]`
Cited 1× in the body (§3). Not in the appendix.

**Type.** Peer-reviewed methods article, with an associated data product (on disk
as ICPSR 150101-V4.1, `data/raw/crosswalks/ftz_1940/`).

**Key terms.**

- **Crosswalk.** A table mapping units in one geography to units in another, with
  weights, so that data collected on the first can be expressed on the second.
- **Area-weighted crosswalk.** Allocates a source county's value to target
  counties in proportion to *land area* overlap. Appropriate for land-based
  quantities; wrong for population-based ones, because it treats an empty square
  mile like a dense one.
- **Population-weighted crosswalk.** Allocates in proportion to *population*
  overlap. Appropriate for counts of people, deaths, employment, and income. The
  paper specifies population-weighted, correctly, since every quantity being
  harmonized is a population quantity.
- **Target-year geography.** The boundary vintage everything is projected onto.
  This paper uses **1940** as the target, which is the right choice: 1940 is the
  baseline year, the denominator year for Eqs. 1, 3 and 4, and the year the
  treatment is defined on.
- **GISJOIN.** The NHGIS-standard geographic identifier. Each crosswalk row
  carries `gisjoin_<year>` and `gisjoin_1940`. It is more robust than FIPS across
  historical vintages because it encodes the census-year geography explicitly.
- **`m1_weight` … `m6_weight`.** Six alternative population-weighting schemes
  shipped with the product. **Choosing among them is a researcher degree of
  freedom the paper has not yet disclosed.** Which weight is used, and whether
  results are robust to the alternatives, should appear in the paper.
- **Independent city.** A municipality that is not part of any county (Virginia
  has ~38 of them; also St. Louis, Baltimore, Carson City). They are a recurring
  failure mode in county harmonization and are the documented cause of the 4%
  failure rate against `countyfips.dta` (ledger trap 1). The paper's §3 sentence —
  "Independent cities and counties affected by boundary changes are harmonized
  rather than treated as time-invariant units" — is the right policy, and the
  paper should state which specific harmonization it applies (e.g. merging cities
  back into their surrounding counties).
- **Commuting zone (CZ).** A cluster of counties defined by commuting flows to
  approximate a local labor market, so that a job in one county held by a
  resident of the next is not treated as two separate economies. `cw_cty_czone.dta`
  is on disk. **The paper does not currently use commuting zones.** Given that war
  plants were frequently sited just outside cities, a county-level design will
  attribute plant employment to the plant's county and its workers' residences to
  neighbors — mechanically splitting one shock across units. A CZ-level robustness
  specification is the standard answer and is cheap to run.

**Function — DATA (infrastructure) / IDENTIFICATION (unit definition).**
Without this, the 1920–1970 panel behind Eq. 10 and the pretrend test cannot be
assembled at all. It also supplies county centroids
(`data/raw/crosswalks/ftz_centroids/`) for the Conley spatial-HAC standard errors
promised in §4.

**Limits.**

- **Crosswalk weights are themselves estimates.** Interpolating population across
  a boundary split introduces error that propagates into every harmonized
  variable. Because the same crosswalk is applied to both $D_i$ and $W_i$, some of
  that error is common and partially cancels in $\mathcal{A}$ — but not all of it,
  and not in the regression coefficients.
- **The choice among `m1`–`m6` is undisclosed.** See above.
- **Harmonization interacts with the residence-at-enlistment problem.** Putting
  1940-vintage deaths and 1970-vintage outcomes on the same polygon does not fix
  the fact that people moved between them.
- **The paper cites the article, not the data deposit.** The ledger records the
  product as ICPSR 150101-V4.1. Best practice is to cite both. Easy fix.

---

## G. Rhetoric, propaganda, and the political history of sacrifice

Six sources. They carry §6 entirely and frame §1 and the conclusion. None of them
enters an equation, and the paper is explicit that they are not meant to. Their
job is to establish that "equality of sacrifice" was a *specific historical
claim*, made by identifiable actors for identifiable purposes — which is what
makes the quantitative disaggregation a test of something rather than a
description of nothing.

---

### 19. Roosevelt, "Fireside Chat: On Sacrifice," 28 April 1942

**Citation.** F. D. Roosevelt, "Fireside Chat: On Sacrifice," April 28, 1942.
`[roosevelt1942]` Cited 2× in the body (§1, §6), 1× in the appendix.

**Type.** Primary rhetorical document — a presidential radio address, the paper's
central textual object.

**Key terms.**

- **Fireside chat.** Roosevelt's series of direct radio addresses to the American
  public (roughly 30 between 1933 and 1944). The genre matters: informal,
  explanatory, addressed to households rather than to Congress, and designed to
  build consent for policy rather than to announce it.
- **"Equality of sacrifice."** The address's organizing phrase, and the paper's
  title concept. Its rhetorical function is to make categorically different
  burdens — a tax payment, a rationed tire, a factory shift, a son's death —
  members of one moral class.
- **The seven-point economic stabilization program.** The policy content the
  address explains: heavier taxation, a ceiling on personal incomes, price
  control, wage stabilization, farm-price control, war-bond purchase, rationing,
  and discouraging installment credit. The address is thus not primarily about
  military service; it is an *economic* speech that recruits military sacrifice as
  the moral warrant for civilian economic controls. That inversion is the paper's
  best evidence for its "political compression" argument.
- **Emergency Price Control Act (1942) / General Maximum Price Regulation.** The
  legal machinery behind the price-control plank; the "General Max" of April 1942
  froze most retail prices at March levels.
- **Little Steel formula.** The July 1942 War Labor Board wage-stabilization rule
  capping wage increases at 15% over January 1941 levels. The wage-restraint plank
  in practice.
- **Rationing.** Administrative allocation of scarce consumer goods by coupon
  rather than by price — gasoline, sugar, coffee, meat, tires, shoes.

**Function — CONTEXT (primary object of the rhetorical analysis).**
It supplies the claim the paper tests the geography of. §1 uses it to introduce
the moral grammar; §6 reads it closely as the operation that "converted
heterogeneous burdens into commensurable citizenship." It is the reason the
paper's core statistic is *correspondence* rather than *compensation*.

**Limits.**

- **The bibliographic entry is incomplete for a primary source.** No archive, no
  edition, no URL, no collection. A speech cited as evidence should be citable to
  a text: the Public Papers and Addresses of Franklin D. Roosevelt, the FDR
  Presidential Library's Master Speech File, or the American Presidency Project.
  **This is the weakest citation in the bibliography as a matter of form**, and it
  is the one a historian referee will notice first.
- **One speech is one speech.** §6 makes a claim about a wartime *discourse*.
  Establishing a discourse requires more than a single address, which is
  presumably why Winkler and Sparrow are cited alongside — but the paper never
  states that the fireside chat is a synecdoche for a broader corpus. It should,
  or it should widen the corpus.
- **Rhetoric ≠ reception.** That Roosevelt said sacrifice was shared does not
  establish that Americans believed it, and the paper does not claim otherwise.
  But §6's argument that the rhetoric's "political efficacy may have depended on
  suppressing geographic differentiation" is a claim about *effect*, and no
  reception evidence (polling, letters, OWI surveys of civilian morale) is cited
  for it. Cantril's wartime public-opinion series would be the obvious source.

---

### 20. Winkler, *The Politics of Propaganda* (1978)

**Citation.** A. M. Winkler, *The Politics of Propaganda: The Office of War
Information, 1942–1945*, Yale University Press, 1978. `[winkler1978]`
Cited 2× in the body (§1, §6). Not in the appendix.

**Type.** Peer-reviewed scholarly monograph — the standard institutional history
of the OWI.

**Key terms.**

- **Office of War Information (OWI).** The federal agency created by executive
  order in June 1942 to coordinate wartime information and propaganda, absorbing
  several predecessor offices. It produced and coordinated posters, films, radio
  content, and press guidance.
- **Domestic Branch vs. Overseas Branch.** OWI's two halves, with different
  missions and different fates. The Domestic Branch — the one that mattered for
  American civilians and therefore for this paper — was attacked by Congress as
  New Deal propaganda and had its appropriation gutted in 1943. The Overseas
  Branch survived. Any claim about "OWI messaging to Americans" is a claim about
  an agency that was politically contested and, after mid-1943, badly weakened.
- **"Strategy of truth."** OWI's self-description: the claim that American
  propaganda would work by accurate information rather than fabrication. Winkler's
  book is substantially about the gap between that self-image and the agency's
  practice and politics.
- **Propaganda (as a scholarly term).** Coordinated persuasive communication in
  service of state objectives. Not necessarily false. The paper uses OWI material
  as evidence of an official *framing*, which is the appropriate use.

**Function — CONTEXT.**
Supports the claim in §1 and §6 that the fireside chat's moral grammar was not
idiosyncratic to Roosevelt but was "elaborated visually" and institutionally by
federal agencies. It converts one speech into a program.

**Limits.**

- **Institutional history, not content analysis.** Winkler explains what OWI was
  and how it fought its political battles. He is not a source for a systematic
  reading of what posters said. The paper's claim in §1 that OWI "elaborated the
  same moral grammar visually, teaching civilians to imagine consumption
  restraint, war work, and bond buying as extensions of battlefield service" is a
  content claim, and it is currently supported by an institutional history plus a
  synthetic monograph (Sparrow). If the paper wants a content claim it needs the
  posters themselves — which are cited in the appendix (entries 23, 24) but *not*
  in the body.
- **1978 scholarship.** Excellent and still standard, but forty-eight years of
  subsequent work on wartime visual culture, gender, and race in propaganda is
  not represented. See §S3.
- **OWI is not the whole propaganda state.** The War Advertising Council, the
  Treasury's War Finance Division (which ran the bond drives), and the armed
  services all produced their own campaigns. For a paper whose fourth empirical
  premise is about *bond sales*, the Treasury's campaign apparatus is the more
  directly relevant agency and it is uncited.

---

### 21. Sparrow, *Warfare State* (2011)

**Citation.** J. T. Sparrow, *Warfare State: World War II Americans and the Age of
Big Government*, Oxford University Press, 2011. `[sparrow2011]`
Cited 2× in the body (§1, §6), 1× in the appendix (with an annotation).

**Type.** Peer-reviewed scholarly monograph — the paper's principal interpretive
framework for the politics of wartime obligation.

**Key terms.**

- **Warfare state.** Sparrow's organizing concept: the wartime expansion of
  federal capacity and reach, and the forms of citizenship it produced. Set
  against "welfare state" as the more familiar account of mid-century state
  growth.
- **Obligation (as a mode of citizenship).** The book's central claim is that the
  wartime state secured mass compliance less through coercion than by
  reconstructing citizenship around duty — making taxation, saving, rationing, and
  labor into civic acts. This is exactly the "moral economy of national
  obligation" the paper invokes in §6.
- **Fiscal citizenship / mass taxation.** WWII converted the federal income tax
  from a levy on the affluent into a mass tax: the number of filers rose roughly
  from 4 million to over 40 million. The **Victory Tax** (1942) and **payroll
  withholding** (Current Tax Payment Act, 1943) made it routine and invisible.
  This is the concrete institutional content of "shared sacrifice" for most
  households.
- **Political compression (the paper's term, not Sparrow's).** The paper's coinage
  for the operation Sparrow describes: heterogeneous material burdens rendered as
  one commensurable civic obligation.

**Function — CONTEXT (framework).**
Supplies the interpretive apparatus for §6 and, per the appendix annotation, "the
historical framework for the paper's interpretation of 'shared sacrifice' as a
political compression of heterogeneous local burdens." It is what allows the paper
to treat wartime rhetoric as a *political technology* rather than as decoration.

**Limits.**

- **Sparrow's account is national and social; the paper's is spatial.** Sparrow
  explains how obligation was constructed across classes, races, and roles. He
  does not argue that the rhetoric suppressed *geographic* differentiation
  specifically. The paper's §6 claim — that the rhetoric's efficacy "may have
  depended on suppressing geographic differentiation" — is the paper's own
  extension of Sparrow, and it is currently phrased as though it were his. The
  hedge "may have" is doing a lot of work. Either mark the extension as the
  paper's own contribution, or supply evidence.
- **Interpretive, not falsifiable by the paper's data.** Nothing in Eq. 7 or
  Eq. 10 can confirm or refute Sparrow. The paper is careful about this, and §6 is
  correctly framed as a reading rather than a test. Keep it that way.

---

### 22. American Historical Association, *GI Roundtable 13* (1945)

**Citation.** American Historical Association, "What Principles Should Govern the
Final Settlement?" *GI Roundtable 13: How Shall Lend-Lease Accounts Be Settled?*,
1945. `[aha1945]` Cited 1× in the body (§6).

**Type.** Primary document — a wartime civic-education pamphlet, produced by a
scholarly society for the armed forces. Not a research article; a contemporaneous
artifact of official discourse.

**Key terms.**

- **GI Roundtable.** A series of discussion pamphlets (issued as **EM**, Education
  Manual, numbers) written by the American Historical Association under contract
  to the War Department's Armed Forces Institute, designed to structure organized
  discussion among service personnel on postwar questions. Their genre is
  deliberate even-handedness: they pose questions and present sides.
- **Lend-Lease.** The 1941 program under which the United States supplied
  materiel to Allied nations without immediate payment, with settlement deferred
  to the postwar period. Pamphlet 13 concerns how those accounts should be
  settled.
- **"No dollar-and-cents price can be set on lives and limbs."** The quoted
  sentence the paper builds on. In its original context it is an argument about
  *international* settlement — that Allied nations' human losses cannot be netted
  against American material aid. The paper repurposes it as a statement about
  commensurability in general.
- **Commensurability.** Whether two quantities can be expressed in a common
  metric. The paper's whole methodological ethic — measuring *correspondence*
  between distributions rather than a dollars-per-death *ratio* — is a
  commensurability position, and this pamphlet is its warrant.

**Function — CONTEXT, and an unusually direct methodological warrant.**
This is the source that, per the paper's own §Research and Drafting Reflection,
"clarified the proper object of the project: not compensation, but
correspondence." It is doing more work than a single citation in §6 suggests: it
is the historical justification for choosing $\mathcal{A}$ (Eq. 7) over a ratio.
That should be stated where $\mathcal{A}$ is introduced, in §4, not only in §6 and
the appendix.

**Limits.**

- **Context transfer.** The quoted principle was articulated about international
  Lend-Lease settlement between *nations*, not about domestic distribution across
  *counties*. Using it as a general principle is defensible and rhetorically
  effective, but the transfer should be acknowledged in a clause. A historian
  referee will spot it.
- **A pamphlet is evidence of what was sayable, not of consensus.** The GI
  Roundtable genre presents multiple positions by design. Quoting one line as
  "the historical vocabulary itself" (§6) slightly overstates what a single
  discussion pamphlet establishes.
- **Attribution.** GI Roundtable pamphlets had individual authors working under
  AHA auspices. Citing the AHA corporately is acceptable but the individual author
  should be identified if determinable. **[unverified]** I cannot confirm the
  author of EM 13 from the materials on disk.

---

### 23. NARA, *World War II Posters, 1942–1945* (Series 44-PA)

**Citation.** National Archives and Records Administration, *World War II Posters,
1942–1945 (Series 44-PA)*, 2026. `[naraPosters]`
Cited **0× in the body**, 1× in the appendix (Primary Objects and Archival
Materials).

**Type.** Archival record series — a visual-materials series held by NARA.

**Key terms.**

- **Series 44-PA.** NARA's identifier. The prefix **44** is the record group
  number for the **Office of Government Reports / Office of War Information**;
  **PA** designates the posters series within it. So this series is, by
  provenance, the OWI's own poster output — the material object behind the
  Winkler citation.
- **Record group / series / item.** NARA's descriptive hierarchy: record group
  (creating agency) → series (a body of records maintained as a unit) → file unit
  → item. Citing at the series level, as here, is appropriate when the argument is
  about the corpus rather than a specific poster; it becomes inadequate the moment
  a specific image is discussed.
- **Poster (as a propaganda form).** Mass-produced visual persuasion for public
  display in workplaces, transit, and shops. Its rhetorical mode is compressed
  and iconographic, which is precisely why it is good evidence for the paper's
  "moral grammar" claim: a poster must make the equivalence between war work and
  battlefield service in a single image.

**Function — CONTEXT (prospective).**
Listed in the appendix as a principal object of study for the rhetorical
component. **It does not currently support any claim in the article.**

**Limits.**

- **The body makes a visual-content claim (§1: OWI "elaborated the same moral
  grammar visually") and cites Winkler and Sparrow for it — not the posters.**
  The one archival series that could directly evidence that claim is confined to
  the appendix. This is the clearest structural mismatch in the citation set:
  the evidence exists, is identified, and is not deployed. Moving 44-PA into §6
  with two or three specific, described posters would convert an asserted claim
  into a demonstrated one.
- **No item-level citations.** A rhetorical analysis of posters requires naming
  posters. Series-level citation cannot support a reading.
- **The 2026 date is a retrieval date, not a publication date**, and should be
  formatted as such (e.g. "accessed 2026").
- **Selection.** With thousands of items, any small set discussed is a
  researcher-chosen sample. The paper would need to say how items were selected.

---

### 24. NMAH, *Princeton University Poster Collection* (NMAH.AC.0433)

**Citation.** National Museum of American History, *Princeton University Poster
Collection, NMAH.AC.0433*, Smithsonian Institution, 2026. `[smithsonianPosters]`
Cited **0× in the body**, 2× in the appendix (Primary Objects; Physical Research
Space).

**Type.** Archival collection — a named manuscript/visual collection with a
finding aid, held at the Archives Center, National Museum of American History,
1300 Constitution Avenue NW, Washington, DC.

**Key terms.**

- **NMAH.AC.0433.** The collection's control number. `AC` designates an Archives
  Center collection; the number is its accession identifier. Citing it makes the
  collection findable in Smithsonian's catalog.
- **Archives Center (NMAH).** The manuscript and archival unit within the museum,
  distinct from the museum's object collections and distinct from the Smithsonian
  Institution Archives. Researcher access is by appointment.
- **Finding aid.** The descriptive inventory of a collection — its provenance,
  scope, arrangement, and box/folder list. It is what a researcher reads before
  visiting, and it is the right thing to cite when describing collection scope.
  Available through SOVA (Smithsonian Online Virtual Archive), which is the
  `sova-nmah-ac-0433` string in the paper's appendix URL.
- **Provenance (archival sense).** The origin and custodial history of a
  collection. Here: material assembled at Princeton and transferred to the
  Smithsonian — which is why it contains both WWI and WWII material, and why its
  composition reflects a collector's choices rather than an agency's output. This
  is a meaningful difference from NARA 44-PA, which is agency-generated.

**Function — CONTEXT (prospective); institutional plan.**
It satisfies the course prospectus's "physical research space" requirement and
identifies where the rhetorical component's primary work would be done. Like
entry 23, it supports nothing in the article proper.

**Limits.**

- **Collector-assembled, not agency-generated.** For an argument about *federal*
  messaging, an agency series (44-PA) has better provenance. The Princeton
  collection's value is breadth and physical access, not representativeness.
- **Mixes WWI and WWII.** The appendix says so. Any sampling from it must
  separate the wars.
- **Not cited in the body.** Same structural point as entry 23.
- **The 2026 date is a retrieval date.**

---

# Part II — Synthesis

## S1. How the sources compose

The bibliography is not a flat list of twenty-four references. It is four
distinct evidentiary layers that meet at exactly one point — the county — and the
paper's contribution is the joint.

### Layer 1: the casualty side

Four archival/statistical sources define the universe of wartime death
(`ferrara2024data`, `naraArmy1946`, `naraNavy1946`, `va2025`), and three
economics articles establish what death does to a local economy
(`acemoglu2004`, `brodeur2022`, `ferrara2022`).

The internal logic runs: VA supplies national totals; the two NARA series supply
*definitions* that conflict; the ICPSR deposit supplies rows; the three articles
supply mechanisms. The conflict between the Army and Navy universes is not a
nuisance the paper works around — it is the reason the paper has an inferential
sample rather than a convenience sample. That single act of source criticism
(§2, and again in the appendix's drafting reflection) is what distinguishes this
casualty measure from a naive one.

What this layer proves: casualties varied enormously across counties, and that
variation predicted fertility, female employment, and Black occupational
composition. What it does not prove: anything about money.

### Layer 2: the investment side

Two CPA record series define what federal war investment *was*
(`cpaContracts1946`, `cpaFacilities1946`); one replication package supplies a
modern reconstruction (`brunetReplication2025`, provenance disputed — see §S4);
and five articles establish what investment did (`fishback2013`, `garin2025`,
`jaworski2017`, `jaworskiyang2025`, `brunet2026`).

The internal logic runs: contracts and facilities are different objects in the
archive, and the literature confirms they behave differently in the data.
Fishback–Cullen find that aggregate spending moved population but not per-capita
outcomes; Garin–Rothbaum find that *public plants* moved manufacturing,
population, income, and even incumbent earnings four decades later. The gap
between those two results is the empirical warrant for the paper's $W^C$/$W^F$
decomposition. Neither paper made that decomposition the object; this paper does.

What this layer proves: war investment was spatially lumpy and its persistence
depended on its form. What it does not prove: anything about who died.

### Layer 3: the harmonization layer

Two sources (`haines2010`, `ferraracrosswalk2024`), plus — crucially and
invisibly — the Garin–Rothbaum replication package cited under `garin2025`.

This layer is what actually permits the joint. Layer 1 arrives keyed on ICPSR
state codes and NARA enlistment codes. Layer 2 arrives keyed on city names with
no county at all. Layer 3 puts them both on 1940 county polygons alongside the
outcome vector. The city→county crosswalk (`cw-city-county.dta`) and the
population-weighted 1940-target crosswalks are the least visible and most
load-bearing items in the whole apparatus: **without them the paper's question
cannot be asked, only posed.**

Note the structural oddity worth stating in the paper: the harmonization layer
is dominated by a single author (Ferrara supplies the casualty microdata *and*
the crosswalks) and a single replication package (Garin–Rothbaum supplies the
city crosswalk, the controls, the adjacency, the plant data, and the County Data
Books). Independence between the paper's inputs is lower than a reader of the
bibliography would assume.

### Layer 4: the rhetorical layer

Six sources (`roosevelt1942`, `winkler1978`, `sparrow2011`, `aha1945`,
`naraPosters`, `smithsonianPosters`), of which two are appendix-only.

This layer answers a question the other three cannot: *why does the geographic
divergence matter?* Without it, $\mathcal{A}=0.455$ is a descriptive fact about
two distributions. With it, $\mathcal{A}$ becomes a measurement of the distance
between a national political claim and its material substrate. The AHA pamphlet
is doing quiet but essential work here: it supplies a *contemporaneous* refusal to
price lives, which is what licenses the paper's choice of an overlap statistic
over a dollars-per-death ratio. The methodological ethic is sourced to 1945, not
imposed from 2026.

### Where the two literatures had not been joined

The casualty literature (Acemoglu–Autor–Lyle, Brodeur–Kattan, Ferrara) treats
mobilization as a *labor supply* shock and asks what removing men did to the
people who stayed. The investment literature (Fishback–Cullen, Jaworski, Garin–
Rothbaum, Brunet, Jaworski–Yang) treats mobilization as a *capital* shock and asks
what building plants did to the places that got them. Both are county-level. Both
use overlapping data infrastructure — indeed Garin–Rothbaum's package literally
contains a county casualty file, which means the two shocks have sat in the same
directory without being crossed.

**The gap this paper occupies is precisely that crossing.** Not "did WWII help
the economy," which both literatures answer in their own terms, but: *were the
counties that supplied the dead the same counties that received the capital?* No
cited work computes a joint distributional statistic over the two exposures. No
cited work estimates $\theta_C$ or $\theta_F$ — the interaction of fatal exposure
with investment. That is the paper's whole claim to originality, and the
bibliography supports it in the strong sense: every input exists, and nobody
listed has combined them.

Two caveats on the novelty claim. First, the *casualty-inequality* question has a
literature the paper does not cite (Kriner and Shen's *The Casualty Gap*, 2010,
is the direct antecedent — see §S3). Second, the ledger's per-capita Spearman
correlation of **−0.034** is a far stronger statement of the finding than the
paper's current qualitative framing, and it is not yet in the paper at all.

---

## S2. Dependency map

For each core quantity: the sources it depends on, and what breaks if a source is
wrong. "Breaks" means the failure propagates into a reported number, not merely
into a robustness check.

| Quantity | Depends on | What breaks if the source is wrong |
|---|---|---|
| **$D_i^A$** — Army/AAF deaths | `ferrara2024data` (DS1); `naraArmy1946` (universe definition); `garin2025` (`crosswalk_statefip_stateicp_1910.dta` for STATEICP→FIPS); `ferraracrosswalk2024` (1940 harmonization) | **Everything.** $D_i^A$ is the numerator of Eqs. 1 and 2, the $p_i^D$ in Eq. 6, and hence $\mathcal{A}$, JS, and both Spearman correlations. If the STATEICP crosswalk mis-maps a state, an entire state's deaths land in the wrong FIPS block and $\mathcal{A}$ is silently wrong. If the honor list's universe is narrower than believed, $B_i^{\mathrm{civic}}$ is a battle-death rate mislabelled as an all-cause rate. |
| **$E_i^A$** — Army/AAF enlistment | `ferrara2024data` (DS2); an unbuilt NARA→FIPS crosswalk; `garin2025` (`WWII_draft_volunteer_casualties_Army_AirForce.dta`, validation) | Eq. 2 — the paper's **preferred inferential burden measure** — cannot be computed at all. Currently open (ledger §4.2): 11,410 code cells against ~3,100 counties. If the eventual crosswalk is wrong, $B_i^A$ is wrong and $\beta_B$, $\theta_C$, $\theta_F$ in Eq. 10 are all contaminated. Because the denominator sits under every interaction term, an $E_i^A$ error is more damaging than a $D_i^A$ error of the same size. |
| **$W_i^C$** — contract investment | `cpaContracts1946` (universe); `brunetReplication2025` (reconstruction — **provenance disputed**); `garin2025` (`cw-city-county.dta`); `haines2010` (1940 population denominator, DS0032); `fishback2013` (validation benchmark) | $\mathcal{A}$, JS, both Spearman figures, Eq. 3, $\beta_C$ and $\theta_C$. Two independent failure modes: (a) the prime-contract-only universe means $W_i^C$ measures awards, not production — a *systematic* understatement of dispersion; (b) the 2.0% unmatched dollars concentrate in industrial metros, so concentration measures are understated. The Fishback–Cullen ≈40% top-20 benchmark against the computed 43.8% is currently the **only** external check on the whole city→county pipeline. If that benchmark is itself artifactual, the pipeline is unvalidated. |
| **$W_i^F$** — facility investment | `cpaFacilities1946` (via `FacilitiesDatabase.xls`); `garin2025`; `haines2010` (denominator); `ferraracrosswalk2024` | Eq. 4, $\beta_F$, $\theta_F$. **Not yet built.** The $W^C$/$W^F$ decomposition is the paper's stated central methodological contribution and its second half does not exist yet. Authorized-vs-realized cost error propagates directly into $\beta_F$. |
| **$G_i$** — public-plant treatment | `cpaFacilities1946`; `garin2025` (design, size and ownership criteria, matched comparisons) | The paper's strongest quasi-experimental arm. **Not yet built.** If the public/private ownership split is mis-coded — mixing certificate-of-necessity private plants into $G_i$ — the treatment is no longer "public capital" and the security-siting exclusion argument evaporates with it. If the criteria diverge from Garin–Rothbaum's, the paper cannot claim to parallel them. |
| **$B_i^{\mathrm{civic}}$** — community burden (Eq. 1) | $D_i^A$ chain; `haines2010` DS0032 (1940 population); `ferraracrosswalk2024` | Every descriptive map and the computed per-capita Spearman of −0.034. Denominator-driven: an error in 1940 county population produces spurious burden variation. Also carries the definitional risk that $D_i$ in Eq. 1 is written unsubscripted while the computed value uses Army/AAF only — the paper should make that explicit. |
| **$B_i^A$** — exposure-conditioned burden (Eq. 2) | $D_i^A$ chain **and** $E_i^A$ chain (both) | The inferential core. It is the only quantity that depends on *both* military chains, so it inherits both failure modes. Currently uncomputable. A secondary specification using 1940 military-age men as denominator (`haines2010` DS0032/0033) is a fallback but reintroduces exactly the age–sex composition problem Eq. 2 exists to remove. |
| **$\mathcal{A}$** — overlap coefficient (Eq. 7) | $D_i^A$ chain × $W_i^C$ chain; `haines2010` (county universe, 3,104 counties); `ferraracrosswalk2024`; `aha1945` (conceptual warrant); `fishback2013` (concentration benchmark) | The headline descriptive result. $\mathcal{A}$ is a *difference of distributions*, so it is sensitive to any error that shifts mass between counties but insensitive to errors that scale both distributions. That makes it robust to level errors and fragile to geocoding errors. The 2.0% unmatched contract dollars are exactly a geocoding error, so the ledger's instruction to "re-check $\mathcal{A}$ after resolving the residual" is not optional housekeeping — it is a stability test on the paper's headline number. |
| **$\mathbf{Y}_{it}$** — outcome vector (Eq. 5) | `haines2010` (DS0032–33, 0035–36, 0038–41); `ferraracrosswalk2024` (1940-target harmonization); `garin2025` and `fishback2013`/`brodeur2022`/`ferrara2022` (which outcomes to include, and benchmark magnitudes) | The entire left side of Eq. 10. Failure modes are definitional rather than technical: census concepts for manufacturing employment, income, and occupation shift between 1940 and 1970, and county median family income does not exist on the same basis in 1940. If harmonization weights (`m1`–`m6`, undisclosed) are wrong, every long difference absorbs boundary noise. |
| **$X_i$** — prewar controls | `garin2025` (`fishbackhorracekantor.dta`, 3,067 counties × 130 vars, plus LAT/LON); `haines2010` (DS0024, DS0026–29, DS0030) | Eq. 9's residualization (and hence the imbalance index $I_i$ and every conditional map) and Eq. 10's $\gamma$. Also the Conley spatial-HAC errors, via the coordinates. Note ledger trap 5: G&R's `Census*.dta` are Haines files renamed, so the two "independent" control sources are partly the same bytes. A failure in the FHK control set propagates to *both* the descriptive typology and the regression. |
| **Standard errors** | `garin2025` (coordinates, `NBER_county_adjacency2010.dta`); no methodological citation | §4 promises state clustering "checked against spatial-HAC inference." Conley (1999) and the modern clustering literature are **uncited**. If the spatial weights or the bandwidth are wrong, every reported inference is wrong and no source in the bibliography constrains the choice. |

**Reading the map.** Three observations fall out of it.

1. **`garin2025` is a single point of failure with unusual reach.** It touches
   $D_i^A$ (state crosswalk), $W_i^C$ (city crosswalk), $W_i^F$, $G_i$, $X_i$,
   the spatial errors, and the County Data Book robustness measure. Seven of
   eleven rows. That should be disclosed in the paper's data section, and the
   independent checks the package itself provides (the 3,073-county casualty file)
   should actually be run.
2. **The two quantities the paper calls "preferred" are the two not yet built.**
   $B_i^A$ (preferred over $B_i^{\mathrm{civic}}$) and $W_i^F$/$G_i$ (the point of
   the decomposition). The paper currently describes them in the present tense.
3. **$\mathcal{A}$ is robust to the errors the paper worries about and fragile to
   the one it does not emphasize.** It survives level and universe errors that
   scale distributions; it does not survive misallocation across counties. Prime-
   only contract measurement and unmatched metro dollars are both misallocation.

---

## S3. Where the citation set is thin

Six gaps, ordered by how much damage they do. Each names specific literature.

### 1. Selective Service and the administration of the draft — entirely absent

**The problem.** Eq. 2 conditions deaths on enlistment records, and §4 proposes
using "individual enlistment characteristics ... to construct predicted fatality
risk." Both moves treat $E_i^A$ as a measure of *exposure to service*. But
enlistment was the output of an administrative screening process that varied
enormously across counties: **local draft boards** exercised wide discretion,
**occupational and agricultural deferments** removed men from war-industry
counties precisely where $W_i^C$ was high, **dependency deferments** varied with
local family structure, and **physical and mental rejection rates (4-F)** varied
by region — dramatically so, with Southern rejection rates far above the national
average because of nutrition, hookworm, dental condition, and education. Every one
of those is correlated with prewar county characteristics *and* with the paper's
treatment variables. $E_i^A$ is not a neutral denominator; it is an outcome.

There is not a single citation to this institutional apparatus in the paper.

**What to add.** On the institution: the Selective Service System's own annual
reports and *Selective Service in Wartime*; George Q. Flynn, *The Draft,
1940–1973* (1993) and *Lewis B. Hershey, Mr. Selective Service* (1985), the
standard administrative histories of local-board discretion. On rejection rates
and regional health: the Army's own physical-standards reports and the public-
health literature on WWII rejection geography. On the econometrics of
draft-induced selection: Angrist (1990, *AER*) on the Vietnam lottery as the
method template for separating draft assignment from selection, and Angrist &
Krueger (1994, *JOLE*) on WWII veteran-status selection specifically — the latter
is directly on point and directly uncited. On mobilization rates as spatial
variation, the paper already cites `acemoglu2004`, but only in §1; it should be
promoted into §4 where the exposure argument is actually made.

**Why it ranks first.** It is the identification hole under the paper's own
preferred measure.

### 2. The casualty-inequality literature — a direct antecedent, uncited

**The problem.** The paper claims in §1 that the two literatures "have largely
treated wartime capital and wartime death as separate local shocks," and frames
its contribution as joining them. That is fair. But there exists a body of work
whose entire subject is the *unequal geographic and socioeconomic distribution of
American war deaths* — which is half of this paper's question — and none of it
appears.

**What to add.** Douglas Kriner and Francis Shen, *The Casualty Gap: The Causes
and Consequences of American Wartime Inequalities* (Oxford, 2010) is the closest
antecedent: it documents, across WWII, Korea, Vietnam, and Iraq, that casualties
fell disproportionately on poorer communities, and it connects that inequality to
political consequences. Their community-level casualty measures are conceptually
$B_i^{\mathrm{civic}}$. Not engaging them is a novelty-claim risk: a referee who
knows the book will ask what this paper adds, and the answer ("we cross it with
the investment geography and compute a joint distributional statistic") is a good
answer that the paper currently cannot give because it does not raise the
question. Also relevant: the sociological life-course work on WWII cohorts —
Glen Elder's *Children of the Great Depression* and the Elder/Clipp studies of
military service across the life course; and, for a longer-run methodological
analogue, Costa and Kahn's work on Civil War soldiers and community effects.

**Why it ranks second.** It bears directly on the paper's claim to originality.

### 3. The GI Bill and postwar housing/education — the missing mediator

**The problem.** $\mathbf{Y}_{it}$ includes homeownership $H_{it}$ and income
$\log y_{it}$, measured to 1970, and the paper attributes divergence to wartime
exposures. But between the war and 1970 stands the **Servicemen's Readjustment
Act of 1944 (the GI Bill)** — education benefits, VA-guaranteed mortgages,
unemployment allowances — which is the single largest institutional channel
connecting military service to postwar homeownership, education, and income, and
which was allocated *to veterans*, i.e. in proportion to a county's service
population. It is the most obvious mediator between the paper's treatment and two
of its five primary outcomes, and it is cited zero times.

Worse for identification: GI Bill benefits were administered in ways that varied
sharply by race and region (VA and FHA underwriting practices, and the discretion
of local administrators and lenders). The paper has a **Black semiskilled
employment** secondary outcome. Racially differential benefit administration is
a live confounder for it.

**What to add.** John Bound and Sarah Turner (2002, *Journal of Labor Economics*)
on the GI Bill and educational attainment; Marcus Stanley (2003, *QJE*) on the
returns to the WWII and Korean bills; Daniel Fetter (2013, *AEJ: Economic Policy*)
on VA and FHA mortgage programs and the postwar homeownership boom — Fetter is
the direct citation for $H_{it}$; Turner and Bound (2003, *Journal of Economic
History*) on race and the GI Bill. For the institutional/racial administration:
Ira Katznelson, *When Affirmative Action Was White* (2005); Richard Rothstein,
*The Color of Law* (2017); Suzanne Mettler, *Soldiers to Citizens* (2005).

**And its companion confounder: Cold War procurement.** The 1950–1970 outcome
window contains the Korean War and the Cold War defense buildup, which continued
to place contracts and facilities — substantially in the *same* places, because
industrial capacity persists. Attributing 1970 divergence to WWII exposures
requires ruling out continued federal spending along the same geography. Add:
Ann Markusen, Peter Hall, Scott Campbell and Sabina Deitrick, *The Rise of the
Gunbelt* (1991); Gregory Hooks, *Forging the Military-Industrial Complex* (1991);
Roger Lotchin, *Fortress California* (1992). A control for postwar defense
spending, or at minimum a discussion, belongs in §4.

**Why it ranks third.** It is two large uncited forces operating inside the
paper's own outcome window.

### 4. Econometric method — the paper's estimators have no citations at all

Every methodological choice in §3 and §4 is currently unsourced.

- **Inverse hyperbolic sine.** The paper uses arsinh in Eqs. 3 and 4 and justifies
  it in one clause ("preserves true zeros while limiting the leverage of extreme
  spending values"). There is now a substantial literature arguing that arsinh
  coefficients are *not* interpretable as elasticities and are sensitive to units
  when zeros are present: Bellemare and Wichman (2020, *Oxford Bulletin*), Chen
  and Roth (2024, *QJE*) on the arbitrariness of extensive-margin scaling, and
  Mullahy and Norton (2024) on alternatives. A referee in applied micro will raise
  Chen and Roth. Cite it and defend the choice, or use a Poisson/PPML
  specification for the dollar outcomes.
- **The overlap coefficient itself.** $\mathcal{A} = 1 - \tfrac12\sum_i|p_i^D -
  p_i^W|$ is **exactly one minus the index of dissimilarity**, the standard
  segregation statistic. The paper presents it as a novel construction. It should
  instead claim the (stronger) position that a well-understood distributional
  statistic is being applied to a new pair of distributions, and cite the lineage:
  Duncan and Duncan (1955) for dissimilarity; Weitzman (1970) and Inman and
  Bradley (1989) for the overlap coefficient; Reardon and Firebaugh (2002) for
  multigroup segregation measures; Lin (1991) for Jensen–Shannon divergence. This
  also imports known properties — the dissimilarity index's sensitivity to unit
  size and its behavior under aggregation — that the paper needs anyway.
- **Difference-in-differences and pretrends.** §4 promises a dynamic extension
  with 1920 and 1930 outcomes to test differential pretrends. Nothing is cited.
  Even in a long-difference design, Roth (2022) on pretest power and
  Rambachan and Roth (2023) on honest inference under trend violations are the
  expected citations.
- **Spatial and clustered inference.** Conley (1999) for spatial HAC; Bester,
  Conley and Hansen or Cameron–Miller for state clustering with 48 clusters —
  which is few enough that the paper should say something about it.
- **Continuous treatment with interactions.** $\theta_C$ and $\theta_F$ are
  interactions of two continuous treatments, which is a harder object than the
  paper's prose suggests. Callaway, Goodman-Bacon and Sant'Anna (2024) on
  continuous-treatment DiD is the current reference.

### 5. Home-front economic and social history — thin outside the OWI

`winkler1978` and `sparrow2011` are both excellent and both about *the state*.
The paper makes claims about the war economy and about civilian experience that
neither covers.

- **The war economy as economic history.** Harold Vatter, *The U.S. Economy in
  World War II* (1985); Alan Milward, *War, Economy and Society* (1977); Hugh
  Rockoff on price controls and *America's Economic Way of War* (2012); Robert
  Higgs (1992, *JEH*) "Wartime Prosperity? A Reassessment of the U.S. Economy in
  the 1940s," which directly challenges whether wartime output gains were real
  welfare gains — an objection the paper's premise of "productive investment"
  invites; Alexander Field on wartime and prewar productivity growth.
- **War-plant labor and migration.** The paper's mechanism for $W_i^F$ is
  agglomeration and labor-market depth, which is a migration story. James Gregory,
  *The Southern Diaspora* (2005) and the Great Migration literature (Boustan,
  *Competition in the Promised Land*, 2016; Collins and Wanamaker) are the direct
  citations, and Boustan's work in particular is methodologically adjacent.
- **Gender and race on the home front.** With female LFP and Black semiskilled
  employment as secondary outcomes: Ruth Milkman, *Gender at Work* (1987);
  Karen Anderson, *Wartime Women* (1981); Maureen Honey, *Creating Rosie the
  Riveter* (1984) — the last is also the right citation for the *content* of OWI
  visual rhetoric, which entry 20 cannot supply; Neil Wynn, *The African American
  Experience During World War II*; Nelson Lichtenstein, *Labor's War at Home*
  (1982) for the wartime labor settlement behind the Little Steel formula.

### 6. Small structural fixes

- **Commuting zones.** `cw_cty_czone.dta` is on disk and unused. War plants sited
  just outside cities split one economic shock across county lines. A CZ-level
  robustness run is standard practice and cheap. Cite Tolbert and Sizer (1996) and
  Autor and Dorn (2013).
- **Bond sales as a third exposure.** If `brunetetal2025` has county-level bond
  data, civilian financial sacrifice could be a third dimension in the typology.
  Worth checking.
- **Reception evidence for §6.** The claim that shared-sacrifice rhetoric had
  political efficacy needs evidence of reception, not only of transmission.
  Hadley Cantril's wartime public-opinion compilations and OWI's own Bureau of
  Intelligence surveys of civilian morale are the sources.
- **The posters are cited but not used.** `naraPosters` and `smithsonianPosters`
  appear only in the appendix while the body makes a visual-content claim on the
  strength of two secondary works. Move them into §6 with specific items.
- **The CRS casualty report is on disk and uncited.** `data/docs/literature/`
  holds CRS RL32492. It is a better citation than the VA teachers' guide.

---

## S4. Corrections and open verification items

Items requiring action before submission, in priority order.

| # | Item | Status |
|---|---|---|
| 1 | **Contract-data provenance conflict.** The paper attributes the reconstructed contract series and the "more true zeros" finding to `brunetReplication2025` (war-bonds replication data) in §2, §3, §5 and the appendix. `DATA_LEDGER.md` §6 records the file's provenance as "Brunet–Koustas WWII Major War Supply Contracts (via Goldin–Olivetti–Ferrie replication)." These cannot both be right, and the correct source is **not currently in the bibliography**. | **Must resolve.** Three body citations and one empirical premise depend on it. |
| 2 | **Roosevelt 1942 has no edition or archive.** Cite to a text: FDR Library Master Speech File, *Public Papers and Addresses*, or the American Presidency Project. | Must fix — form. |
| 3 | **$B_i^A$ (Eq. 2) is described as the preferred measure but is not computable** until DS2's NARA codes are crosswalked to FIPS (ledger §4.2). The paper's present tense overstates what exists. | Must fix — build or reframe. |
| 4 | **$W_i^F$ and $G_i$ are not built.** `FacilitiesDatabase.xls` is unparsed. Half the paper's central decomposition. | Must fix — build or reframe. |
| 5 | **The computed results are not in the paper.** $\mathcal{A}=0.455$, JS $=0.351$ bits, per-capita Spearman $=-0.034$, 1,579 counties with deaths and zero contracts, top-20 shares of 20.4% deaths vs 44.8% dollars — all real, all in the ledger, none in the `.tex`. §5 says the paper does "not report invented values," which is correct and admirable, but these are not invented. | Must fix — the per-capita $\rho$ of $-0.034$ is the strongest single sentence available to this paper. |
| 6 | **VA/DS1 number juxtaposition in §2** invites an invalid comparison (291,557 all-service battle vs. 300,131 Army/AAF all-status). Add a clause; consider adding the reconciliation described in entry 4. | Should fix. |
| 7 | **Crosswalk weight (`m1`–`m6`) undisclosed.** State which, and show robustness. | Should fix. |
| 8 | **`ferraracrosswalk2024` cites the article but not the ICPSR 150101-V4.1 deposit** actually used. Cite both. | Should fix. |
| 9 | **`naraArmy1946` / `naraNavy1946`** are cited as if consulted directly. If they are being cited as the provenance of the ICPSR deposit, say so. | Should clarify. |
| 10 | **Prime-contract-only measurement** is not discussed anywhere. It is the largest known systematic bias in $W_i^C$ and it cuts against the paper's headline finding. Add a paragraph in §3. | Should fix — a referee will find it. |
| 11 | **Residence-at-enlistment endogeneity** (war-boom migration → enlistment → death attributed to boom county) is undiscussed and biases $\mathcal{A}$ upward. | Should fix. |
| 12 | **County median family income does not exist in 1940** on the same basis as later years. Check $\Delta Y_{i,1940\rightarrow t}$ for income. | Verify. |
| 13 | **`garin2025` package concentration** — seven of eleven core quantities touch it. Disclose, and run the independent 3,073-county casualty check it provides. | Verify and disclose. |
| 14 | **Brodeur–Kattan's casualty universe** vs. DS1's. Confirm before using their results as premises. **[unverified]** | Verify. |
| 15 | **`jaworski2017` instrument identity** — confirm it is the 1938 IMP before repeating the §4 claim. **[unverified]** | Verify. |
| 16 | **`jaworskiyang2025`** characterized here from title and the paper's one-line gloss only. **[unverified]** | Verify. |
| 17 | **`aha1945` individual author** not determined. **[unverified]** | Verify. |
| 18 | **Retrieval dates formatted as publication dates** in `naraPosters` and `smithsonianPosters` (both "2026"). | Minor fix. |

---

*End of source apparatus. 24 sources documented.*
