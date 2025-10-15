# Zákony pro lidi - Rychlý návod

## ✅ Co bylo vytvořeno

1. **`zakonyprolidi_scraper.py`** - Kompletní scraper s API a HTML
2. **`zakonyprolidi_query.py`** - Nástroj pro dotazování databáze
3. **`zakonyprolidi.db`** - SQLite databáze s 716 dokumenty
4. **`zakonyprolidi_scraper.log`** - Log všech operací

## 📊 Stažená data

- ✅ **716 dokumentů** ze Sbírky zákonů ČR
- ✅ **281 částek** sbírky
- ✅ **Roky 1964 a 2012** (testovací data)
- ✅ **Kompletní obsah** 6 klíčových předpisů:
  - Občanský zákoník 40/1964 Sb.
  - Autorský zákon 121/2000 Sb.
  - Občanský zákoník 89/2012 Sb. (nový)
  - Zákoník práce 262/2006 Sb.
  - A další

## 🚀 Rychlý start

### 1. Zobrazit statistiky
```bash
python3 zakonyprolidi_query.py --stats
```

### 2. Vyhledat dokumenty
```bash
python3 zakonyprolidi_query.py --search "autorský"
python3 zakonyprolidi_query.py --search "práce"
python3 zakonyprolidi_query.py --search "trestní"
```

### 3. Zobrazit rok
```bash
python3 zakonyprolidi_query.py --year 1964
python3 zakonyprolidi_query.py --year 2012
```

### 4. Detail dokumentu
```bash
python3 zakonyprolidi_query.py --detail "1964-40"
python3 zakonyprolidi_query.py --detail "2012-89"
```

### 5. Interaktivní režim
```bash
python3 zakonyprolidi_query.py --interactive
```

Pak můžete psát:
```
zakonyprolidi> search občanský
zakonyprolidi> year 1964
zakonyprolidi> detail 1964-40
zakonyprolidi> stats
zakonyprolidi> quit
```

## 📥 Stažení dalších dat

### Stáhnout konkrétní rok
```bash
python3 zakonyprolidi_scraper.py --mode api --collection cs --year 2000
```

### Stáhnout rozsah let (vyžaduje partnerský klíč)
```bash
python3 zakonyprolidi_scraper.py --mode api --apikey YOUR_KEY --start-year 1918 --end-year 2024
```

### HTML Scraping (kompletní obsah všech dokumentů)
```bash
python3 zakonyprolidi_scraper.py --mode scrape --start-year 1964 --end-year 2024
```

### Kombinovaný režim
```bash
python3 zakonyprolidi_scraper.py --mode both --apikey YOUR_KEY --start-year 2000 --end-year 2024
```

## 💾 SQL dotazy

Můžete přímo dotazovat databázi:

```bash
sqlite3 zakonyprolidi.db
```

### Příklady SQL dotazů:

```sql
-- Všechny zákony z roku 1964
SELECT quote, title
FROM documents
WHERE year = 1964 AND doc_type = '4'
ORDER BY number;

-- Platné předpisy k dnešnímu dni
SELECT quote, title
FROM documents
WHERE effect_from <= date('now')
AND (effect_till IS NULL OR effect_till > date('now'));

-- Fulltextové vyhledávání
SELECT quote, title
FROM documents
WHERE title LIKE '%autorský%';

-- Top 10 nejdelších zákonů
SELECT quote, title, length(content_json) as size
FROM documents
WHERE content_json IS NOT NULL
ORDER BY size DESC
LIMIT 10;

-- Statistiky podle typu
SELECT doc_type, COUNT(*) as pocet
FROM documents
GROUP BY doc_type
ORDER BY pocet DESC;

-- Dokumenty publikované v roce 2012
SELECT COUNT(*) as pocet,
       strftime('%Y-%m', publish_date) as mesic
FROM documents
WHERE year = 2012
GROUP BY mesic;
```

## 🔑 Typy dokumentů

| Kód | Typ dokumentu |
|-----|---------------|
| 1   | Nařízení vlády |
| 2   | Vyhláška |
| 3   | Ústavní zákon |
| 4   | Zákon |
| 7   | Oznámení |
| 21  | Rozhodnutí |
| 22  | Usnesení |
| 24  | Nález |
| 25  | Opatření |
| 26  | Úplné znění |
| 30  | Redakční oznámení |
| 146 | Sdělení |

## 📚 Příklady využití v Pythonu

```python
import sqlite3
import json

# Připoj se k databázi
conn = sqlite3.connect("zakonyprolidi.db")
cursor = conn.cursor()

# Najdi všechny zákony
cursor.execute("""
    SELECT quote, title
    FROM documents
    WHERE doc_type = '4'
    ORDER BY year DESC, number
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

# Získej kompletní obsah dokumentu
cursor.execute("""
    SELECT content_json
    FROM documents
    WHERE code = '1964-40'
""")

doc = cursor.fetchone()
if doc and doc[0]:
    data = json.loads(doc[0])
    print(json.dumps(data, indent=2, ensure_ascii=False))

conn.close()
```

## 🌐 Webové rozhraní (volitelné)

Můžete vytvořit jednoduché Flask API:

```python
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/search/<keyword>')
def search(keyword):
    conn = sqlite3.connect("zakonyprolidi.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quote, title, year
        FROM documents
        WHERE title LIKE ?
    """, (f"%{keyword}%",))
    results = [dict(zip(['quote', 'title', 'year'], row))
               for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000)
```

Pak:
```bash
curl http://localhost:5000/api/search/občanský
```

## 🔒 Získání partnerského přístupu

Pro kompletní data kontaktujte:
- 📧 Email: info@zakonyprolidi.cz
- 🌐 Formulář: https://www.zakonyprolidi.cz/feedback

S partnerským klíčem můžete:
- ✅ Stáhnout všechny roky (1918-2025)
- ✅ Přístup ke všem dokumentům
- ✅ Historické i budoucí verze
- ✅ Neomezené RSS feeds

## 📖 Struktura databáze

### Tabulka: documents
Hlavní tabulka s dokumenty
```sql
CREATE TABLE documents (
    doc_id INTEGER PRIMARY KEY,
    collection TEXT,
    code TEXT,
    year INTEGER,
    number INTEGER,
    quote TEXT,
    title TEXT,
    doc_type TEXT,
    declare_date DATE,
    publish_date DATE,
    effect_from DATE,
    effect_till DATE,
    last_update TIMESTAMP,
    href TEXT,
    content_json TEXT,      -- Kompletní obsah z API
    content_html TEXT,      -- HTML obsah ze scrapingu
    scraped_at TIMESTAMP
);
```

### Tabulka: batches
Částky sbírky zákonů
```sql
CREATE TABLE batches (
    batch_id INTEGER PRIMARY KEY,
    collection TEXT,
    year INTEGER,
    number INTEGER,
    code TEXT,
    quote TEXT,
    publish_date DATE,
    href TEXT,
    file TEXT
);
```

## 🛠️ Pokročilé použití

### Export do JSON
```bash
sqlite3 zakonyprolidi.db ".mode json" ".output data.json" "SELECT * FROM documents"
```

### Export do CSV
```bash
sqlite3 zakonyprolidi.db ".mode csv" ".output data.csv" "SELECT quote, title, year FROM documents"
```

### Backup databáze
```bash
sqlite3 zakonyprolidi.db ".backup zakonyprolidi_backup.db"
```

### Vacuum (optimalizace)
```bash
sqlite3 zakonyprolidi.db "VACUUM"
```

## 📈 Monitoring stahování

Log je v souboru `zakonyprolidi_scraper.log`:

```bash
# Sleduj log v reálném čase
tail -f zakonyprolidi_scraper.log

# Najdi chyby
grep ERROR zakonyprolidi_scraper.log

# Počet stažených dokumentů
grep "Uloženo.*dokumentů" zakonyprolidi_scraper.log
```

## 💡 Tipy a triky

1. **Rychlost**: API je rychlejší než scraping
2. **Respektuj server**: Používej delay mezi požadavky
3. **Backup**: Zálohuj databázi před velkým stahováním
4. **Indexy**: Pro velké množství dat přidej další indexy
5. **Monitoring**: Sleduj log pro chyby

## 🐛 Řešení problémů

### Problem: API vrací 403
```bash
# Zkontroluj API klíč
python3 zakonyprolidi_scraper.py --apikey test --test-only
```

### Problem: Databáze je zamčená
```bash
# Uzavři všechna spojení a zkus znovu
killall python3
sqlite3 zakonyprolidi.db "PRAGMA integrity_check"
```

### Problem: Chybí Python moduly
```bash
pip3 install --user requests beautifulsoup4 lxml
```

## 📞 Podpora

- 📚 Dokumentace API: https://www.zakonyprolidi.cz/help/api.htm
- 📧 Kontakt: info@zakonyprolidi.cz
- 💬 Issues: Hlašte chyby v tomto repozitáři

## ⚖️ Licence

Data ze Zákonů pro lidi podléhají jejich licenčním podmínkám.
Pro komerční použití získejte partnerský přístup.

---

**Užívejte si lokální repliku Zákonů pro lidi! 🎉**
