# 🌐 Zákony pro lidi - Web GUI s AI - Návod k použití

## 🎯 Co umí webové rozhraní

### ✨ Hlavní funkce

1. **💬 AI Asistent**
   - Položte otázku v češtině
   - AI odpoví na základě stažených zákonů
   - Zobrazí zdroje (konkrétní zákony)
   - Podporuje Claude (Anthropic) i ChatGPT (OpenAI)

2. **🔍 Inteligentní vyhledávání**
   - Vyhledávání v názvech a obsahu
   - Zobrazení tagů a metadat
   - Rychlý přístup k detail dokumentu

3. **📥 Automatické stahování**
   - Filtrování podle data, roku, typu
   - Konverze do PDF
   - OCR (optické rozpoznání textu)
   - Stahování všech příloh
   - Kontrola duplikátů
   - Nastavitelná pauza mezi požadavky
   - Automatické tagování

---

## 🚀 Instalace

### 1. Základní závislosti

```bash
# Nainstaluj Python balíčky
pip3 install --user -r zakonyprolidi_web_requirements.txt
```

### 2. AI API klíče (volitelné ale doporučené)

**Varianta A: Anthropic Claude (doporučeno)**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**Varianta B: OpenAI ChatGPT**
```bash
export OPENAI_API_KEY="sk-..."
```

Získání klíčů:
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

### 3. OCR nástroje (volitelné)

**macOS:**
```bash
brew install tesseract tesseract-lang

# Česká jazyková data
brew install tesseract-lang
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-ces
sudo apt-get install poppler-utils  # pro pdf2image
```

**Windows:**
- Stáhni Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Přidej do PATH

---

## ▶️ Spuštění

### Základní spuštění

```bash
python3 zakonyprolidi_web.py
```

Pak otevři prohlížeč na: **http://localhost:5000**

### S vlastním API klíčem

```bash
# Nastavit proměnnou prostředí
export ANTHROPIC_API_KEY="tvůj-klíč"

# Spustit
python3 zakonyprolidi_web.py
```

### Produkční nasazení (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 zakonyprolidi_web:app
```

---

## 📖 Použití jednotlivých funkcí

### 1. 💬 AI Asistent

**Příklady otázek:**

```
"Jaká je maximální výška pokuty za překročení rychlosti?"

"Co říká občanský zákoník o odpovědnosti za škodu?"

"Jaké jsou podmínky pro založení s.r.o.?"

"Jak dlouhá je promlčecí lhůta u smluv?"

"Co je to nález ústavního soudu?"
```

**Jak to funguje:**
1. Zadej otázku v češtině
2. AI vyhledá relevantní dokumenty v databázi
3. Přečte jejich obsah
4. Odpoví s odkazy na konkrétní zákony

**Bez AI klíče:**
- Systém zobrazí relevantní dokumenty
- Nebude AI odpověď, ale můžeš si přečíst zákony sám

### 2. 🔍 Vyhledávání

**Vyhledávací dotazy:**

```
občanský zákoník
trestní řád
autorské právo
stavební zákon 2024
nařízení vlády kybernetická
```

**Filtry:**
- Zobrazí všechny nalezené dokumenty
- Kliknutím na dokument zobrazíš detail
- Tagy ukazují oblast práva

### 3. 📥 Stahování dokumentů

#### Kritéria stahování:

**📅 Podle data:**
- **Datum od/do**: Stáhni dokumenty publikované v určitém období
- **Novější než X dní**: Např. 30 = poslední měsíc

**📊 Podle typu:**
- Zákon
- Vyhláška
- Nařízení vlády
- Ústavní zákon

**🔢 Rok:**
- Zadej konkrétní rok (např. 2025)

**⚙️ Nastavení:**
- **Max dokumentů**: Kolik najednou (max 1000)
- **Pauza**: Sekundy mezi požadavky (2-5s doporučeno)

#### Příklady použití:

**Stáhnout všechny zákony z 2025:**
```
Datum od: 2025-01-01
Datum do: 2025-12-31
Typ: Zákon
Max dokumentů: 100
Pauza: 3
```

**Stáhnout nové vyhlášky za poslední měsíc:**
```
Novější než: 30
Typ: Vyhláška
Max dokumentů: 50
```

**Stáhnout všechno z konkrétního data:**
```
Datum od: 2025-01-01
Datum do: 2025-01-31
Typ: (všechny)
Max dokumentů: 200
```

#### Co se stáhne:

✅ **PDF dokument** - Celý zákon/vyhláška
✅ **OCR text** - Automatické rozpoznání textu
✅ **Přílohy** - Všechny PDF, DOC, XLS přílohy
✅ **Tagy** - Automatické kategorizace
✅ **Metadata** - Datum, typ, autor

#### Výstupní adresáře:

```
pdfs/           - PDF dokumenty
ocr_texts/      - OCR výstupy
attachments/    - Přílohy
```

---

## 🏷️ Automatické tagování

Systém automaticky přiřadí tagy podle:

**Oblast práva:**
- trestní právo
- občanské právo
- daňové právo
- pracovní právo
- stavební právo
- dopravní právo

**Typ:**
- zákon
- vyhláška
- nařízení vlády

**Aktualita:**
- nové (2020+)
- platné (2000-2019)
- historické (<2000)

**Z webu:**
- Stáhne původní tagy z zakonyprolidi.cz

---

## 📊 Monitoring stahování

Když běží stahování, zobrazí se:

```
📊 Stav stahování
Aktuální: 2025-412
━━━━━━━━━━ 75%
Staženo: 75 / 100
```

**Ovládání:**
- 🚀 **Spustit** - Začne stahovat
- ⏹️ **Zastavit** - Přeruší (můžeš pokračovat později)
- Automatická kontrola duplikátů

---

## 💡 Tipy a triky

### 1. Nejlepší AI dotazy

**✅ Dobře:**
```
"Jaká je maximální pokuta za překročení rychlosti?"
"Co musím udělat pro založení s.r.o.?"
"Jak dlouho platí řidičský průkaz?"
```

**❌ Špatně:**
```
"zákon"  (příliš obecné)
"Co je právo?"  (příliš široké)
```

### 2. Efektivní stahování

- Začni s malým počtem (10-20 dokumentů)
- Nastav pauzu alespoň 2s
- Používej konkrétní kritéria
- Kontroluj chyby

### 3. Bez AI klíče

Funguje i bez AI:
- Vyhledávání: ✅
- Stahování: ✅
- AI odpovědi: ❌ (zobrazí jen dokumenty)

### 4. Optimalizace

**Pro rychlé vyhledávání:**
```sql
CREATE INDEX idx_documents_tags ON documents(tags);
CREATE INDEX idx_documents_title_fts ON documents(title);
```

---

## 🔧 Řešení problémů

### Problem: "AI není k dispozici"

**Řešení:**
```bash
# Zkontroluj klíč
echo $ANTHROPIC_API_KEY

# Nastav správně
export ANTHROPIC_API_KEY="sk-ant-..."

# Restart serveru
python3 zakonyprolidi_web.py
```

### Problem: OCR nefunguje

**Řešení:**
```bash
# macOS
brew install tesseract tesseract-lang

# Test
tesseract --version

# V Pythonu
pip3 install --user pytesseract pdf2image
```

### Problem: "Module not found"

**Řešení:**
```bash
pip3 install --user -r zakonyprolidi_web_requirements.txt
```

### Problem: Stahování se zastavilo

**Důvody:**
- Server timeout (nastav delší pauzu)
- Špatné URL (kontroluj log)
- Plný disk (uvolni místo)

**Řešení:**
- Klikni "Spustit" znovu (přeskočí stažené)
- Zvětši pauzu na 5s
- Sníž max dokumentů

### Problem: PDF obsahuje špatné znaky

**Důvod:** Reportlab nezvládá české znaky

**Řešení:**
1. Použij OCR výstup místo PDF
2. Nebo stáhni originál z webu

---

## 📁 Struktura souborů

```
zakonyprolidi_web.py        - Flask backend
templates/index.html         - Web GUI
zakonyprolidi.db            - SQLite databáze
pdfs/                       - Stažené PDF
ocr_texts/                  - OCR výstupy
attachments/                - Přílohy
  2025-412/                 - Přílohy dokumentu
    priloha1.pdf
    priloha2.xlsx
```

---

## 🚀 Pokročilé funkce

### Custom AI model

Uprav v `zakonyprolidi_web.py`:

```python
ai_engine = AIQueryEngine(
    provider='anthropic',  # nebo 'openai'
)
```

### Vlastní tagy

```python
def auto_tag_document(doc):
    tags = []
    # Tvoje logika
    if 'kyber' in doc['title'].lower():
        tags.append('kybernetická bezpečnost')
    return tags
```

### Webhook po stažení

Přidej do `download_batch()`:

```python
# Po každém dokumentu
requests.post('http://your-webhook', json={
    'doc_code': doc_code,
    'status': 'downloaded'
})
```

---

## 📞 Podpora

- 📚 Dokumentace: `zakonyprolidi_README.md`
- 💬 Issues: GitHub issues
- 📧 Email: info@zakonyprolidi.cz (oficiální web)

---

## ⚖️ Licence a využití

- Data patří Zákonům pro lidi
- Respektuj jejich licenční podmínky
- Komerční využití = partnerský klíč
- Nastav rozumnou pauzu (2-5s)

---

**Užívej si AI asistenta pro české zákony! 🎉⚖️**
