# 🏛️ Zákony pro lidi - Web GUI s AI asistentem

> Moderní webové rozhraní pro procházení, vyhledávání a stahování české legislativy s integrovaným AI asistentem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)](https://flask.palletsprojects.com/)

## 📋 Obsah

- [O projektu](#-o-projektu)
- [Funkce](#-funkce)
- [Rychlý start](#-rychlý-start)
- [Instalace](#-instalace)
- [Použití](#-použití)
- [API dokumentace](#-api-dokumentace)
- [Testování](#-testování)
- [Deployment](#-deployment)
- [Příspěvky](#-příspěvky)
- [Licence](#-licence)

## 🎯 O projektu

**Zákony pro lidi - Web GUI** je komplexní aplikace pro práci s českou legislativou. Umožňuje:

- **AI dotazování** na právní otázky pomocí Claude/ChatGPT
- **Inteligentní vyhledávání** v 2000+ dokumentech
- **Automatické stahování** nových zákonů a vyhlášek
- **PDF konverzi** s OCR rozpoznáváním textu
- **Automatické tagování** podle oblasti práva

### 🎬 Demo

```bash
./start_webgui.sh
# Otevři: http://localhost:5000
```

![Screenshot](docs/screenshot.png)

## ✨ Funkce

### 1. 💬 AI Asistent

Pokládejte otázky v češtině a získejte odpovědi na základě stažených zákonů:

```
Otázka: "Jaká je maximální pokuta za překročení rychlosti?"

AI odpověď:
"Podle zákona o provozu na pozemních komunikacích (č. 361/2000 Sb.)
je maximální pokuta za překročení rychlosti stanovena na 10 000 Kč
v blokovém řízení, v správním řízení až 100 000 Kč..."

📚 Zdroje: 361/2000 Sb., 250/2016 Sb.
```

**Podporované AI modely:**
- ✅ Anthropic Claude 3.5 Sonnet (doporučeno)
- ✅ OpenAI GPT-4

### 2. 🔍 Inteligentní vyhledávání

- Fulltextové vyhledávání v názvech a obsahu
- Zobrazení tagů a metadat
- Rychlý přístup k detailu dokumentu

```python
# Příklad API volání
POST /api/search
{
  "query": "občanský zákoník",
  "limit": 10
}
```

### 3. 📥 Automatické stahování

Download manager s pokročilými filtry:

- **Datum od-do**: Stáhni dokumenty z období
- **Stáří**: Poslední N dní
- **Typ**: Zákon, vyhláška, nařízení vlády...
- **Rok**: Konkrétní rok
- **Max dokumentů**: Limit na batch
- **Pauza**: Respektování rate limits

**Co se stáhne:**
- ✅ PDF dokument
- ✅ OCR text (český)
- ✅ Všechny přílohy (PDF, DOC, XLS)
- ✅ Automatické tagy
- ✅ Metadata

### 4. 🏷️ Automatické tagování

Dokumenty jsou automaticky kategorizovány:

```python
Oblasti práva:
- trestní právo
- občanské právo
- daňové právo
- pracovní právo
- stavební právo
- dopravní právo

Typy:
- zákon
- vyhláška
- nařízení vlády

Aktualita:
- nové (2020+)
- platné (2000-2019)
- historické (<2000)
```

### 5. 📊 Real-time monitoring

- Live progress bar při stahování
- Aktuální stav každou sekundu
- Počet stažených/chybných
- Odhad zbývajícího času

## 🚀 Rychlý start

### Předpoklady

- Python 3.8+
- pip
- (Volitelně) Tesseract OCR pro optické rozpoznávání

### 1. Instalace

```bash
# Klonuj repozitář
git clone https://github.com/your-username/zakonyprolidi-web-gui.git
cd zakonyprolidi-web-gui

# Nainstaluj závislosti
pip3 install -r requirements.txt

# (Volitelně) Nastav AI klíč
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### 2. Stažení dat

```bash
# Stáhni testovací data
python3 zakonyprolidi_scraper.py --test-only

# NEBO stáhni konkrétní roky
python3 zakonyprolidi_scraper.py --years 2024 2025
```

### 3. Spuštění

```bash
# Spusť web server
./start_webgui.sh

# Otevři prohlížeč
open http://localhost:5000
```

## 📦 Instalace

### Základní instalace

```bash
pip3 install --user -r requirements.txt
```

**requirements.txt:**
```
Flask>=3.1.1
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
anthropic>=0.18.0
openai>=1.12.0
reportlab>=4.0.0
pytesseract>=0.3.10
pdf2image>=1.16.3
```

### OCR podpora (volitelné)

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-ces poppler-utils
```

**Windows:**
- Stáhni Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Přidej do PATH

### AI API klíče (doporučeno)

**Anthropic Claude:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**OpenAI ChatGPT:**
```bash
export OPENAI_API_KEY="sk-..."
```

Získání klíčů:
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

## 🎓 Použití

### CLI - Scraper

```bash
# Test API přístupu
python3 zakonyprolidi_scraper.py --test-only

# Stáhni konkrétní roky
python3 zakonyprolidi_scraper.py --years 2024 2025

# Stáhni poslední měsíc
python3 zakonyprolidi_scraper.py --days 30

# Použij HTML scraping místo API
python3 zakonyprolidi_scraper.py --mode scrape --years 2024

# Pokračuj v přerušeném stahování
python3 zakonyprolidi_scraper.py --resume
```

### CLI - Query tool

```bash
# Interaktivní režim
python3 zakonyprolidi_query.py

# Vyhledávání
python3 zakonyprolidi_query.py --search "občanský zákoník"

# Dokumenty z roku
python3 zakonyprolidi_query.py --year 2024

# Detail dokumentu
python3 zakonyprolidi_query.py --detail "89/2012"
```

### Web GUI

```bash
# Základní spuštění
python3 zakonyprolidi_web.py

# S vlastním portem
python3 zakonyprolidi_web.py --port 8080

# S AI klíčem
export ANTHROPIC_API_KEY="..."
python3 zakonyprolidi_web.py
```

### Použití jako Python knihovna

```python
from zakonyprolidi_web import AIQueryEngine, DocumentIndexer

# AI dotazy
ai = AIQueryEngine(provider='anthropic')
docs = ai.search_documents('trestní právo', limit=5)
answer = ai.ask_ai('Jaká je pokuta za krádež?', docs)

# Indexování
indexer = DocumentIndexer()
tags = indexer.auto_tag_document({
    'title': 'Zákon o daních z příjmů',
    'content': '...'
})
print(tags)  # ['daňové právo', 'zákon', 'nové']
```

## 📡 API dokumentace

### REST API Endpoints

#### `GET /`
Hlavní stránka (HTML)

#### `GET /api/stats`
Statistiky databáze

**Response:**
```json
{
  "total_documents": 2006,
  "tagged_documents": 716,
  "pdfs_downloaded": 3,
  "ocr_completed": 0
}
```

#### `POST /api/search`
Vyhledávání v dokumentech

**Request:**
```json
{
  "query": "autorské právo",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "121/2000",
      "title": "Zákon o právu autorském",
      "year": 2000,
      "type": "Zákon",
      "tags": ["občanské právo", "zákon"]
    }
  ]
}
```

#### `POST /api/ask`
AI dotaz (vyžaduje API klíč)

**Request:**
```json
{
  "question": "Jaká je maximální pokuta za krádež?"
}
```

**Response:**
```json
{
  "answer": "Podle trestního zákoníku...",
  "sources": ["40/2009 Sb."],
  "context_docs": [...]
}
```

#### `POST /api/download/start`
Spuštění stahování

**Request:**
```json
{
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "doc_type": "Zákon",
  "max_documents": 50,
  "pause_seconds": 3
}
```

#### `GET /api/download/status`
Stav stahování

**Response:**
```json
{
  "running": true,
  "current": "2025-412",
  "downloaded": 75,
  "total": 100,
  "errors": 0
}
```

#### `POST /api/download/stop`
Zastavení stahování

## 🧪 Testování

### Automatické testy

```bash
# Spusť všechny testy
python3 test_webgui.py

# Unit testy
python3 -m pytest tests/

# Coverage
python3 -m pytest --cov=. tests/
```

### Test report

Poslední test report: **100% úspěšnost** ✅

```
Testy provedeno:      6
Testy úspěšné:        6
Testy selhaly:        0
Úspěšnost:            100%

✅ Flask web server
✅ Databázové dotazy
✅ Vyhledávání dokumentů
✅ Stahování PDF (3/3)
✅ Automatické tagování (3/3)
✅ Kontrola duplikátů (4/4)
```

Detaily: [TEST_REPORT.md](TEST_REPORT.md)

## 🚢 Deployment

### Lokální (Development)

```bash
./start_webgui.sh
```

### Produkce (Gunicorn)

```bash
# Nainstaluj Gunicorn
pip3 install gunicorn

# Spusť s 4 workery
gunicorn -w 4 -b 0.0.0.0:5000 zakonyprolidi_web:app

# S timeout
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 zakonyprolidi_web:app
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "zakonyprolidi_web:app"]
```

```bash
# Build
docker build -t zakonyprolidi-web .

# Run
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -v $(pwd)/zakonyprolidi.db:/app/zakonyprolidi.db \
  zakonyprolidi-web
```

### NGINX Reverse Proxy

```nginx
server {
    listen 80;
    server_name zakony.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📁 Struktura projektu

```
zakonyprolidi-web-gui/
├── zakonyprolidi_scraper.py       # Scraper (659 řádků)
├── zakonyprolidi_web.py           # Flask backend (20 KB)
├── zakonyprolidi_query.py         # CLI query tool
├── templates/
│   └── index.html                 # Web GUI (23 KB)
├── pdfs/                          # Stažené PDF
├── ocr_texts/                     # OCR výstupy
├── attachments/                   # Přílohy
├── zakonyprolidi.db              # SQLite databáze
├── requirements.txt               # Python závislosti
├── start_webgui.sh               # Spouštěcí skript
├── test_webgui.py                # Testy
├── README.md                      # Tento soubor
├── TEST_REPORT.md                # Test report
├── WEBGUI_NAVOD.md               # Uživatelská příručka
└── WEBGUI_HOTOVO.md              # Kompletní dokumentace

docs/
├── screenshot.png
├── api.md
└── deployment.md
```

## 🛠️ Technologie

### Backend
- **Flask 3.1.1** - Web framework
- **SQLite** - Databáze (2006+ dokumentů)
- **Anthropic API** - Claude 3.5 Sonnet
- **OpenAI API** - GPT-4
- **BeautifulSoup** - HTML parsing
- **ReportLab** - PDF generování
- **Pytesseract** - OCR

### Frontend
- **Vanilla JavaScript** - Žádné frameworky
- **CSS Grid & Flexbox** - Moderní layout
- **Fetch API** - AJAX komunikace
- **Real-time updates** - setInterval polling

### Database Schema

```sql
CREATE TABLE documents (
    doc_id INTEGER PRIMARY KEY,
    collection TEXT,
    code TEXT UNIQUE,
    year INTEGER,
    number INTEGER,
    quote TEXT,
    title TEXT,
    doc_type TEXT,
    declare_date TEXT,
    publish_date TEXT,
    effect_from TEXT,
    effect_till TEXT,
    content_json TEXT,
    content_html TEXT,
    tags TEXT
);

CREATE INDEX idx_documents_year ON documents(year);
CREATE INDEX idx_documents_type ON documents(doc_type);
CREATE INDEX idx_documents_tags ON documents(tags);
```

## 📊 Výkon

| Operace | Čas |
|---------|-----|
| Vyhledávání | <100ms |
| AI odpověď | 2-5s |
| Stažení 1 dokumentu | 3-5s |
| Stažení 100 dokumentů | 5-10 min |
| PDF konverze | 1-2s |
| OCR | 5-10s |

## 🔐 Bezpečnost

### Kontroly
- ✅ Rate limiting (pauza mezi požadavky)
- ✅ Kontrola duplikátů
- ✅ Validace vstupů
- ✅ Error handling
- ✅ Timeout (30s)

### Privacy
- ✅ API klíče v env proměnných (ne v kódu)
- ✅ Žádné logování dotazů
- ✅ Lokální databáze
- ✅ Žádné cookies/tracking

### Best Practices
- Nastav pauzu min. 2s mezi požadavky
- Max 100-200 dokumentů na batch
- Používej HTTPS v produkci
- Pravidelně zálohuj databázi

## 🐛 Známé problémy

### Port 5000 obsazený (macOS)
**Problém:** AirPlay Receiver používá port 5000

**Řešení:**
```bash
# Použij jiný port
python3 zakonyprolidi_web.py --port 5001

# NEBO vypni AirPlay
# System Preferences → General → AirDrop & Handoff → AirPlay Receiver: Off
```

### PDF s českými znaky
**Problém:** ReportLab má problémy s diakritikou

**Řešení:**
- Použij OCR výstup místo PDF
- Nebo stáhni originál z webu

### OCR nefunguje
**Problém:** Tesseract není nainstalován

**Řešení:**
```bash
# macOS
brew install tesseract tesseract-lang

# Linux
sudo apt-get install tesseract-ocr tesseract-ocr-ces
```

## 💡 FAQ

**Q: Potřebuji API klíč?**
A: Ne, ale AI asistent funguje jen s klíčem. Vyhledávání a stahování funguje i bez něj.

**Q: Kolik to stojí?**
A: Anthropic Claude: ~$0.003/dotaz, OpenAI GPT-4: ~$0.01/dotaz

**Q: Můžu stáhnout všechny zákony?**
A: Ano, ale respektuj rate limits (pauza 2-5s). Pro komerční použití potřebuješ partnerský klíč.

**Q: Kde jsou data?**
A: V SQLite databázi `zakonyprolidi.db` + PDF/OCR soubory v `pdfs/` a `ocr_texts/`

**Q: Jak přidám vlastní tagy?**
A: Uprav funkci `auto_tag_document()` v `zakonyprolidi_web.py`

## 🔮 Roadmap

### v1.1 (Q1 2026)
- [ ] Export do CSV/JSON
- [ ] Bookmark oblíbených dokumentů
- [ ] Dark mode
- [ ] History dotazů

### v2.0 (Q2 2026)
- [ ] Multi-user support
- [ ] PostgreSQL podpora
- [ ] Elasticsearch full-text
- [ ] REST API pro mobilní app
- [ ] WebSocket real-time

### v3.0 (Q3 2026)
- [ ] Docker Compose stack
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Grafana dashboards

## 🤝 Příspěvky

Příspěvky jsou vítány! Prosím:

1. Fork repozitář
2. Vytvoř feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit změny (`git commit -m 'Add AmazingFeature'`)
4. Push do branche (`git push origin feature/AmazingFeature`)
5. Otevři Pull Request

### Development

```bash
# Naklonuj
git clone https://github.com/your-username/zakonyprolidi-web-gui.git
cd zakonyprolidi-web-gui

# Vytvoř virtualenv
python3 -m venv venv
source venv/bin/activate

# Nainstaluj dev závislosti
pip install -r requirements-dev.txt

# Spusť testy
pytest

# Formátování kódu
black .
flake8 .
```

## 📞 Podpora

- 📚 **Dokumentace**: [docs/](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/zakonyprolidi-web-gui/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/zakonyprolidi-web-gui/discussions)
- 📧 **Email**: your-email@example.com

## ⚖️ Licence

MIT License - viz [LICENSE](LICENSE)

**Důležité:**
- Data patří [Zákonům pro lidi](https://www.zakonyprolidi.cz)
- Respektuj jejich [licenční podmínky](https://www.zakonyprolidi.cz/help/api.htm)
- Komerční využití vyžaduje partnerský klíč
- AI API klíče jsou na vaši zodpovědnost

## 🙏 Poděkování

- [Zákony pro lidi](https://www.zakonyprolidi.cz) - za poskytnutí API
- [Anthropic](https://www.anthropic.com) - Claude AI
- [OpenAI](https://openai.com) - ChatGPT
- [Flask](https://flask.palletsprojects.com/) - Web framework
- Všem přispěvatelům! ❤️

## 📈 Statistiky

![GitHub stars](https://img.shields.io/github/stars/your-username/zakonyprolidi-web-gui?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/zakonyprolidi-web-gui?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/zakonyprolidi-web-gui)
![GitHub license](https://img.shields.io/github/license/your-username/zakonyprolidi-web-gui)

---

**Vytvořeno s ❤️ a Claude Code - 15. října 2025**

**Uživej si AI asistenta pro české zákony!** 🎉⚖️
