# [Intern] Signaal — geautomatiseerde interne nieuwsbrief

Een gratis, zelfstandige pijplijn die wekelijks privacy- en informatiebeveiligingsnieuws
verzamelt uit drie bronnen en er een nieuwsbrief in [Intern]-huisstijl van maakt.
De nieuwsbrief wordt gepubliceerd als webpagina op GitHub Pages. Geen server, geen
abonnement, geen mailkoppeling nodig.

## Wat het doet

Elke week haalt het script items op uit de afgelopen 7 dagen:

- **Autoriteit Persoonsgegevens** (nieuws-RSS)
- **European Data Protection Board** (nieuws-RSS)
- **Rechtspraak.nl** (Open Data-webservice, gefilterd op privacytrefwoorden)
- **HvJ-EU** via **EUR-Lex** (SPARQL-endpoint, EU-rechtspraak over gegevensbescherming)

Per item toont de nieuwsbrief een korte signalering van twee tot drie zinnen met een
link naar de bron. De opmaak volgt de huisstijl: accentkleur #292347, primaire kleur
#d1d943 en Fira Sans voor de koppen.

## Eenmalige installatie

1. Maak een gratis GitHub-account als je dat nog niet hebt.
2. Maak een nieuwe repository, bijvoorbeeld `[intern]-signaal`. Publiek mag, dan is Pages
   sowieso gratis. Wil je hem privé, dan werkt Pages ook, mits de organisatie op een
   plan zit dat Pages voor private repos toestaat.
3. Upload de inhoud van deze map naar de repository (behoud de mappenstructuur).
4. Zet GitHub Pages aan: ga in de repository naar **Settings, Pages** en kies bij
   *Source* de optie **GitHub Actions**.
5. Klaar. De workflow draait vanaf nu automatisch elke maandagochtend.

## Handmatig draaien

Wil je niet wachten tot maandag, ga dan naar het tabblad **Actions**, kies de workflow
*Wekelijkse nieuwsbrief* en klik op **Run workflow**. Na een minuut staat de nieuwe
editie online.

## Waar staat de nieuwsbrief?

Op `https://<jouw-gebruikersnaam>.github.io/<repo-naam>/`. Deel die link intern; hij
blijft gelijk en toont altijd de laatste editie.

## Lokaal testen

```bash
pip install -r requirements.txt
python src/main.py
# open vervolgens build/index.html in je browser
```

## Aanpassen

Bijna alles staat in `src/config.py`:

- **Frequentie**: pas de `cron`-regel in `.github/workflows/nieuwsbrief.yml` aan.
  Nu staat hij op maandag 07:00 UTC.
- **Tijdvenster**: `DAGEN_TERUG` (standaard 7).
- **Trefwoorden** voor de jurisprudentiefilter: de lijst `TREFWOORDEN`.
- **Bronnen**: `RSS_BRONNEN` voor extra RSS-feeds.
- **Huisstijl**: het `HUISSTIJL`-woordenboek.

## Let op

GitHub pauzeert de wekelijkse planner als een repository 60 dagen geen activiteit heeft.
Eén handmatige run of een kleine commit zet hem weer aan. De publieke bronnen kunnen hun
feed-URL wijzigen; als een bron leeg blijft, controleer dan de URL in `config.py`.

De samenstelling is geautomatiseerd. Controleer een signalering altijd bij de bron
voordat je die met een klant deelt.
