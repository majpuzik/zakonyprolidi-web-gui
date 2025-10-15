# Zákony pro lidi - Scraper & Lokální Replika

Kompletní nástroj pro stahování dat ze [Zákonů pro lidi](https://www.zakonyprolidi.cz) a vytvoření lokální repliky v SQLite databázi.

## Funkce

- ✅ **API Client** - Plná podpora oficiálního API
- ✅ **HTML Scraper** - Stahování dat, která nejsou v API
- ✅ **SQLite Databáze** - Lokální replika s indexy
- ✅ **Metadata** - Sbírky, typy dokumentů, částky
- ✅ **Verze** - Podpora historických verzí předpisů
- ✅ **Resumable** - Možnost obnovit přerušené stahování
- ✅ **Logging** - Podrobné logování do souboru
- ✅ **Statistiky** - Přehled stažených dat

## Instalace

```bash
# Nainstaluj závislosti
pip3 install -r zakonyprolidi_requirements.txt

# Nebo ručně:
pip3 install requests beautifulsoup4 lxml
```

## Použití

### 1. Stažení testovacích dat (klíč "test")

```bash
python3 zakonyprolidi_scraper.py --test-only
```

Stáhne:
- Občanský zákoník 40/1964 Sb.
- Autorský zákon 121/2000 Sb.
- Občanský zákoník 89/2012 Sb. (nový)
- Zákoník práce 262/2006 Sb.
- A další testovací předpisy
- Registry ročníků 1964 a 2012

### 2. Stažení konkrétního roku

```bash
python3 zakonyprolidi_scraper.py --mode api --collection cs --year 1964
```

### 3. Stažení rozsahu let

```bash
python3 zakonyprolidi_scraper.py --mode api --collection cs --start-year 1964 --end-year 1970
```

### 4. HTML Scraping (pro kompletní obsah)

```bash
python3 zakonyprolidi_scraper.py --mode scrape --collection cs --start-year 1964 --end-year 2024
```

### 5. Kombinovaný režim (API + Scraping)

```bash
python3 zakonyprolidi_scraper.py --mode both --apikey YOUR_KEY --start-year 1918 --end-year 2024
```

### 6. Zobrazení statistik

```bash
python3 zakonyprolidi_scraper.py --mode stats
```

## Parametry

| Parametr | Popis | Výchozí |
|----------|-------|---------|
| `--mode` | Režim: `api`, `scrape`, `both`, `stats` | `api` |
| `--apikey` | API klíč | `test` |
| `--collection` | Kód sbírky (`cs`, `ms`) | `cs` |
| `--year` | Konkrétní rok | - |
| `--start-year` | Počáteční rok | `1964` |
| `--end-year` | Koncový rok | `2012` |
| `--db` | Cesta k databázi | `zakonyprolidi.db` |
| `--test-only` | Jen testovací data | `false` |

## Struktura databáze

### Tabulka: collections
- Sbírky zákonů (Sbírka zákonů ČR, Mezinárodní smlouvy)

### Tabulka: doc_types
- Typy dokumentů (zákon, vyhláška, nařízení vlády, atd.)

### Tabulka: documents
- Kompletní dokumenty s metadaty
- JSON obsah z API
- HTML obsah ze scrapingu
- Indexy pro rychlé vyhledávání

### Tabulka: document_versions
- Historické verze dokumentů
- Účinnost od-do

### Tabulka: batches
- Částky sbírky zákonů

## API Endpointy

Scraper používá tyto API metody:

- `CollectionList` - Seznam sbírek
- `DocTypeList` - Typy dokumentů
- `Year` - Všechny dokumenty v roce
- `YearDocList` - Seznam dokumentů v roce
- `DocData` - Kompletní obsah dokumentu
- `DocVersions` - Verze dokumentu
- `PublishList` - Publikované v období

## Příklady SQL dotazů

### Najdi všechny zákony z roku 1964
```sql
SELECT * FROM documents
WHERE year = 1964 AND doc_type = 'Zakon'
ORDER BY number;
```

### Najdi platné předpisy k dnešnímu dni
```sql
SELECT * FROM documents
WHERE effect_from <= date('now')
AND (effect_till IS NULL OR effect_till > date('now'));
```

### Fulltextové vyhledávání v názvech
```sql
SELECT quote, title FROM documents
WHERE title LIKE '%občanský%'
ORDER BY year DESC;
```

### Statistiky podle typu dokumentu
```sql
SELECT doc_type, COUNT(*) as pocet
FROM documents
GROUP BY doc_type
ORDER BY pocet DESC;
```

## Testovací přístup API

S klíčem `apikey=test` lze získat:
- ✅ Aktuální znění předpisů: 40/1964 Sb., 121/2000 Sb., 1/2011 Sb., 307/2002 Sb., 89/2012 Sb., 262/2006 Sb.
- ✅ Registry ročníků: 1964 a 2012
- ❌ Listování RSS: omezeno na -14+40 dní

## Partnerský přístup

Pro kompletní data kontaktujte:
- Email: info@zakonyprolidi.cz
- Formulář: https://www.zakonyprolidi.cz/feedback

## Logování

Veškeré aktivity jsou logovány do:
- **Konzole** - INFO a vyšší
- **zakonyprolidi_scraper.log** - Vše včetně DEBUG

## Etika scrapingu

- ✅ Respektuje `robots.txt`
- ✅ Delay mezi požadavky (1-2s)
- ✅ User-Agent identifikace
- ✅ Používá primárně API
- ✅ HTML scraping jen jako doplněk

## Licence dat

Data ze Zákonů pro lidi podléhají jejich licenčním podmínkám.
Pro komerční použití kontaktujte provozovatele.

## Podpora

- 📚 API Dokumentace: https://www.zakonyprolidi.cz/help/api.htm
- 📧 Kontakt: info@zakonyprolidi.cz
- 🐛 Issues: Ohlašte chyby v tomto repozitáři

## Autor

Vytvořeno s pomocí Claude Code

## Časté problémy

### Problem: 403 Forbidden
**Řešení**: Zkontrolujte API klíč nebo použijte `apikey=test` pro testování

### Problem: Timeout
**Řešení**: Zvyšte timeout v `requests.get(..., timeout=60)`

### Problem: Prázdná databáze
**Řešení**: Zkontrolujte log soubor pro chybové hlášky

## Roadmap

- [ ] Export do JSON/XML
- [ ] GUI rozhraní
- [ ] Automatická synchronizace
- [ ] Elasticsearch integrace
- [ ] REST API nad lokální DB
- [ ] Docker kontejner

## Příklady použití

### Python API
```python
from zakonyprolidi_scraper import ZakonyProLidiDownloader

# Vytvoř downloader
dl = ZakonyProLidiDownloader(apikey="test")

# Stáhni metadata
dl.download_metadata()

# Stáhni konkrétní rok
dl.download_year("cs", 1964)

# Zobraz statistiky
dl.show_statistics()

# Uzavři spojení
dl.close()
```

### Vlastní SQL dotazy
```python
import sqlite3

conn = sqlite3.connect("zakonyprolidi.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT quote, title
    FROM documents
    WHERE year = 1964
    ORDER BY number
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
```

---

**Happy scraping! 🚀**
