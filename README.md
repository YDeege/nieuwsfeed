# IBP — geautomatiseerde interne nieuwsbrief

Een gratis, zelfstandige pijplijn die wekelijks privacy- en informatiebeveiligingsnieuws
verzamelt uit verschillende bronnen en er een nieuwsbrief in huisstijl van maakt.
De nieuwsbrief wordt gepubliceerd als webpagina op GitHub Pages. Geen server, geen
abonnement, geen mailkoppeling nodig.

## Wat het doet

Elke week haalt het script items op uit de afgelopen 7 dagen:

- **Autoriteit Persoonsgegevens** (nieuws-RSS)
- **European Data Protection Board** (nieuws-RSS)
- **Rechtspraak.nl** (Open Data-webservice, gefilterd op privacytrefwoorden)
- **HvJ-EU** via **DPcuria** (SPARQL-endpoint, EU-rechtspraak over gegevensbescherming)
- **Privacynieuws.nl** & **Security.nl** (nieuws-RSS)

Per item toont de nieuwsbrief een kort bericht van twee tot drie zinnen met een
link naar de bron. De opmaak volgt de huisstijl: accentkleur #292347, primaire kleur
#d1d943 en Fira Sans voor de koppen.

## Handmatig draaien

Wil je niet wachten tot maandag, ga dan naar het tabblad **Actions**, kies de workflow
*Wekelijkse nieuwsbrief* en klik op **Run workflow**. Na een minuut staat de nieuwe
editie online.

## Waar staat de nieuwsbrief?

Op `https://ydeege.github.io/nieuwsbrief/`. Deel die link intern; hij
blijft gelijk en toont altijd de laatste editie.

## Let op

GitHub pauzeert de wekelijkse planner als een repository 60 dagen geen activiteit heeft.
Eén handmatige run of een kleine commit zet hem weer aan. De publieke bronnen kunnen hun
feed-URL wijzigen; als een bron leeg blijft, controleer dan de URL in `config.py`.

De samenstelling is geautomatiseerd. Controleer een signalering altijd bij de bron
voordat je die met een klant deelt.
