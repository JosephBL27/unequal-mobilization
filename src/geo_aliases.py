#!/usr/bin/env python3
"""
Shared place->county resolution for the two CPA source volumes.

Both the contracts volume and the facilities volume record a *place* name, and
neither uses a consistent geographic vocabulary. Three failure modes recur:

  1. Boroughs and neighborhoods used as if they were cities
     (Brooklyn, Long Island City, San Pedro, Terminal Island).
  2. Government installations and company towns that were never incorporated
     places (Wilson Dam AL, Geneva UT, Lake City MO, Weldon Springs MO).
     These matter disproportionately: they are the large publicly financed
     plants that carry the G_i treatment.
  3. Transcription errors in the original volumes (Witchita, Paulsbord).

Every entry below is a deliberate historical identification, not a fuzzy match.
Sources: NARA plant records, USGS GNIS historical place lookup, and the plant
histories in the CPA volumes themselves.
"""
import re

def norm_city(s):
    if s is None: return None
    s = str(s).lower().strip()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    for a, b in [(r'\bft\b','fort'), (r'\bst\b','saint'), (r'\bmt\b','mount'),
                 (r'\bn\b','north'), (r'\bs\b','south'),
                 (r'\be\b','east'), (r'\bw\b','west')]:
        s = re.sub(a, b, s)
    return re.sub(r'\s+', ' ', s).strip()

# ---- 1. boroughs and neighborhoods -------------------------------------
BOROUGH = {
 # The city crosswalk resolves 'new york, NY' to Kings County, which sends
 # Manhattan's contracts (about $3.6bn) into Brooklyn. Override it.
 ('new york','NY'):36061,
 ('new york city','NY'):36061,
 ('brooklyn','NY'):36047, ('long island city','NY'):36081, ('flushing','NY'):36081,
 ('jamaica','NY'):36081, ('astoria','NY'):36081, ('corona','NY'):36081,
 ('woodside','NY'):36081, ('college point','NY'):36081, ('maspeth','NY'):36081,
 ('elmhurst','NY'):36081, ('richmond hill','NY'):36081, ('ozone park','NY'):36081,
 ('staten island','NY'):36085, ('bronx','NY'):36005, ('manhattan','NY'):36061,
 ('wilmington','CA'):6037, ('san pedro','CA'):6037, ('terminal island','CA'):6037,
 ('north hollywood','CA'):6037, ('van nuys','CA'):6037, ('venice','CA'):6037,
 ('hollywood','CA'):6037, ('canoga park','CA'):6037, ('el segundo','CA'):6037,
 ('vernon','CA'):6037, ('maywood','CA'):6037,
}

# ---- 2. installations, company towns, unincorporated plant sites --------
# Identified from the plant record; county assignment is the historical one.
INSTALLATION = {
 ('wilson dam','AL'):1033,       # TVA, Muscle Shoals -> Colbert Co
 ('muscle shoals','AL'):1033,
 ('childersburg','AL'):1121,     # Alabama Ordnance Works -> Talladega
 ('geneva','UT'):49049,          # Geneva Steel -> Utah Co
 ('magna','UT'):49035,           # Salt Lake Co
 ('mare island','CA'):6095,      # Navy Yard -> Solano Co
 ('port chicago','CA'):6013,     # Contra Costa
 ('velasco','TX'):48039,         # Dow magnesium -> Brazoria
 ('texas city','TX'):48167,      # Galveston
 ('choteau','OK'):40097,         # Pryor / Oklahoma Ordnance -> Mayes
 ('chouteau','OK'):40097,
 ('pryor','OK'):40097,
 ('weldon springs','MO'):29183,  # Atlas Powder -> St Charles
 ('lake city','MO'):29095,       # Lake City Arsenal -> Jackson
 ('warren township','MI'):26099, # Detroit Tank Arsenal -> Macomb
 ('willow run','MI'):26161,      # Ford bomber plant -> Washtenaw
 ('institute','WV'):54039,       # synthetic rubber -> Kanawha
 ('south charleston','WV'):54039,
 ('allenwood','PA'):42119,       # Union Co (per plant record)
 ('marcus hook','PA'):42045,     # Delaware Co
 ('essington','PA'):42045,
 ('johnsville','PA'):42017,      # Bucks Co
 ('sparrows point','MD'):24005,  # Bethlehem Steel -> Baltimore Co
 ('elkton','MD'):24015,          # Triumph Explosives -> Cecil
 ('bendix','NJ'):34003,          # Teterboro -> Bergen
 ('fort crook','NE'):31153,      # Martin bomber plant -> Sarpy
 ('mead','NE'):31155,            # Nebraska Ordnance -> Saunders
 ('burlington','IA'):19057,      # Des Moines Co
 ('east chicago','IN'):18089,    # Lake Co
 ('charlestown','IN'):18019,     # Indiana Ordnance -> Clark
 ('kingsbury','IN'):18091,       # LaPorte
 ('radford','VA'):51121,         # Montgomery Co (indep. city later)
 ('hopewell','VA'):51041,        # Chesterfield
 ('oak ridge','TN'):47001,       # Anderson Co
 ('milan','TN'):47053,           # Gibson
 ('childersburg','AL'):1121,
 ('pine bluff','AR'):5069,       # Jefferson Co arsenal
 ('parsons','KS'):20099,         # Labette
 ('baytown','TX'):48201,         # Harris
 ('pampa','TX'):48179,           # Gray
 ('henderson','NV'):32003,       # Basic Magnesium -> Clark
 ('richland','WA'):53005,        # Hanford -> Benton
 ('hanford','WA'):53005,
 ('vancouver','WA'):53011,       # Kaiser shipyard -> Clark
 ('sunflower','KS'):20091,       # Johnson Co
 ('tullahoma','TN'):47031,       # Coffee
 ('ravenna','OH'):39133,         # Portage
 ('ravenna','NE'):31019,
}

# ---- 3. transcription errors in the source volumes ---------------------
TYPO = {
 ('witchita','KS'):20173, ('pittsburg','PA'):42003, ('cincinatti','OH'):39061,
 ('detriot','MI'):26163, ('phillidelphia','PA'):42101, ('milwaukie','WI'):55079,
 ('paulsbord','NJ'):34015, ('wood rver','IL'):17119, ('minneapoils','MN'):27053,
 ('clevland','OH'):39035, ('baltimor','MD'):24510, ('los angles','CA'):6037,
}

# ---- 4. named war-plant sites identified from the plant record ---------
# These are unincorporated sites or company towns that carry large publicly
# financed plants. Each was identified from the operator + product in the CPA
# volume, then assigned its historical county.
PLANT_SITE = {
 ('crab orchard lake','IL'):17199,  # Illinois Ordnance -> Williamson
 ('west lynn','MA'):25009,          # General Electric -> Essex
 ('jones mill','AR'):5059,          # Alcoa alumina -> Hot Spring
 ('lester','PA'):42045,             # Westinghouse -> Delaware
 ('listerhill','AL'):1033,          # Reynolds Metals -> Colbert
 ('permanente','CA'):6085,          # Kaiser cement/magnesium -> Santa Clara
 ('robertson','MO'):29189,          # Curtiss-Wright -> St Louis Co
 ('southington','CT'):9003,         # Hartford
 ('wheatfield','NY'):36063,         # Bell Aircraft -> Niagara
 ('karnack','TX'):48203,            # Longhorn Ordnance -> Harrison
 ('shumaker','AR'):5103,            # Naval Ordnance -> Ouachita
 ('port newark','NJ'):34013,        # Essex
 ('wood ridge','NJ'):34003,         # Curtiss-Wright -> Bergen (NOT Woodbridge)
 ('woodridge','NJ'):34003,
 ('north hempstead','NY'):36059,    # Nassau
 ('hanover','MA'):25023,            # Plymouth (NOT Andover)
 ('grand island','NE'):31079,       # Cornhusker Ordnance -> Hall
 ('sidney','OH'):39149,             # Shelby
 ('joliet','IL'):17197,             # Elwood Ordnance -> Will
 ('elwood','IL'):17197,
 ('seneca','IL'):17099,             # LST shipyard -> LaSalle
 ('savanna','IL'):17015,            # Carroll
 ('baraboo','WI'):53000 if False else 55111,   # Badger Ordnance -> Sauk
 ('burlington','NJ'):34005,         # Burlington Co
 ('morgantown','WV'):54061,         # Monongalia
 ('point pleasant','WV'):54053,     # Mason
 ('kingsport','TN'):47163,          # Holston Ordnance -> Sullivan
 ('alcoa','TN'):47009,              # Blount
 ('sylacauga','AL'):1121,           # Talladega
 ('talladega','AL'):1121,
 ('brunswick','GA'):13127,          # Glynn
 ('macon','GA'):13021,              # Bibb
 ('marietta','GA'):13067,           # Bell bomber -> Cobb
 ('la porte','TX'):48201,           # Harris
 ('orange','TX'):48361,             # Orange Co
 ('beaumont','TX'):48245,           # Jefferson
 ('borger','TX'):48375,             # Hutchinson
 ('amarillo','TX'):48375,
 ('wichita falls','TX'):48485,      # Wichita Co
 ('tullytown','PA'):42017,          # Bucks
 ('conshohocken','PA'):42091,       # Montgomery
 ('eddystone','PA'):42045,          # Delaware
 ('claymont','DE'):10003,           # New Castle
 ('sparrows pt','MD'):24005,
 ('curtis bay','MD'):24510,         # Baltimore City
 ('middle river','MD'):24005,       # Glenn L Martin -> Baltimore Co
 ('port deposit','MD'):24015,       # Cecil
 ('parkersburg','WV'):54107,        # Wood
 ('nitro','WV'):54039,              # Kanawha
 ('ashtabula','OH'):39007,          # Ashtabula Co
 ('lordstown','OH'):39155,          # Trumbull
 ('ravenna arsenal','OH'):39133,
 ('newport','IN'):18165,            # Vermillion
 ('madison','IN'):18077,            # Jefferson
 ('evansville','IN'):18163,         # Vanderburgh
 ('michigan city','IN'):18091,      # LaPorte
 ('centerline','MI'):26099,         # Macomb
 ('center line','MI'):26099,
 ('ypsilanti','MI'):26161,          # Washtenaw
 ('wyandotte','MI'):26163,          # Wayne
 ('trenton','MI'):26163,
 ('st paul park','MN'):27163,       # Washington
 ('rosemount','MN'):27037,          # Dakota
 ('des moines','IA'):19153,         # Polk
 ('ankeny','IA'):19153,
 ('grand prairie','TX'):48113,      # Dallas
 ('garland','TX'):48113,
 ('kansas city','KS'):20209,        # Wyandotte
 ('neosho','MO'):29145,             # Newton
 ('louisiana','MO'):29163,          # Pike (Missouri Ordnance)
 ('baxter springs','KS'):20021,     # Cherokee
 ('pocatello','ID'):16005,          # Bannock
 ('ogden','UT'):49057,              # Weber
 ('tooele','UT'):49045,             # Tooele Co
 ('herington','KS'):20049,          # Dickinson
 ('hastings','NE'):31001,           # Adams (Naval Ammunition Depot)
 ('sioux city','IA'):19193,         # Woodbury
 ('bellevue','NE'):31153,           # Sarpy
 ('la salle','IL'):17099,
 ('sterling','IL'):17195,           # Whiteside
 ('rockford','IL'):17201,           # Winnebago
 ('melrose park','IL'):17031,       # Cook
 ('cicero','IL'):17031,
 ('la grange','IL'):17031,
 ('bedford','IN'):18093,            # Lawrence
 ('bloomfield','NJ'):34013,         # Essex
 ('kearny','NJ'):34017,             # Hudson
 ('linden','NJ'):34039,             # Union
 ('paulsboro','NJ'):34015,          # Gloucester
 ('deepwater','NJ'):34033,          # Salem
 ('carneys point','NJ'):34033,
}

ALIAS = {**BOROUGH, **INSTALLATION, **TYPO, **PLANT_SITE}

# Fuzzy matching must never cross a county line on a near-miss. These pairs
# look similar but are different places in different counties; block them.
FUZZY_BLOCK = {
 ('woodridge','NJ','woodbridge'), ('hanover','MA','andover'),
 ('wood ridge','NJ','woodbridge'), ('north hempstead','NY','south hempstead'),
 ('newport','IN','newpoint'), ('milton','PA','milton grove'),
}

def alias_frame():
    import pandas as pd
    return pd.DataFrame([(k[0], k[1], v) for k, v in ALIAS.items()],
                        columns=['cn','st','alias_fips'])
