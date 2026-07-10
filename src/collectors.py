"""
Ophalen van de vier bronnen en normaliseren naar één gemeenschappelijk formaat.

Elk item is een dict:
    {
        "bron": str,          # naam van de bron
        "categorie": str,     # groep waaronder het valt in de nieuwsbrief
        "titel": str,
        "samenvatting": str,  # korte tekst (2-3 zinnen), reeds ingekort
        "url": str,
        "datum": datetime,    # publicatie- of wijzigingsdatum (tz-aware, UTC)
    }
"""

from datetime import datetime, timedelta, timezone
import time
import html
import re
import xml.etree.ElementTree as ET

import requests
import feedparser

import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
}
TIMEOUT = 30


def _nu_utc():
    return datetime.now(timezone.utc)


def _grens():
    return _nu_utc() - timedelta(days=config.DAGEN_TERUG)


def _schoon(tekst: str, max_len: int = 320) -> str:
    """HTML strippen, whitespace normaliseren en inkorten tot ~2-3 zinnen."""
    if not tekst:
        return ""
    tekst = re.sub(r"<[^>]+>", " ", tekst)          # tags weg
    tekst = html.unescape(tekst)
    tekst = re.sub(r"\s+", " ", tekst).strip()
    if len(tekst) <= max_len:
        return tekst
    # Knip netjes af op zinseinde binnen de limiet.
    afgekapt = tekst[:max_len]
    laatste_punt = max(afgekapt.rfind(". "), afgekapt.rfind("! "), afgekapt.rfind("? "))
    if laatste_punt > 120:
        return afgekapt[: laatste_punt + 1]
    return afgekapt.rstrip() + "..."


def _bevat_trefwoord(*teksten) -> bool:
    bak = " ".join(t for t in teksten if t).lower()
    return any(tw in bak for tw in config.TREFWOORDEN)


def _struct_naar_dt(struct_time):
    if not struct_time:
        return None
    return datetime.fromtimestamp(time.mktime(struct_time), tz=timezone.utc)


# --------------------------------------------------------------------------
# 1. RSS-bronnen (AP, EDPB)
# --------------------------------------------------------------------------
def haal_rss(bron: dict) -> list:
    items = []
    grens = _grens()
    # feedparser gebruikt requests-achtige headers via agent-parameter niet
    # altijd; we halen zelf op voor betrouwbare user-agent.
    try:
        resp = requests.get(bron["url"], headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"  [waarschuwing] {bron['naam']} niet bereikbaar: {e}")
        return items

    for entry in feed.entries:
        datum = _struct_naar_dt(    
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
            or getattr(entry, "created_parsed", None)
            or getattr(entry, "expired_parsed", None)

        )
        # Fallback: gebruik huidige tijd zodat item niet verloren gaat
        if datum is None:
            datum = _nu_utc()
        if datum < grens:
            continue     
        datum = _struct_naar_dt(
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )
        if datum is None or datum < grens:
            continue
        titel = getattr(entry, "title", "").strip()
        samenvatting = _schoon(
            getattr(entry, "summary", "") or getattr(entry, "description", "")
        )
        if bron.get("filter_op_trefwoord") and not _bevat_trefwoord(titel, samenvatting):
            continue
        items.append({
            "bron": bron["naam"],
            "categorie": bron["categorie"],
            "titel": titel,
            "samenvatting": samenvatting,
            "url": getattr(entry, "link", ""),
            "datum": datum,
        })
    return items


# --------------------------------------------------------------------------
# 2. Rechtspraak.nl (NL-jurisprudentie)
# --------------------------------------------------------------------------
_ATOM = "{http://www.w3.org/2005/Atom}"


def haal_rechtspraak() -> list:
    """
    Twee stappen:
      1. ECLI-index opvragen: alle uitspraken gewijzigd sinds de grensdatum.
      2. Per ECLI de inhoudsindicatie ophalen en op trefwoord filteren.
    """
    items = []
    grens = _grens()
    modified = grens.strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "modified": modified,
        "return": "DOC",       # alleen ECLI's met een echt document
        "max": "1000",
        "sort": "DESC",
    }
    try:
        resp = requests.get(
            config.RECHTSPRAAK_ZOEK_URL, params=params, headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"  [waarschuwing] Rechtspraak.nl index niet bereikbaar: {e}")
        return items

    ecli_lijst = []
    for entry in root.findall(f"{_ATOM}entry"):
        ecli_el = entry.find(f"{_ATOM}id")
        titel_el = entry.find(f"{_ATOM}title")
        samenv_el = entry.find(f"{_ATOM}summary")
        link_el = entry.find(f"{_ATOM}link")
        if ecli_el is None:
            continue
        ecli = ecli_el.text or ""
        titel = (titel_el.text or "").strip() if titel_el is not None else ecli
        samenvatting = (samenv_el.text or "").strip() if samenv_el is not None else ""
        link = link_el.get("href") if link_el is not None else ""
        # Voorfilter op wat de index al geeft (titel + korte samenvatting).
        ecli_lijst.append((ecli, titel, samenvatting, link))

    # Filter op trefwoord met wat de index levert; dat scheelt losse calls.
    for ecli, titel, samenvatting, link in ecli_lijst:
        if not _bevat_trefwoord(titel, samenvatting):
            continue
        if not link:
            link = f"https://uitspraken.rechtspraak.nl/details?id={ecli}"
        items.append({
            "bron": "Rechtspraak.nl",
            "categorie": "Jurisprudentie (NL)",
            "titel": titel,
            "samenvatting": _schoon(samenvatting) or "Geen inhoudsindicatie beschikbaar.",
            "url": link,
            "datum": grens,   # index geeft geen exacte datum per entry mee
        })
        if len(items) >= config.RECHTSPRAAK_MAX_ITEMS:
            break
    return items


# --------------------------------------------------------------------------
# 3. EUR-Lex / HvJ-EU (EU-jurisprudentie)
# --------------------------------------------------------------------------
def haal_eurlex() -> list:
    """
    Recente EU-rechtspraak over gegevensbescherming via de publieke
    SPARQL-endpoint van Publications Office (CELLAR). Geen account nodig.
    """
    items = []
    grens = _grens().strftime("%Y-%m-%d")
    # Arresten/conclusies (sector 6 = case-law) met een datum vanaf de grens,
    # waarvan de titel een van de kernbegrippen bevat.
    query = f"""
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    SELECT DISTINCT ?work ?title ?date WHERE {{
      ?work cdm:work_date_document ?date .
      ?work cdm:work_is_about_concept_eurovoc ?eurovoc .
      ?expr cdm:expression_belongs_to_work ?work .
      ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/NLD> .
      ?expr cdm:expression_title ?title .
      FILTER(?date >= "{grens}"^^<http://www.w3.org/2001/XMLSchema#date>)
      FILTER(CONTAINS(LCASE(STR(?title)), "persoonsgegevens")
          || CONTAINS(LCASE(STR(?title)), "gegevensbescherming")
          || CONTAINS(LCASE(STR(?title)), "verordening 2016/679"))
    }} ORDER BY DESC(?date) LIMIT {config.EURLEX_MAX_ITEMS}
    """
    try:
        resp = requests.get(
            config.EURLEX_SPARQL_URL,
            params={"query": query, "format": "application/sparql-results+json"},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [waarschuwing] EUR-Lex SPARQL niet bereikbaar: {e}")
        return items

    for row in data.get("results", {}).get("bindings", []):
        titel = row.get("title", {}).get("value", "").strip()
        work = row.get("work", {}).get("value", "")
        datum_str = row.get("date", {}).get("value", "")
        try:
            datum = datetime.strptime(datum_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            datum = _grens()
        # Van work-URI een leesbare EUR-Lex-link maken.
        celex = work.rstrip("/").split("/")[-1]
        url = f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:{celex}"
        items.append({
            "bron": "HvJ-EU (via EUR-Lex)",
            "categorie": "Jurisprudentie (EU)",
            "titel": _schoon(titel, 200),
            "samenvatting": "Recente EU-uitspraak of conclusie over gegevensbescherming. Klik door voor de volledige tekst.",
            "url": url,
            "datum": datum,
        })
    return items


# --------------------------------------------------------------------------
def verzamel_alles() -> list:
    alles = []
    for bron in config.RSS_BRONNEN:
        print(f"Ophalen: {bron['naam']} ...")
        alles.extend(haal_rss(bron))
    print("Ophalen: Rechtspraak.nl ...")
    alles.extend(haal_rechtspraak())
    print("Ophalen: EUR-Lex / HvJ-EU ...")
    alles.extend(haal_eurlex())
    # Sorteer nieuwste eerst.
    alles.sort(key=lambda x: x["datum"], reverse=True)
    return alles
