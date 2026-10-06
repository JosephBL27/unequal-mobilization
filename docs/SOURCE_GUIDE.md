# Source Guide — Unequal Mobilization

Six families structure this list. Two supply the paper's own quantities directly: military casualty/enlistment microdata and primary federal investment records. A third — harmonization and county data — makes those two commensurable on a single fixed grid of 3,107 1940-boundary counties. Two literatures then bracket the contribution: a casualty-as-labor-shock tradition that treats WWII mobilization as a wage/demographic shock, and a war-investment econometrics tradition that treats WWII spending as a regional-development treatment; this paper is the first to hold casualty and investment apart as independently measured allocations and ask whether they align. The sixth family, rhetoric and the home front, supplies the primary and secondary sources for the humanities sub-question — what "shared sacrifice" was claimed to mean while the county data show how unevenly it was actually distributed.

---

## Military records and casualty data

### ferrara2024data — Ferrara, WWII Enlistment and Casualty Records, ICPSR 38927 (2024)
- **Key terms:** *Army/AAF* — the single branch this dataset covers (Navy, Marine Corps, Coast Guard fall outside it). *Home county* — the county-of-residence field the microdata is aggregated to. *DS1* — the 300,131-record death file within the larger study.
- **Role:** DATA. Primary microdata source for D_i^A; the companion 6.94M-record enlistment file supplies E_i^A. Both B_i^civic and B_i^A are built directly from these two county aggregates.
- **Watch out:** Army/AAF-only coverage means the paper's burden measures omit Navy/Marine/Coast Guard deaths, understating true county war mortality relative to all-service totals like va2025's.

### naraArmy1946 — War Dept, WWII Honor List of Dead and Missing Army and AAF Personnel, RG 407, NARA (1946)
- **Key terms:** *Honor List* — NARA's official name/rank/home-address roster of Army dead and missing, organized by state. *RG 407* — the Record Group housing Army adjutant-general records that includes this list. *Home of record* — the address convention that "home county" digitization descends from.
- **Role:** DATA (archival source). The original paper roster ferrara2024data digitized into ICPSR 38927; establishes the recording conventions behind D_i^A.
- **Watch out:** as a scanned wartime administrative document, transcription and place-name ambiguity in the original are inherited by any digitization built on it.

### naraNavy1946 — Navy Dept, State Summary of War Casualties for Navy, Marine Corps, and Coast Guard, RG 24, NARA (1946)
- **Key terms:** *State Summary* — a state-level Navy casualty tabulation, coarser than the Army list's individual detail. *Navy/Marine/Coast Guard personnel* — the branches this record covers, all excluded from D_i^A. *War casualties* — includes killed, wounded, and missing.
- **Role:** CONTEXT. Documents the scale of non-Army deaths the paper's Army/AAF focus leaves out, supporting the scope discussion around D_i^A.
- **Watch out:** state-level aggregation in the source means it cannot substitute for a county-level Navy casualty measure even if a referee asks why Navy deaths are excluded.

---

## Casualty-as-labor-shock literature

### acemoglu2004 — Acemoglu, Autor & Lyle, "Women, War, and Wages," JPE 112(3) (2004)
- **Key terms:** *Mobilization intensity* — a state-level share of men leaving civilian jobs for service, used as the wartime labor-supply shock. *War widow* — the mechanism linking mobilization to postwar female labor supply. *Wage structure* — the skill-group wage distribution the shock is used to explain.
- **Role:** BENCHMARK/CONTEXT. The methodological ancestor for treating WWII mobilization as an economic shock; situates D_i^A/E_i^A within an established tradition at a coarser (state) scale.
- **Watch out:** studies a labor-supply channel via state-level wage effects, not county investment or casualty geography — doesn't speak to the overlap/misalignment question.

### brodeur2022 — Brodeur & Kattan, "WWII, the Baby Boom, and Employment: County-Level Evidence," JOLE 40(2) (2022)
- **Key terms:** *County-level mobilization rate* — enlistment share of county population, the closest precedent to a county-scale intensity measure. *Sex ratio shock* — the male/female ratio change from military departure. *Baby boom* — the postwar fertility surge linked to local mobilization intensity.
- **Role:** BENCHMARK. Establishes the county as a valid unit for WWII mobilization research, methodologically close to this paper's E_i^A construction.
- **Watch out:** outcomes (fertility, employment) and channel (mobilization rate, not casualty-vs-investment divergence) differ substantially, limiting direct comparability of results.

### ferrara2022 — Ferrara, "World War II and Black Economic Progress," JOLE 40(4) (2022)
- **Key terms:** *Occupational upgrading* — Black workers' movement into higher-skilled jobs during wartime labor scarcity, the central outcome. *War-induced labor tightness* — the local labor slack exploited for identification. *Economic progress* — the outcome category spanning wages, occupation, employment.
- **Role:** BENCHMARK/CONTEXT. Extends the WWII-shock literature to distributional effects across racial groups, paralleling this paper's move from aggregate to distributional (geographic) analysis.
- **Watch out:** the distributional axis is race/occupation, not place — the analogy to geographic winners and losers is suggestive, not a shared empirical design.

---

## Primary investment records

### cpaContracts1946 — US Civilian Production Administration, Alphabetic Listing of Major War Supply Contracts (1946)
- **Key terms:** *Prime contract* — a contract awarded directly by the War or Navy Dept to a firm, distinct from subcontracted work. *Civilian Production Administration* — the postwar successor to the War Production Board that compiled this cumulative listing. *Cumulative listing* — totals all major contracts June 1940–September 1945 in one volume.
- **Role:** DATA. Primary archival source for W_i^C — all 190,693 contracts ($178.2bn) were transcribed from this volume to build per-capita county war-supply spending.
- **Watch out:** contracts are recorded at the awarded firm's listed address, which may be a headquarters rather than the plant that performed the work — a geocoding risk partly offset by the 1947 County Data Book validation (r=0.992).

### cpaFacilities1946 — US Civilian Production Administration, War Industrial Facilities Authorized July 1940–August 1945 (1946)
- **Key terms:** *Facility authorization* — formal government approval to build or expand a wartime plant, the unit of observation. *Publicly financed plant* — a facility built with federal funds, as opposed to privately financed expansion (W_i^F counts only the former). *Plant location* — the company/address field used to geocode each facility.
- **Role:** DATA. Primary source for W_i^F (the $19.1bn publicly financed share of $24.0bn total plant investment) and for G_i, built from the 1,306 largest facilities.
- **Watch out:** location is recorded as company/plant address at authorization, and the public-vs-private financing split depends on correctly parsing the source's category codes.

---

## War-investment econometrics

### brunet2026 — Brunet, "Stimulus on the Home Front: The State-Level Effects of WWII Spending," REStat 108(3) (2026)
- **Key terms:** *Fiscal multiplier* — the local output/employment response per dollar of war spending. *State-level spending shock* — war procurement aggregated to the state, the treatment variable. *Home-front stimulus* — framing WWII spending as regional Keynesian stimulus.
- **Role:** BENCHMARK. State-level precedent for estimating local effects of WWII spending, part of the lineage this paper's county-level, tripartite (contracts/plants/installations) design disaggregates.
- **Watch out:** state aggregation would average over exactly the intra-state contract/plant/installation divergence this paper finds near-orthogonal, potentially masking offsetting local effects.

### brunetetal2025 — Brunet, Hilt & Jaremski, "War Bonds and Household Saving in WWII," EEH 97 (2025)
- **Key terms:** *War bond deposit displacement* — the extent to which bond purchases substituted for ordinary bank deposits. *Household saving channel* — the mechanism (bond drives, payroll deduction) through which war finance reached households. *Home-front financing* — the broader civilian-side war finance category.
- **Role:** CONTEXT. Supplies one specific figure — the deposit-displacement estimate — used to characterize household war finance; not part of the county investment measures.
- **Watch out:** bond-buying is voluntary household behavior, a different allocation channel from the firm/plant/installation spending analyzed here — relevance is illustrative, not comparable data.

### brunetReplication2025 — Brunet, Hilt & Jaremski, Replication Data for "War Bonds and Household Saving in WWII," Princeton DSS (2025)
- **Key terms:** *Replication package* — the archived data/code reproducing brunetetal2025's results. *Princeton DSS* — Princeton's Data and Statistical Services repository hosting the deposit. *Deposit displacement figure* — the specific estimate drawn from the package.
- **Role:** DATA. Cited only to source the exact war-bond deposit-displacement figure attributed to brunetetal2025.
- **Watch out:** single-figure citation only — treating it as a broader data source for this paper's own panel would overstate its role.

### fishback2013 — Fishback & Cullen, "Second World War Spending and Local Economic Activity in US Counties, 1939-58," EHR 66(4) (2013)
- **Key terms:** *Fishback-Horrace-Kantor vector* — the specific prewar county control set this paper adopts directly as X_i. *Local economic activity* — the outcome category (retail sales, banking, population) across 1939-58. *Spending-to-outcome elasticity* — the core estimated county spending-outcome relationship.
- **Role:** METHOD/BENCHMARK. Supplies the prewar control-vector specification used for X_i, plus a direct benchmark of spending-outcome correlations against this paper's near-zero results.
- **Watch out:** their spending measure isn't decomposed into contracts/plants/installations, so elasticity magnitudes aren't directly comparable — only the control-vector logic transfers cleanly.

### garin2025 — Garin & Rothbaum, "The Long-Run Impacts of Public Industrial Investment on Local Development and Economic Mobility," QJE 140(1) (2025)
- **Key terms:** *Public industrial investment* — federally financed plant construction, the same category underlying W_i^F. *Economic mobility* — intergenerational income mobility, the long-run outcome emphasized. *Long-run local development* — the multi-decade postwar trajectory of plant-recipient counties.
- **Role:** BENCHMARK. The closest, most recent precedent for W_i^F; this paper's 1970 manufacturing-share finding (+0.35 for plants vs -0.63 for installations) directly tests and extends the Garin-Rothbaum mechanism.
- **Watch out:** their identification is plausibly causal (siting-based instruments), while this paper explicitly frames estimates as conditional associations — a referee will ask why that stronger design wasn't adopted here.

### jaworski2017 — Jaworski, "World War II and the Industrialization of the American South," JEH 77(4) (2017)
- **Key terms:** *Regional industrialization* — the shift of manufacturing toward the South during WWII, the central story. *War-induced structural change* — the claim that wartime investment durably altered a region's industrial mix. *South as treatment region* — the geographic scope of the analysis.
- **Role:** BENCHMARK. Establishes the qualitative postwar-legacy narrative — war investment reshaping regional industrial structure — that this paper generalizes nationally and decomposes into three differently-behaving channels.
- **Watch out:** single-region, single-channel scope; doesn't address the contracts/plants/installations divergence that is this paper's main contribution.

### jaworskiyang2025 — Jaworski & Yang, "Did War Mobilization Cause Aggregate and Regional Growth?" EEH 97 (2025)
- **Key terms:** *Aggregate vs. regional growth* — the central distinction between national- and place-level growth effects of mobilization. *War mobilization* — the treatment variable, spending plus manpower together. *Growth accounting* — the method decomposing observed growth into mobilization-attributable components.
- **Role:** BENCHMARK. Directly interrogates whether war-spending-to-growth links are causal, the same caution this paper adopts by framing its results as conditional associations given adverse pre-trends.
- **Watch out:** raises exactly the identification concern this paper does not fully resolve — a referee could invoke it to press harder on causal language.

---

## Harmonization and county data

### ferraracrosswalk2024 — Ferrara, Testa & Zhou, "New Area- and Population-based Geographic Crosswalks for US Counties and Congressional Districts, 1790-2020," Historical Methods 57(2) (2024)
- **Key terms:** *Population-weighted crosswalk* — reallocating data between differently-defined county boundaries in proportion to population rather than land area. *Boundary harmonization* — fixing historical records with shifting county lines onto one geography. *Area-based crosswalk* — the alternative (land-area) weighting scheme this method complements.
- **Role:** METHOD. Supplies the technique mapping every source — contracts, facilities, casualties, census — onto the paper's fixed 1940-boundary grid of 3,107 counties.
- **Watch out:** population weighting approximates poorly where boundary change doesn't track population evenly (e.g., annexation of sparsely populated land), introducing small-county measurement error.

### haines2010 — Haines & ICPSR, Historical, Demographic, Economic, and Social Data: The United States, 1790-2002, ICPSR 2896 (2010)
- **Key terms:** *County Data Book* — the compiled decennial county census series this study draws on, including the 1947 edition used for external validation. *Historical county panel* — the multi-decade (1790-2002) compiled dataset. *Prewar covariates* — the 1930/1940 census variables drawn into X_i.
- **Role:** DATA/BENCHMARK. Supplies the 1930/1940 controls in X_i and the 1950/1960/1970 outcomes Y_it; its County Data Book component also serves as the external benchmark validating the reconstructed contract series (r=0.992).
- **Watch out:** inherits original Census Bureau small-county suppression and rounding, and category definitions (e.g., "manufacturing") shift across census years.

---

## Rhetoric and the home front

### aha1945 — American Historical Association, GI Roundtable 13: How Shall Lend-Lease Accounts Be Settled? (1945)
- **Key terms:** *GI Roundtable* — a wartime pamphlet series for servicemen debating postwar policy, of which this is one title. *Lend-Lease settlement* — the debate over repaying/forgiving wartime aid to Allied nations. *Burden-sharing* — the underlying concept, here at the international rather than domestic level.
- **Role:** CONTEXT. Primary-source evidence of how wartime economic burden-sharing was framed for servicemen, supporting the humanities sub-question about sacrifice rhetoric.
- **Watch out:** addresses interallied financial settlement, not domestic county-level distribution of casualties and spending — its use is illustrative of the era's discourse, not direct evidence for the empirical claim.

### naraPosters — NARA, World War II Posters, 1942-1945, Series 44-PA (2026)
- **Key terms:** *Series 44-PA* — NARA's archival series designation for its WWII poster holdings, mostly OWI-directed. *Visual propaganda* — government imagery urging civilian support for the war effort. *Sacrifice iconography* — recurring visual tropes (rationing, bonds, loss) depicting shared wartime burden.
- **Role:** CONTEXT. Primary visual-source material for official "shared sacrifice" messaging, which the county-level findings empirically complicate.
- **Watch out:** documents elite-produced messaging, not lived experience or reception — cannot show whether the public believed sacrifice was actually shared.

### roosevelt1942 — F. D. Roosevelt, Fireside Chat: "On Sacrifice," April 28, 1942
- **Key terms:** *Fireside chat* — FDR's radio-address format for direct public communication. *Shared sacrifice* — the rhetorical claim that wartime costs were borne equally nationwide. *Home-front mobilization appeal* — the speech's function of asking civilians to accept burdens alongside servicemen.
- **Role:** CONTEXT. The paper's anchor primary text for the "nationally shared sacrifice" narrative that the overlap results (A=0.455, near-zero correlations) are used to empirically complicate.
- **Watch out:** a single speech is illustrative, not representative of the full range and evolution of wartime political rhetoric across 1942-45.

### smithsonianPosters — National Museum of American History, Princeton University Poster Collection, NMAH.AC.0433, Smithsonian
- **Key terms:** *NMAH.AC.0433* — the Smithsonian's archival accession number for this collection. *Princeton University Poster Collection* — the original collecting institution, now held at NMAH. *Material-culture evidence* — physical objects used as historical evidence, complementing textual sources like roosevelt1942.
- **Role:** CONTEXT. Supplementary primary visual source for wartime sacrifice messaging, functioning alongside naraPosters for the humanities sub-question.
- **Watch out:** overlaps substantially with naraPosters in evidentiary role; adds value only if distinct posters or collecting context are actually drawn on.

### sparrow2011 — Sparrow, Warfare State: World War II Americans and the Age of Big Government, Oxford UP (2011)
- **Key terms:** *Warfare state* — Sparrow's term for the WWII-era expansion of federal fiscal/administrative capacity that outlasted the war. *Fiscal citizenship* — how wartime taxation and spending reshaped Americans' relationship to the federal government. *Big government expansion* — the thesis linking mobilization to permanent federal growth.
- **Role:** CONTEXT. Secondary-source historical framework situating federal war investment (W_i^C, W_i^F, W_i^M) within the "warfare state" historiography.
- **Watch out:** a synthetic historical argument, not a quantitative source — offers interpretive framing, not a testable claim the paper's results can be checked against.

### va2025 — US Dept of Veterans Affairs, America's Wars, Veterans Day Teachers Resource Guide (2025)
- **Key terms:** *Official casualty totals* — the VA's standard aggregate death/service figures by conflict, the widely-cited "national" number. *Veterans Day Teachers Resource Guide* — the document's public-education format. *America's Wars* — the VA's recurring comparative-conflict casualty summary title.
- **Role:** CONTEXT. Likely supplies the standard national-scale WWII casualty/service figures against which the paper's county-level, uneven-distribution findings can be contrasted as a popular baseline.
- **Watch out:** a pedagogical summary, not a scholarly or primary source — aggregate national figures only, no county detail; would need independent verification if used beyond rhetorical framing.

### winkler1978 — Winkler, The Politics of Propaganda: The Office of War Information, 1942-1945, Yale UP (1978)
- **Key terms:** *Office of War Information (OWI)* — the federal agency (1942-45) that produced and coordinated wartime propaganda, including the posters cited above. *Politics of propaganda* — Winkler's framing of OWI's internal struggles over how to message the war. *Government messaging apparatus* — the institutional machinery generating the sacrifice-rhetoric artifacts.
- **Role:** CONTEXT. Secondary-source institutional history of the agency producing the sacrifice rhetoric analyzed elsewhere, grounding the humanities sub-question in its production context.
- **Watch out:** covers OWI's internal politics and production process, not audience reception — doesn't establish whether the "shared sacrifice" message was believed or effective.

---

## Summary table

| Source key | Family | Role |
|---|---|---|
| ferrara2024data | Military records and casualty data | DATA |
| naraArmy1946 | Military records and casualty data | DATA |
| naraNavy1946 | Military records and casualty data | CONTEXT |
| acemoglu2004 | Casualty-as-labor-shock literature | BENCHMARK |
| brodeur2022 | Casualty-as-labor-shock literature | BENCHMARK |
| ferrara2022 | Casualty-as-labor-shock literature | BENCHMARK |
| cpaContracts1946 | Primary investment records | DATA |
| cpaFacilities1946 | Primary investment records | DATA |
| brunet2026 | War-investment econometrics | BENCHMARK |
| brunetetal2025 | War-investment econometrics | CONTEXT |
| brunetReplication2025 | War-investment econometrics | DATA |
| fishback2013 | War-investment econometrics | METHOD |
| garin2025 | War-investment econometrics | BENCHMARK |
| jaworski2017 | War-investment econometrics | BENCHMARK |
| jaworskiyang2025 | War-investment econometrics | BENCHMARK |
| ferraracrosswalk2024 | Harmonization and county data | METHOD |
| haines2010 | Harmonization and county data | DATA |
| aha1945 | Rhetoric and the home front | CONTEXT |
| naraPosters | Rhetoric and the home front | CONTEXT |
| roosevelt1942 | Rhetoric and the home front | CONTEXT |
| smithsonianPosters | Rhetoric and the home front | CONTEXT |
| sparrow2011 | Rhetoric and the home front | CONTEXT |
| va2025 | Rhetoric and the home front | CONTEXT |
| winkler1978 | Rhetoric and the home front | CONTEXT |
