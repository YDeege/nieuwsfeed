"""
Configuratie voor de Lumen Group interne nieuwsbrief.
Alle instelbare waarden staan hier bij elkaar, zodat je niets in de logica hoeft aan te passen.
"""

# --- Tijdvenster ---------------------------------------------------------
# Aantal dagen terug dat als "nieuw" telt. Wekelijks = 7.
DAGEN_TERUG = 7

# --- Bronnen -------------------------------------------------------------
# AP en EDPB leveren een RSS-feed. Rechtspraak.nl en EUR-Lex worden apart
# opgehaald via hun eigen API (zie collectors.py), omdat filteren daar
# gerichter moet.

RSS_BRONNEN = [
    {
        "naam": "Autoriteit Persoonsgegevens",
        "categorie": "Toezichthouder (NL)",
        "url": "https://www.autoriteitpersoonsgegevens.nl/feed/article/rss.xml",
        # AP-feed gaat over privacy; geen extra trefwoordfilter nodig.
        "filter_op_trefwoord": False,
    },
    {
        "naam": "European Data Protection Board (News)",
        "categorie": "Toezichthouder (EU)",
        "url": "https://www.edpb.europa.eu/feed/news_en",
        "filter_op_trefwoord": False,
    },
    {
        "naam": "European Data Protection Board (Publications)",
        "categorie": "Toezichthouder (EU)",
        "url": "https://www.edpb.europa.eu/feed/publications_en",
        "filter_op_trefwoord": False,
    },
    {
        "naam": "Nationaal Cyber Security Centrum",
        "categorie": "Expertisecentrum",
        "url": "https://feeds.ncsc.nl/nieuws.rss",
        "filter_op_trefwoord": False,
    },
    {
        "naam": "Security.nl Headlines",
        "categorie": "Nieuwswebsite",
        "url": "https://www.security.nl/rss/headlines.xml",
        "filter_op_trefwoord": True,
    },
    {
        "naam": "Kennisnet",
        "categorie": "Expertisecentrum",
        "url": "https://www.kennisnet.nl/feed/",
        "filter_op_trefwoord": False,
    },
    {
        "naam": "Privacynieuws.nl",
        "categorie": "Nieuwswebsite",
        "url": "https://privacynieuws.nl/?format=feed&type=rss",
        "filter_op_trefwoord": False,
    },
    {
        "naam": "European Data Protection Supervisor",
        "categorie": "Toezichthouder (EU)",
        "url": "https://www.edps.europa.eu/feed/news_en",
        "filter_op_trefwoord": False,
    }
]

# --- Rechtspraak.nl ------------------------------------------------------
# Open Data REST-webservice. We halen de ECLI-index op (gewijzigd sinds datum)
# en filteren daarna op trefwoorden in titel/samenvatting.
RECHTSPRAAK_ZOEK_URL = "https://data.rechtspraak.nl/uitspraken/zoeken"
RECHTSPRAAK_CONTENT_URL = "https://data.rechtspraak.nl/uitspraken/content"
# Maximaal aantal uitspraken dat we per week meenemen (na filtering).
RECHTSPRAAK_MAX_ITEMS = 8

# --- EU-jurisprudentie (HvJ-EU) via DPcuria.eu -------------------------
# DPcuria.eu is een gespecialiseerde database met uitsluitend de
# gegevensbeschermingsrechtspraak van het HvJ-EU. Stabiele links, geen
# account nodig. We lezen de lijst "Latest preliminary rulings".
DPCURIA_URL = "https://www.dpcuria.eu/"
EURLEX_MAX_ITEMS = 6
# HvJ-privacyuitspraken zijn zeldzaam; op 7 dagen filteren geeft meestal
# een lege sectie. Zet op True om altijd de laatste uitspraken te tonen,
# ongeacht datum. Zet op False voor strak filteren op DAGEN_TERUG.
EURLEX_NEGEER_DATUM = True

# --- Trefwoorden voor jurisprudentiefilter -------------------------------
# Een uitspraak telt als relevant zodra één van deze termen voorkomt in de
# titel, samenvatting of inhoudsindicatie. Kleine letters; er wordt
# hoofdletterongevoelig vergeleken.
TREFWOORDEN = [
    "avg", "gdpr", "persoonsgegevens", "privacy", "gegevensbescherming",
    "datalek", "data protection", "uavg", "verwerkingsverantwoordelijke",
    "verwerker", "bijzondere persoonsgegevens", "informatiebeveiliging", "information security",
    "autoriteit persoonsgegevens", "bewaartermijn", "nis2", "cbw",
    "inzagerecht", "recht op vergetelheid", "nis2", "informatiebeveiliging",
]

# --- Huisstijl Lumen Group ----------------------------------------------
HUISSTIJL = {
    "primair": "#d1d943",      # limegroen
    "accent": "#292347",       # donkerpaars/blauw
    "tekst": "#1f1c33",
    "tekst_zacht": "#5a5670",
    "achtergrond": "#ffffff",
    "vlak": "#f7f7f2",         # zachte tint van primair
    "lijn": "#e5e5dc",
    "kop_font": "'Fira Sans', 'Segoe UI', sans-serif",
    "tekst_font": "'Segoe UI', system-ui, sans-serif",
}

# Titel en subtitel van de nieuwsbrief.
NIEUWSBRIEF_TITEL = "[Intern] Signaal"
NIEUWSBRIEF_SUBTITEL = "Wekelijkse signalering privacy, informatiebeveiliging en jurisprudentie"
