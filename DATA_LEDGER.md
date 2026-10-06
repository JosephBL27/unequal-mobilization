# WWII Sacrifice–Investment Project — Governing Data Ledger

**Status date:** 2026-08-28 · **Supersedes:** the handoff ledger pasted into chat
**Authority:** This file governs. Where it disagrees with the earlier ledger, this
file is right — every claim below was verified by reading the file on disk.

Paper: `paper/War_Divergence.tex` — *Unequal Mobilization: Military Loss, Federal
War Investment, and the Geography of Postwar Development* (Joseph Blumberg).

---

## 1. Headline corrections to the previous ledger

The old ledger was written before the archives were unpacked. Six of its claims
are wrong, and two of them were blocking work that is in fact already possible.

| # | Old ledger said | Actually true | Consequence |
|---|---|---|---|
| 1 | DS1 casualties **NEEDED** | **On disk**, 300,131 × 11 | No download required |
| 2 | DS1 has "state/county residence" needing assignment | `COUNTYID` **is the county FIPS code** (verified: Morgan IL→17137, Bristol MA→25005, Douglas WI→55031) | County deaths are one merge away, not a geocoding project |
| 3 | DS2 **NEEDED**, ~5 GB | **On disk** as 873 MB TSV + 1.26 GB `.stc`; converted to **142 MB parquet**, 8,293,187 rows exact | No download; loads in seconds |
| 4 | DS3 optional/not held | **On disk**, 65,507 × 18, and it carries **full county FIPS** | Usable immediately for descriptive all-service maps |
| 5 | Place→county crosswalk **NEEDED** (NHGIS, geocoding) | `cw-city-county.dta` (25,131 rows) ships inside the Garin–Rothbaum package | **98.0% of contract dollars** already assigned to counties |
| 6 | Haines: download ~20 files | All **106** already downloaded; **20 needed** ones copied in (55 MB of 528 MB) | Nothing to download |
| 7 | FTZ crosswalks **NEEDED** | Arrived mid-session as ICPSR 150101-V4.1; 1940-target crosswalks for every census year extracted | Harmonization solved |

**The single most consequential correction:** the Garin–Rothbaum replication
package is not just the plant data. It contains the city→county crosswalk, a
ready-made county casualty/enlistment panel, the Fishback–Horrace–Kantor prewar
control set with coordinates, county adjacency for spatial errors, and the
combined 1947–77 County Data Books. It closed four of the ledger's open P0 items.

---

## 2. What is on disk — verified inventory

All paths are relative to the repository root.
Row and variable counts were read from the files, not from documentation.

### 2.1 Military exposure — ICPSR 38927 (Ferrara)
`data/raw/casualties_icpsr38927/`

| File | Rows × Vars | Geography | Role |
|---|---|---|---|
| `38927-0001-Data.dta` (DS1) | 300,131 × 11 | `STATEICP` + `COUNTYID` = **county FIPS** | $D_i^A$ Army/AAF fallen |
| `38927-0002-Data.tsv` (DS2) | 8,293,187 × 24 | `ENL_STATE`, `ENL_COUNTY` (NARA codes) | $E_i^A$ enlistment denominator; `KILLED` flag |
| `38927-0003-Data.dta` (DS3) | 65,507 × 18 | `FIPS`, `STATEFIPS`, `COUNTYFIPS`, `PLACEFIPS` | Navy/USMC/USCG — **descriptive only** |
| `38927-0002-Data.stc` | — | — | 1.26 GB Stata-5 compressed; **unreadable without Stata**, superseded by the TSV |

DS1 `STATUS`: KIA 171,530 · DNB 82,479 · DOW 24,786 · FOD 18,888 · M 1,352 ·
DOI 912 · blank 184. Only 44 records lack a county name.

> **Universe warning, carried into the paper's Data section.** DS1 and DS3 do not
> share a definition. Army/AAF honor lists include battle and non-battle dead and
> missing; the Navy/USMC/USCG lists exclude deaths inside the United States and
> deaths from disease, homicide, or suicide. **Never sum DS1 + DS3 into an
> all-service total.** Causal work stays inside DS1 ∪ DS2.

### 2.2 Procurement — Brunet–Koustas contracts
`data/raw/contracts/WWII_contracts_clean.dta` — 190,693 × 22.
Carries `city_name`, `state`, `fips_state`, value, product, agency, dates.
No county FIPS in the source; assigned in §3.1 below.

### 2.3 County outcomes and controls — Haines ICPSR 2896
`data/raw/haines_icpsr2896/` — **20 of 106** datasets, 55 MB.

- **Pretrends** DS0024 (1920) · DS0026–29 (1930 I–IV) · DS0030 (1937 unemployment)
- **Baseline** DS0032, DS0033 (1940 I–II)
- **Postwar** DS0035–36 (1950) · DS0038–40 (1960) · DS0041 (1970)
- **County Data Books** DS0070 (1947) · DS0071 (1949) · DS0072 (1952) · DS0074 (1962) · DS0075 (1967) · DS0076 (1972)

DS0071 (1949) was added beyond the old ledger's list — it sits between the 1947
and 1952 books and tightens the immediate-postwar window.

### 2.4 Durable public plants and prewar controls — Garin & Rothbaum (2025)
`data/raw/garin_rothbaum/` — 731 MB extracted from the Harvard Dataverse package.
The files that matter, and why:

| File | Size | What it unlocks |
|---|---|---|
| `Data/RawData/FacilitiesRaw/FacilitiesDatabase.xls` | 6.2 MB | Plant-level facilities → $W_i^F$ and the $G_i$ treatment. **NOT a CPA volume**: this is U.S. War Production Board, *War Manufacturing Facilities Authorized through October 1944 by General Type of Product of Operator in 1939* (March 1945), digitized by Garin–Rothbaum from Harvard scans. |
| `Data/RawData/cw-city-county.dta` | 2.4 MB | **25,131-row city→county crosswalk.** Solves contract geocoding |
| `Data/RawData/WWII_draft_volunteer_casualties_Army_AirForce.dta` | 394 KB | **3,073-county** casualties + volunteer/drafted, by race, with 14–40/14–45 age denominators — an independent check on anything built from DS1/DS2 |
| `Data/RawData/fishbackhorracekantor.dta` | 1.8 MB | 3,067 counties × 130 prewar vars incl. `LATITUDE`/`LONGITUD` — the $X_i$ vector **and** coordinates for Conley spatial errors |
| `Data/RawData/NBER_county_adjacency2010.dta` | 1.8 MB | 22,200 adjacency pairs — spatial weights |
| `Data/RawData/ccdb47_77.dta` | 21.5 MB | County Data Books 1947–77 pre-combined |
| `Data/RawData/crosswalk_statefip_stateicp_1910.dta` | 4.5 KB | `STATEICP` ↔ `statefip`; required to complete DS1's FIPS |
| `Data/RawData/cw_cty_czone.dta` | 51 KB | County → commuting zone |
| `Data/RawData/DD350/countyfips.dta` | 435 KB | 2,980-county FIPS reference (a DD350 subset — **not** all 3,141; see §5) |
| `Data/RawData/Census19{20,30,40,50}.dta`, `unemp37.dta` | — | **Byte-identical** to Haines DS0024/0026/0032/0035/0030 (SHA-256 verified). Kept for replication fidelity, not re-derived |

`Data/CreatedData/` and `Data/Temp/` ship **empty** — they are outputs of their
Stata build, not inputs.

---

## 3. Derived data built so far

> **Stale figures below (flagged 2026-08-30).** Sections 3.x record an earlier
> pipeline state. Superseded values: contract geocoding 98.0% → **98.5%** of
> dollars; counties with any contract 1,489/48.0% → **48.5%**; counties that lost
> men and received no contract 1,579 → **1,553**; plant validation $15.3bn vs
> $16.7bn / Pearson 0.949 → **$15.0bn vs $16.3bn / 0.958**; geocoding stage split
> Exact 93.2% / Alias 5.2% → **Exact 83.1% / Alias 15.2%**. The manuscript and
> `src/audit_paper_vs_data.py` are authoritative; this ledger is narrative.

### 3.1 Contract → county assignment — **solved to 98.0% of dollars**

Three-stage match against `cw-city-county.dta`:

| Stage | Rows | Dollars |
|---|---|---|
| Exact `city + state` | 90.5% | 91.5% |
| + normalization (`FT`→`Fort`, `ST`→`Saint`, punctuation, directionals) | 91.8% | 93.2% |
| + 31-entry alias table (NYC boroughs, LA neighborhoods, plant sites, source typos) | **95.7%** | **98.0%** |

Counties covered: **1,499**. Residual: 8,247 rows / $3.61 bn of $181.0 bn,
spread over 711 distinct city-states — a long tail of typos (`WOOD RVER`,
`PAULSBORD`) and unincorporated plant sites.

> The residual is **not** missing at random: it concentrates in dense industrial
> metros whose plant addresses used neighborhood names. Report the coverage rate
> in the paper, and check whether dropping unmatched rows moves $\mathcal{A}$.

### 3.2 DS2 enlistment → parquet
`data/interim/ds2_enlistment.parquet` — 8,293,187 rows, **142 MB** (6.1× smaller
than the TSV). Row count matches the ICPSR manifest exactly. Built by
`src/ds2_to_parquet.py`; all columns typed as strings where the source mixes
numeric and coded values (`AGCT` contains `"U5"`, which is why a naive numeric
read fails).

---

## 3.3 First computed result — the overlap coefficient

Built by `src/overlap_analysis.py` on 3,104 counties in the 1940 universe
(132.1M people). **These are real numbers from the real data, not placeholders.**

| Quantity | Value |
|---|---|
| Overlap coefficient $\mathcal{A}$ | **0.455** |
| Jensen–Shannon divergence | 0.351 bits |
| Spearman $\rho$ (raw counts) | 0.612 |
| Spearman $\rho$ (**per capita**) | **−0.034** |

Coverage and concentration:

- 3,037 counties (97.8%) recorded at least one Army/AAF death
- 1,489 counties (48.0%) received any major contract dollar
- **1,579 counties lost men but received no major contract at all**
- Top 20 counties: **20.4% of deaths, 43.8% of contract dollars**
- Top 100 counties: 40.7% of deaths, 81.5% of dollars

**Two things to notice.**

First, the top-20 contract share of 43.8% sits right on Fishback and Cullen's
"roughly two-fifths to the top twenty counties." Our contract series was built
independently, from Brunet's reconstruction through a different crosswalk. The
agreement is a genuine external validation of the city→county match in §3.1.

Second, the per-capita rank correlation is **−0.034** — statistically
indistinguishable from zero. Once county size is netted out, knowing a county's
fatal burden tells you essentially nothing about how much war investment it
received. That is the paper's thesis expressed as a single number, and it is
considerably stronger than "imperfect correspondence."

> **Caveat to state in the paper.** Concentration figures use matched contracts
> only (98.0% of dollars). The 2.0% residual concentrates in dense industrial
> metros, so top-20 and top-100 shares are, if anything, *understated*.
> Re-check $\mathcal{A}$ after resolving the residual.

Artifacts: `data/analysis/county_exposure_panel.parquet`,
`overlap_results.json`, `match_report.json`, `contracts_unmatched.csv`.

---

## 3.4 Second session — built, validated, and one new finding

**Facilities parsed.** The WPB facilities volume (29 sheets) is now plant-level
data: 14,693 records, $24.01bn, 79.7% publicly financed, reconciling to 0.00%.
See `src/parse_facilities.py`. Three parsing bugs were fixed; footnote markers
like `14,275B/` alone had zeroed $1.19bn of the largest public plants.

**Master panel built.** `data/analysis/master_panel_v2.parquet` — 3,107 counties,
75 variables: three war exposures, Army/AAF deaths, 1930/1940 controls,
Fishback–Horrace–Kantor prewar vector with coordinates, and outcomes at 1940,
1950, 1960, 1970. Coverage 99%+ on every outcome.

**External validation passed.** The reconstructed contract series against the
1947 County Data Book: $177.3bn vs $180.4bn, Pearson 0.992, Spearman 0.957,
top-20 share 44.0% vs 42.7% on the 3,070 counties both series carry. Publicly
financed plant against County Data Book *industrial* facilities: $15.0bn vs
$16.3bn, Pearson 0.958.

**A third geography.** The County Data Book splits war facilities into industrial
(`var90`) and **military** (`var91`, $9.8bn — camps, bases, depots). The two are
nearly orthogonal (Spearman 0.31). Per capita, all three investment types are
uncorrelated with fatal burden (−0.031, +0.008, −0.039), and the two kinds of
federal capital left opposite legacies: by 1970 military installations show the
largest population effect (+0.050) but a large negative effect on manufacturing
share (−0.630) and homeownership (−0.340), while industrial plant raised all
three. Full results in `docs/AUDIT.md` §3.2.

**Pre-trends are partly adverse** and bound the causal language — see
`docs/AUDIT.md` §4.2.

**One citation error blocks submission**: `brunetReplication2025` (a war-bonds
replication package) is cited four times as the source of the contract data.
`docs/AUDIT.md` §4.1.

Deliverables: `docs/AUDIT.md`, `docs/SOURCE_APPARATUS.md`, 12 compiled tables in
`paper/tables/`.

## 6.1 Provenance recovered 2026-08-30 (disk search)

| Source | Established provenance | Evidence |
|---|---|---|
| **Jaworski IMP instruments** | Jaworski's openICPSR replication deposit for *"World War II and the Industrialization of the American South,"* **Journal of Economic History 77(4), December 2017: 1048–1082**. Our `data/raw/jaworski_imp/data-controls-raw.dta` is **byte-identical** to `data/controls/data-controls-raw.dta` in that deposit. | SHA-256 `ad1f7e80af2910bc6917d87cdf34bddb71166f8f719207abc70ed144eea5ffa5` on both copies; deposit at `~/Downloads/2017JEH_OpenICPSR/`, its `readme.rtf` states the article, volume, issue and page range verbatim. |
| **Garin–Rothbaum package** | Harvard Dataverse, **`doi:10.7910/DVN/NGRAWI`**, downloaded 2026-08-28. | The DOI is embedded in the download URL macOS recorded: `dvn-cloud-iqss.s3.amazonaws.com/10.7910/DVN/NGRAWI/...`, referrer `dataverse.harvard.edu`. |
| **ICPSR 38927 (casualties/enlistment)** | ICPSR, `doi:10.3886/ICPSR38927.v1`, released 2024-04-02. | `38927-descriptioncitation.html` gives the preferred citation verbatim; the zip's `kMDItemWhereFroms` records an `icpsr.umich.edu` PCMS download. |
| **FTZ crosswalks** | ICPSR deposit **`doi:10.3886/E150101`**; the underlying paper is documented on disk only as Ferrara, Testa & Zhou (2021), *CAGE Working Paper No. 588*. | `FTZ_teaching_material.pdf` pp. 9 and 14. **The manuscript's *Historical Methods* 57(2), 2024, 67–79 placement is not corroborated on disk** — it may be the published version of that working paper, but Joseph must confirm it. |
| **Brunet dissertation** | eScholarship, `qt668691f7`. | `kMDItemWhereFroms` on the PDF. |
| **DS1 universe** | Documented in DS1's own ICPSR codebook: 300,131 records split killed in action 171,530 (57.2%), **died non-battle 82,479 (27.5%)**, died of wounds 24,786, finding of death 18,888, died of fatal battle injury 912, missing 1,352. CRS RL32492 note (d) defines "died non-battle" as sickness, homicide, suicide or accident outside combat areas. | `38927-0001-Codebook-ICPSR.pdf` p. 7 (STATUS / STATUSNUM); `CRS_RL32492_war_casualties.pdf` p. 3. |
| **DS3 universe** | CRS Table 27, "Navy, Marine Corps, and Coast Guard Personnel / State Summary of War Casualties", reports the dead in **two** columns only — Combat and Prison Camp — with no non-battle category. That is the structural basis for non-additivity. No document on disk states an explicit exclusion rule; do not assert one. | `CRS_RL32492_war_casualties.pdf` p. 3, Table 27 header. |
| **CRS RL32492 date** | **None.** The footer reads "VERSION 24 · UPDATED" followed only by the page number; PDF metadata carries only the 2026-08-28 download. The bibliography cites it undated. Do not supply a year. | PDF footer and `pdf.metadata`. |
| **NARA record groups** | **Not corroborated.** RG 407 appears nowhere on disk; the only record group in the 309-page NARA reference PDF is RG 64, and it attaches to NARA's own documentation, not to the Honor List. Both RG numbers removed from the bibliography. | `NARA_100.1CL_SD_source.pdf`, full-text search. |
| **Haines ICPSR 2896** | Current archive-preferred citation carries **no place of publication** and DOI `10.3886/ICPSR02896.v3`, distributed 2010-05-21. The pre-2018 form with "Ann Arbor, MI" and "ICPSR02896-v3" is superseded — the archive says so explicitly. Bibliography now matches the current form. **8 of the 20 parts on disk are read** (32, 35, 38, 41, 70, 72, 75, 76). | `02896-descriptioncitation.html` line 75 and its Version History; `grep -ohE "haines\('[0-9]{4}'" src/*.py`. |
| **1947 County Data Book** | Part 70's variables 88–91 come from Tables 1 and 3 of U.S. Bureau of the Census, *County Data Book* (GPO, 1947). Now cited directly at the validation benchmark. | `02896-Codebook.pdf` p. 35, Data Sources. |
| **DS3 source document** | Documented *inside the data*: DS3's `MAINSTRING` field carries entries reading "Published Missing on Maine State Summary of War Casualties" and "Carried Missing on Colorado State Summary", naming the source series. | `38927-0003-Data.dta`, 18 such records. |
| **Contract microdata** | **RESOLVED 2026-08-30 (web).** The Google Drive file id recovered from the download attribute — `1MC0WJtxxtOjaKqy4n-YlGOrRB_6T49Dl` — is the link Gillian Brunet publishes on her own research page as "WWII contract data," alongside Brunet, Hilt and Jaremski, *Inflation, War Bonds, and Voter Backlash in the 1950s*, **Review of Economics and Statistics**, `doi:10.1162/REST.a.1783`. It is therefore an author-distributed public file, not a private share. Cite it as distributed by the authors; there is no DOI for the data file itself. | `xattr -l data/raw/contracts/WWII_contracts_clean.dta` → `kMDItemWhereFroms` gives the id; `sites.google.com/site/gillianmbrunet/research` links the identical id under "WWII contract data". The county-level WWII spending file is separately deposited at openICPSR `doi:10.3886/E226845V2`. |

**Not a validation source.** Jaworski's deposit also carries `data/ww2/data-investment-final.dta`,
a county-level war-facilities aggregation. It is **not** comparable to ours: 6,379 raw rows and
$6.803bn national against our 14,681 and $20.812bn, with only 633 facility-bearing counties in
common. The 0.98 correlation on that partial overlap is not evidence of agreement and must not be
reported as external validation without first establishing what his universe restricts to.


## 3.5 Third session — NARA decoded, boundaries acquired, panel final

**The NARA enlistment geography is decoded.** Joseph produced a crosswalk from
the NARA county code list (`data/raw/crosswalks/nara/`). The NARA county code is
the county FIPS code; the NARA *state* code is not (Alabama 41, Arizona 98,
Arkansas 87, California 91). 99.8% of derived FIPS fall inside the 1940 census
universe. **7,280,828 of 8,293,187 DS2 records (87.8%) now map to counties** —
the residual is "United States at large", Alaska, Hawaii, the Canal Zone, and
foreign residence.

Validation: county enlistment from DS2 correlates with the Garin–Rothbaum
tabulation at **0.990**; DS2's own `KILLED` flag correlates with DS1 deaths at
0.945 but undercounts by 32% (enlistment-to-casualty match failure). **DS1 stays
authoritative for deaths; DS2 supplies the denominator and composition.**

**Composition variables now available** for 7.17M enlistees: race, education,
birth year, enlistment source, AGCT score. Composition explains 17.7% of the
variance in county fatality rates. Volunteer share raises the rate sharply
(+220), Black share lowers it (−39.5), education and AGCT raise it — all
consistent with assignment to branch. Composition-adjusted risk correlates with
investment at −0.182 (contracts), −0.118 (plant), −0.083 (military): more
negative than unadjusted.

**County boundaries acquired.** Newberry Atlas of Historical County Boundaries
(free, no login), sliced to 1 April 1940. NHGIS 1940 conflated shapefile also on
disk at `data/raw/geo/nhgis_1940/`. Two maps are in the paper.

**Jaworski IMP replication filed** at `data/raw/jaworski_imp/` — the 1938
Industrial Mobilization Plan controls, the input to a future instrument.

**Two geocoding errors fixed.** The city crosswalk sent `new york, NY` to Kings
County, putting $3.64bn of Manhattan's contracts in Brooklyn; aliases now
override the crosswalk. And 14 independent cities held $6.83bn of contracts but
only 251 deaths (0.11 per 1,000 against 2.26 national) because the sources split
city from county — all 26 are now merged into their parent county, identified by
longest shared border on the 1940 boundaries.

**Final panel: 3,073 continental counties, 131.7M residents, 85 variables.**

## 4. What is still genuinely missing

**Nothing that blocks the paper.** The Ferrara–Testa–Zhou crosswalks arrived
mid-session (ICPSR 150101-V4.1) and closed the last P1 item.

### 4.1 Harmonization — now solved
`data/raw/crosswalks/ftz_1940/` holds population-weighted county crosswalks to
**1940 geography** for every census year 1790–2020, plus `Identifiers_1940.csv`.
Each row carries `gisjoin_<year>`, `gisjoin_1940`, area, and six alternative
population weights `m1_weight`…`m6_weight`. The years this paper needs —
1920, 1930, 1950, 1960, 1970 → 1940 — are all present.
County centroids (lat/lon) extracted to `data/raw/crosswalks/ftz_centroids/`
for Conley spatial standard errors.

### 4.2 Remaining derived work (not downloads)

| Item | Status |
|---|---|
| DS2 `ENL_STATE`/`ENL_COUNTY` → FIPS | **Open.** These are NARA codes; the aggregation yields 11,410 state-county cells against ~3,100 real counties, so a crosswalk is required before $E_i^A$ can be merged. Validate the result against G&R's `WWII_draft_volunteer_casualties_Army_AirForce.dta`, which already has county-level volunteer/drafted counts |
| $W_i^F$ and $G_i$ from `FacilitiesDatabase.xls` | **Open.** Plant-level file is on disk, not yet parsed |
| Contract residual (2.0% of dollars) | **Open.** 711 city-states in `data/analysis/contracts_unmatched.csv` |
| 1938 Industrial Mobilization Plan counts | **P2, optional.** `fishbackhorracekantor.dta` proxies prewar industrial capacity |
| NHGIS 1940 boundary shapefiles | **P2, figures only.** Not needed for estimation |

### 4.3 Supporting documents now filed
`data/docs/literature/` — CRS RL32492 casualty tables, Fishback & Cullen (2013)
*EHR*. `data/raw/geo/census_apportionment.csv` — historical state populations.

## 5. Known traps

1. **`countyfips.dta` covers 2,980 counties, not 3,141.** It is a DD350 subset.
   The 4% of DS1 counties that fail against it are Virginia independent cities
   (51xxx) — a genuine known hard case, not a bug in the FIPS derivation. Use a
   complete 1940 FIPS list for validation, not this file.
2. **`.stc` files need Stata.** No Python or R reader handles Stata-5 compressed.
   The header is literally `**COMPRESSED**` repeated — that is a real ICPSR
   format, not a corrupt download. Use the `.dta`/`.tsv` siblings.
3. **`AGCT` in DS2 is not numeric** (`"U5"` appears). Same for several coded
   columns. Read as string, cast deliberately.
4. **DS1 + DS3 are not additive.** See §2.1.
5. **G&R's `Census*.dta` are Haines files renamed.** Do not treat agreement
   between them as independent corroboration — it is the same bytes.
6. **County Data Book war spending (DS0070) is the legacy series.** Brunet's
   reconstruction finds more true-zero counties. Use reconstructed contracts as
   preferred; DS0070 is a robustness comparison only.

---

## 6. Provenance

| Source | Citation |
|---|---|
| Casualties/enlistment | Ferrara, A. *WWII Enlistment and Casualty Records, US, 1941–1945.* ICPSR 38927-v1, 2024. doi:10.3886/ICPSR38927.v1 |
| Contracts | Brunet–Koustas digitization of CPA (1946), *Alphabetic Listing of Major War Supply Contracts*. Transcribed to CSV by E-Records USA; cleaned by Gillian Brunet and Dmitri Koustas (Brunet 2017 dissertation, Appendix A.2). **The route by which this particular release reached the project is not recorded — Joseph should document it.** It holds 190,693 rows against the dissertation's 190,599, so it is a later vintage, not that extract. |
| County panel | Haines, M. *Historical, Demographic, Economic, and Social Data: US, 1790–2002.* ICPSR 2896-v3 |
| Plants / prewar controls | Garin, A. & Rothbaum, J. (2025), QJE. Harvard Dataverse doi:10.7910/DVN/NGRAWI |

---


## 6.2 Citations verified against primaries 2026-08-30 (web)

Four bibliography entries were carrying invented or mis-attributed detail. All
four are now sourced.

| Entry | Was | Is |
|---|---|---|
| `roosevelt1942` | "Fireside Chat on the Economy and Equality of Sacrifice" — a title assembled from a phrase inside the speech | **"Fireside Chat 21: On Sacrifice,"** 28 April 1942. The phrase *economy and equality of sacrifice* is verbatim in the transcript (Miller Center, UVA), but it is not the title. |
| `naraPosters` | dated 2026, no record group | **Record Group 44, Records of the Office of Government Reports**; Local ID 44-PA, NAID 513498, 2,828 items, Still Picture Branch, College Park. Undated. |
| `smithsonianPosters` | "National Museum of American History. 2026" | **Archives Center, NMAH**, Collection NMAH.AC.0433, donated by Princeton University Library 1963 and 1967. Undated. |
| `brunetReplication2025` | "Princeton University Data and Statistical Services" — a library service, not a repository | **openICPSR, `doi:10.3886/E226845V2`**. The article is *Explorations in Economic History* 97: 101692. |

`brunet2026` (REStat 108(3): 628--644) and `ferraracrosswalk2024` were checked and
stand as written.


## 7. Maintenance

Re-run `python src/inventory.py` after adding any file. It hashes every data
file, flags exact duplicates, and rewrites `data/docs/inventory.json`.
Update this ledger in the same commit as any change to `data/raw/`.
