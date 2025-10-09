# Changelog - Cubee Dashboard

## [2.3.0] - 2025-10-09

### 🎯 Optimalizační Doporučení
- **Inteligentní doporučení** - automatická detekce optimálních časů nákupu/prodeje
- **Vizualizace inspirovaná Cubee.cz:**
  - ⚫ Černá linie - cena za nákup (OTE + CEZ + import tariff)
  - 🔵 Modrá linie - cena za prodej (feed-in tariff)
  - 🔴 Červené sloupce - doporučení NÁKUP/nabíjení (< 85% průměru)
  - 🟢 Zelené sloupce - doporučení PRODEJ/vybíjení (> 115% průměru)
  - ⏰ Černá přerušovaná - aktuální čas
- **Schodový graf** - všechny ceny jako step chart (`shape: 'hv'`)
- **4-vrstvá vizualizace** - buy price, sell price, recommendations, current time

### 📊 Vylepšený Graf
- **Trace 1:** Cena za nákup (černá, horní) s výplní
- **Trace 2:** Cena za prodej (modrá, dolní) s výplní
- **Trace 3:** Aktuální čas (svislá přerušovaná čára)
- **Trace 4:** Naše doporučení (červené/zelené sloupce)

### 🧮 Optimalizační Algoritmus
```javascript
// Červená (NÁKUP) - když cena < 85% denního průměru
if (buyPrice < avgBuyPrice * 0.85) → recommend BUY/charge

// Zelená (PRODEJ) - když cena > 115% denního průměru
if (buyPrice > avgBuyPrice * 1.15) → recommend SELL/discharge
```

### 📝 Změny v kódu
- `static/js/dashboard.js`:
  - `renderChart()` - přidána optimalizační logika
  - `trace4` - nový bar chart pro doporučení
  - Dynamické barvy podle prahovacích hodnot
  - Pastelové barvy s 50% průhledností

### 📚 Dokumentace
- **OPTIMIZATION_GUIDE.md** - kompletní průvodce optimalizacemi:
  - Algoritmus rozhodování
  - Vizualizace a interpretace
  - Výpočet zisku
  - Praktické příklady
  - Troubleshooting
  - Porovnání s Cubee.cz

## [2.2.0] - 2025-10-09

### 🔌 MCP Server Integration
- **MCP Client** - připojení k MCP serveru na 192.168.10.35:5002
- **71 nástrojů** dostupných (Solax, OTE, Cubee, Loxone, Gmail, ...)
- **3-úrovňový fallback:**
  1. MCP Server (priorita)
  2. Solax Cloud API (fallback)
  3. Mock data (ultimate fallback)
- **Auto-detekce** - automaticky detekuje dostupnost MCP serveru
- **Error handling** - logování a graceful degradace
- **Cache 120s** - MCP server cachuje Solax data

### 📝 Změny v kódu
- `solax_client.py` - přidána MCP integrace
- `_get_mcp_data()` - volání MCP serveru
- `_parse_mcp_response()` - parsing MCP dat
- Environment vars: `MCP_SERVER_HOST`, `MCP_SERVER_PORT`, `USE_MCP`

### 📚 Dokumentace
- `MCP_INTEGRATION.md` - kompletní MCP guide
- Příklady použití všech 71 MCP nástrojů
- Troubleshooting a fallback strategie

## [2.1.0] - 2025-10-09

### 🔌 Solax Cloud Integration
- **SolaxClient** - připojení k Solax Cloud API
- **Fallback mock data** - lokální JSON soubor (solax_state.json)
- **Battery current tracking** - přesný výpočet z proudu (A)
- **Energy calculation** - E = I × V × t / 1000
- **Profit from current flow:**
  - Kladný proud (>1A) = nabíjení → náklady
  - Záporný proud (<-1A) = vybíjení → úspora
- **Optional web scraping** - BeautifulSoup pro cbee.cz
- **Real-time import/export** - ze Solax dat
- **SolaxPriceClient wrapper** - kombinuje Solax + OTE ceny

### 📝 Změny v kódu
- `solax_client.py` - nový modul (255 řádků)
- `main.py` - updated pro Solax integraci
- `compute_metrics()` - výpočet z battery current
- Environment vars: `SOLAX_BASE_URL`, `SOLAX_TOKEN`

### 🔧 API Changes
- `get_state()` vrací: `battery_current` (A), `battery_voltage` (V)
- `metrics` vrací: `battery_current_a`, `battery_energy_kwh`

## [2.0.0] - 2025-10-09

### ✨ Přidáno
- **Přesný výpočet zisku** s reálnými spotovými cenami (Bezdodavatele + CEZ)
- **Historie metrik** uložená v SQLite databázi
- **Trend graf** denních zisků (30 dní)
- **Skutečné spotové poplatky:**
  - CEZ distribuční poplatek: 0.85 CZK/kWh
  - Import tariff: 0.30 CZK/kWh
  - Export tariff (feed-in): 0.55 CZK/kWh
- **Omezení 50A jističe** (11.5 kW max)
- **Docker deployment** s Dockerfile a multi-stage build
- **Deployment config** pro Render.com a Fly.io
- **Health check** endpoint
- **Database migrations** automaticky při startu
- **Gunicorn** pro production

### 🔧 Vylepšeno
- Přepracovaný výpočet zisku na základě skutečných import/export dat
- Cachování OTE cenových dat
- Lepší error handling s fallback mechanismy
- Separované metriky pro naši strategii vs Cubee
- Automatické ukládání denních metrik
- Responsive design s lepšími grafy

### 📊 Nové metriky
- `ote_price_avg` - průměrná spotová cena
- `our_profit` - náš čistý zisk
- `cubee_profit` - Cubee zisk
- `total_import_kwh` - celkový import ze sítě
- `total_export_kwh` - celkový export do sítě
- `total_consumption_kwh` - celková spotřeba

### 🚀 Deployment
- Dockerfile s production-ready setup
- render.yaml pro automatický deploy na Render.com
- fly.toml pro Fly.io edge deployment
- Volume mounting pro perzistentní databázi
- Environment variables konfigurace

### 📝 Dokumentace
- README_DEPLOYMENT.md s deployment instrukcemi
- Příklady pro Docker, Render, Fly.io
- Troubleshooting guide
- Security best practices

## [1.0.0] - 2025-10-09 (Initial)

### Původní verze
- Základní dashboard s Flask backendem
- Real-time zobrazení stavu baterie
- Graf plán vs skutečná spotřeba
- Passive/Active režimy
- Export do CSV a PNG
- OTE price integration

---

## Migration Guide

### Z 1.0 na 2.0

**Breaking changes:**
- Nová databázová struktura (SQLite)
- Změna API endpointů (`/api/strategy` místo pouze state)
- Nové environment variables

**Postup upgradu:**
1. Záložujte stará data (pokud máte)
2. Stáhněte novou verzi
3. Nastavte nové env vars (viz README_DEPLOYMENT.md)
4. Spusťte - databáze se vytvoří automaticky
5. Ověřte funkčnost na `/api/state`

**Nové dependencies:**
- gunicorn==21.2.0 (pro production)

---

**Autor:** M.A.J. Puzik
**Repository:** /Users/m.a.j.puzik/apps/cubee_dashboard/
