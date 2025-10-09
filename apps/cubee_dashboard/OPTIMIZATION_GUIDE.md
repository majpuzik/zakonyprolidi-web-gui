# 🎯 Průvodce Optimalizačními Doporučeními - Cubee Dashboard v2.3

**Verze:** 2.3.0
**Datum:** 2025-10-09
**Status:** ✅ PRODUCTION READY

---

## 📊 Co jsou Optimalizační Doporučení?

Dashboard nyní automaticky analyzuje 24hodinové spotové ceny elektřiny a **doporučuje optimální časy** pro:
- 🔴 **NÁKUP/NABÍJENÍ** - v levných hodinách
- 🟢 **PRODEJ/VYBÍJENÍ** - v drahých hodinách

Vizualizace je inspirována oficiálním Cubee.cz dashboardem, ale používá **naši vlastní optimalizační logiku**.

---

## 🎨 Vizualizace

### Graf "Ceny elektřiny (24h)"

Dashboard zobrazuje **4 vrstvy dat**:

#### 1. ⚫ Černá Linie - Cena za Nákup
```javascript
buyPrice = OTE_spot + 0.85 (CEZ) + 0.30 (import tariff)
```
- **Typ:** Schodový graf (`shape: 'hv'`)
- **Barva:** `rgba(50, 50, 50, 1)` (černá)
- **Výplň:** Světle zelená mezi nákupem a prodejem
- **Význam:** Skutečná cena, kterou zaplatíte při nákupu elektřiny ze sítě

#### 2. 🔵 Modrá Linie - Cena za Prodej
```javascript
sellPrice = 0.55 CZK/kWh (feed-in tariff)
```
- **Typ:** Schodový graf (`shape: 'hv'`)
- **Barva:** `rgba(100, 150, 255, 1)` (modrá)
- **Výplň:** Světle modrá od nuly k prodejní ceně
- **Význam:** Kolik dostanete za prodej přebytku do sítě

#### 3. 🔴🟢 Barevné Sloupce - Naše Doporučení
```javascript
// Červená = NÁKUP (levné hodiny)
if (buyPrice < průměr * 0.85) → červený sloupec

// Zelená = PRODEJ (drahé hodiny)
if (buyPrice > průměr * 1.15) → zelený sloupec
```
- **Typ:** Sloupcový graf (`type: 'bar'`)
- **Barvy:**
  - Červená: `rgba(255, 100, 100, 0.4)` - doporučujeme nabíjení
  - Zelená: `rgba(100, 255, 100, 0.4)` - doporučujeme vybíjení
- **Průhlednost:** 50% (`opacity: 0.5`)
- **Význam:** Kdy aktivně jednat

#### 4. ⏰ Černá Přerušovaná - Aktuální Čas
```javascript
x = aktuální hodina (např. "14:00")
y = od 0 do max ceny
```
- **Typ:** Čára (`type: 'scatter'`)
- **Styl:** Přerušovaná (`dash: 'dash'`)
- **Barva:** `rgba(0, 0, 0, 0.5)` (poloprůhledná černá)
- **Význam:** Orientace v čase

---

## 🧮 Optimalizační Algoritmus

### Krok 1: Výpočet Nákupních Cen
```javascript
const buyPrices = prices.map(p => p + 0.85 + 0.30);
// p = OTE spotová cena z /api/prices
// 0.85 = CEZ distribuční poplatek
// 0.30 = import tariff
```

**Příklad:**
```
Hodina 3:00 - OTE spot: 2.43 CZK/kWh
→ buyPrice = 2.43 + 0.85 + 0.30 = 3.58 CZK/kWh ✅ LEVNÉ!
```

### Krok 2: Výpočet Průměrné Ceny
```javascript
const avgBuyPrice = buyPrices.reduce((a, b) => a + b, 0) / 24;
```

**Příklad:**
```
Denní průměr: 7.85 CZK/kWh
```

### Krok 3: Rozhodovací Logika
```javascript
for (let i = 0; i < 24; i++) {
  if (buyPrices[i] < avgBuyPrice * 0.85) {
    // Cena je < 85% průměru → LEVNÁ HODINA
    recommendations[i] = buyPrices[i];
    recommendColors[i] = 'rgba(255, 100, 100, 0.4)';  // 🔴 ČERVENÁ
    // Akce: Nabíjení baterie ze sítě
  }
  else if (buyPrices[i] > avgBuyPrice * 1.15) {
    // Cena je > 115% průměru → DRAHÁ HODINA
    recommendations[i] = buyPrices[i];
    recommendColors[i] = 'rgba(100, 255, 100, 0.4)';  // 🟢 ZELENÁ
    // Akce: Vybíjení baterie, použití uložené energie
  }
  else {
    // Normální cena → bez doporučení
    recommendations[i] = null;
    recommendColors[i] = 'rgba(0,0,0,0)';  // Průhledná
  }
}
```

### Prahy Rozhodování

| Cena vs Průměr | Akce | Barva | Strategie |
|----------------|------|-------|-----------|
| < 85% průměru | 🔴 NÁKUP | Červená | Nabíjet baterie, zapnout TUV |
| 85% - 115% | ⚪ MONITOROVAT | Bez označení | Přímá spotřeba ze solárů |
| > 115% průměru | 🟢 PRODEJ | Zelená | Vybíjet baterie, vypnout TUV |

**Příklad:**
```
Průměr: 7.85 CZK/kWh

Hodina 3:00 → 3.58 CZK (45% průměru) → 🔴 ČERVENÁ (nabíjení)
Hodina 10:00 → 7.20 CZK (92% průměru) → ⚪ NEUTRÁLNÍ (monitorovat)
Hodina 18:00 → 9.50 CZK (121% průměru) → 🟢 ZELENÁ (vybíjení)
```

---

## 💰 Výpočet Zisku

Dashboard počítá **dvě hodnoty zisku**:

### 1. Náš Zisk (Our Profit)
```javascript
// Při nabíjení (battery_current > 1A)
cost = battery_energy_kwh * buyPrice
our_profit = -cost  // Záporné = náklady

// Při vybíjení (battery_current < -1A)
savings = battery_energy_kwh * buyPrice
our_profit = +savings  // Kladné = úspora
```

### 2. Cubee Zisk
```javascript
cubee_profit = our_profit * 0.85
// Předpoklad: 85% efektivita Cubee systému
```

**Reálný příklad:**
```
Hodina 3:00 (levná):
- buyPrice: 3.58 CZK/kWh
- battery_current: +5.2A (nabíjení)
- battery_voltage: 230V
- energy: 5.2 × 230 / 1000 = 1.196 kWh
- cost: 1.196 × 3.58 = -4.28 CZK

Hodina 18:00 (drahá):
- buyPrice: 9.50 CZK/kWh
- battery_current: -8.0A (vybíjení)
- energy: 8.0 × 230 / 1000 = 1.84 kWh
- savings: 1.84 × 9.50 = +17.48 CZK

Celkový denní zisk: -4.28 + 17.48 = +13.20 CZK ✅
```

---

## 🔧 Technická Implementace

### Soubor: `/static/js/dashboard.js`

#### Funkce `renderChart(state, prices)`

**Hlavní logika:**
```javascript
// 1. Načti data (pokud nejsou předaná)
if (!state) state = await loadState();
if (!prices) prices = await loadPrices();

// 2. Vypočítej buy/sell ceny
const buyPrices = prices.map(p => p + 0.85 + 0.30);
const sellPrices = new Array(24).fill(0.55);

// 3. Vypočítej doporučení
const avgBuyPrice = buyPrices.reduce((a,b) => a+b, 0) / 24;
const recommendations = [];
const recommendColors = [];

for (let i = 0; i < 24; i++) {
  if (buyPrices[i] < avgBuyPrice * 0.85) {
    recommendations[i] = buyPrices[i];
    recommendColors[i] = 'rgba(255, 100, 100, 0.4)';
  } else if (buyPrices[i] > avgBuyPrice * 1.15) {
    recommendations[i] = buyPrices[i];
    recommendColors[i] = 'rgba(100, 255, 100, 0.4)';
  } else {
    recommendations[i] = null;
    recommendColors[i] = 'rgba(0,0,0,0)';
  }
}

// 4. Vytvoř trace objekty pro Plotly
const trace1 = { /* Buy price - černá */ };
const trace2 = { /* Sell price - modrá */ };
const trace3 = { /* Current time - přerušovaná */ };
const trace4 = { /* Recommendations - sloupce */ };

// 5. Vykresli graf
Plotly.newPlot("plotly-chart", [trace2, trace1, trace4, trace3], layout);
```

#### Trace 4 - Doporučení
```javascript
const trace4 = {
  x: hourLabels,              // ["0:00", "1:00", ..., "23:00"]
  y: recommendations,         // [null, null, 3.58, ..., 9.50, null]
  name: "Doporučení",
  type: "bar",                // Sloupcový graf
  marker: {
    color: recommendColors,   // Dynamické barvy
    line: { width: 0 }        // Bez ohraničení
  },
  opacity: 0.5,               // 50% průhlednost
  showlegend: true
};
```

---

## 📈 Interpretace Grafu

### Co Vidím v Dashboardu?

1. **Hodiny s červenými sloupci** (NÁKUP)
   - ✅ Výhodné časy pro nabíjení baterie
   - ✅ Zapnout TUV bojler
   - ✅ Spustit pračku/myčku
   - ✅ Aktivní import ze sítě

2. **Hodiny se zelenými sloupci** (PRODEJ)
   - ✅ Použít energii z baterie místo ze sítě
   - ✅ Vypnout zbytečné spotřebiče
   - ✅ Exportovat přebytek do sítě
   - ✅ Minimalizovat import

3. **Hodiny bez sloupců** (NEUTRÁLNÍ)
   - ⚪ Standardní provoz
   - ⚪ Přímá spotřeba ze solárů
   - ⚪ Monitorovat bez aktivních akcí

4. **Černá přerušovaná čára**
   - ⏰ Aktuální čas
   - Pomáhá orientaci "kde jsme teď"

---

## 🎯 Praktické Příklady

### Scénář 1: Ranní Nákup
```
Čas: 3:00
OTE spot: 2.43 CZK/kWh
Buy price: 3.58 CZK/kWh (< 85% průměru)
→ 🔴 ČERVENÉ DOPORUČENÍ

Akce:
✅ Nabít baterii na 90% SOC
✅ Zapnout TUV (ohřát vodu)
✅ Spustit pračku
→ Náklady: -10 CZK, ale ušetřeno později: +25 CZK
```

### Scénář 2: Večerní Prodej
```
Čas: 18:00
OTE spot: 8.70 CZK/kWh
Buy price: 9.85 CZK/kWh (> 115% průměru)
→ 🟢 ZELENÉ DOPORUČENÍ

Akce:
✅ Použít baterii (vybíjení 8A)
✅ Minimalizovat import ze sítě
✅ Vypnout TUV
→ Úspora: +18 CZK (neplatíte drahý proud)
```

### Scénář 3: Polední Neutralita
```
Čas: 12:00
OTE spot: 7.20 CZK/kWh
Buy price: 8.35 CZK/kWh (95% průměru)
PV výkon: 5.2 kW
→ ⚪ BEZ DOPORUČENÍ

Akce:
✅ Přímá spotřeba ze solárů
✅ Přebytek do baterie
⚪ Monitorovat, žádná aktivní optimalizace
```

---

## 🔄 Automatizace (v2.4+)

### Budoucí Integrace s Loxone

```javascript
// Automatická akce při červeném doporučení
if (recommendation === 'buy' && soc < 80) {
  loxone_control_switch('tuv_boiler', 1);  // Zapni TUV
  loxone_control_switch('battery_charge', 1);  // Force charge
}

// Automatická akce při zeleném doporučení
if (recommendation === 'sell' && soc > 40) {
  loxone_control_switch('tuv_boiler', 0);  // Vypni TUV
  loxone_control_switch('battery_discharge', 1);  // Force discharge
}
```

### Email Notifikace (v2.4+)

```javascript
// Denní report
outlook_send_email({
  to: 'user@example.com',
  subject: 'Cubee Optimalizace - Denní Report',
  body: `
    🔴 Levné hodiny dnes: 3:00-5:00, 13:00-14:00
    🟢 Drahé hodiny dnes: 18:00-20:00
    💰 Odhadovaná úspora: +45 CZK
  `
});
```

---

## 🧪 Testování

### Manuální Test v Konzoli
```javascript
// Otevřete http://localhost:5001
// Otevřete Developer Console (F12)

// 1. Načtěte ceny
const prices = await loadPrices();
console.log("Spotové ceny:", prices);

// 2. Vypočítejte buy prices
const buyPrices = prices.map(p => p.finalni_cena + 0.85 + 0.30);
console.log("Buy prices:", buyPrices);

// 3. Najděte průměr
const avg = buyPrices.reduce((a,b) => a+b, 0) / 24;
console.log("Průměr:", avg);

// 4. Identifikujte doporučení
buyPrices.forEach((price, i) => {
  if (price < avg * 0.85) console.log(`${i}:00 → 🔴 NÁKUP (${price})`);
  if (price > avg * 1.15) console.log(`${i}:00 → 🟢 PRODEJ (${price})`);
});
```

---

## 📊 Porovnání s Cubee.cz

| Funkce | Cubee.cz | Náš Dashboard |
|--------|----------|---------------|
| **Vizualizace** | ✅ Černá/modrá linie | ✅ Identické |
| **Aktuální čas** | ✅ Svislá čára | ✅ Přerušovaná čára |
| **Doporučení** | ✅ Červené/zelené bloky | ✅ Červené/zelené sloupce |
| **Algoritmus** | ❓ Proprietární | ✅ Open-source (85%/115%) |
| **Customizace** | ❌ Nelze upravit | ✅ Plně upravitelné |
| **Real-time data** | ✅ Solax Cloud | ✅ MCP Server (3-level fallback) |
| **Historická data** | ❌ Omezená | ✅ SQLite (30 dní) |

---

## 🔧 Ladění Algoritmu

### Úprava Prahů

Pokud chcete **agresivnější optimalizaci**:
```javascript
// V dashboard.js, změňte prahy:
if (buyPrices[i] < avgBuyPrice * 0.90) {  // Bylo 0.85 → méně červených
if (buyPrices[i] > avgBuyPrice * 1.10) {  // Bylo 1.15 → více zelených
```

### Úprava Barev

```javascript
// Červená intenzivnější
recommendColors[i] = 'rgba(255, 50, 50, 0.6)';  // Bylo 0.4

// Zelená pastelověji
recommendColors[i] = 'rgba(150, 255, 150, 0.3)';
```

---

## ✅ Checklist Funkčnosti

- [x] Graf zobrazuje 4 vrstvy (buy, sell, recommendations, time)
- [x] Schodový graf pro ceny (`shape: 'hv'`)
- [x] Červené sloupce v levných hodinách
- [x] Zelené sloupce v drahých hodinách
- [x] Aktuální čas označen přerušovanou čárou
- [x] Hover shows unified data (cena + doporučení)
- [x] Legend zobrazuje všechny 4 trace
- [x] Auto-refresh každých 60s
- [x] Responsive design

---

## 🐛 Troubleshooting

### Graf nezobrazuje doporučení
```bash
# Zkontrolujte konzoli
F12 → Console → hledejte "❌ Chyba"

# Zkontrolujte data
console.log(recommendations);
console.log(recommendColors);
```

### Doporučení jsou všechna null
```javascript
// Problém: Průměr je špatně spočítaný
const avg = buyPrices.reduce((a,b) => a+b, 0) / 24;
console.log("Průměr by měl být ~7-9 CZK:", avg);
```

### Barvy se nezobrazují
```javascript
// Zkontrolujte, že trace4 je v Plotly.newPlot
Plotly.newPlot("plotly-chart", [trace2, trace1, trace4, trace3], ...);
//                                                    ^^^^^^ MUSÍ být zde
```

---

## 📚 Další Dokumentace

- [README.md](README.md) - Hlavní dokumentace
- [CHANGELOG.md](CHANGELOG.md) - Historie verzí
- [MCP_SERVER_V5.md](MCP_SERVER_V5.md) - MCP integrace
- [TEST_REPORT.md](TEST_REPORT.md) - Test results

---

**Verze:** 2.3.0
**Autor:** M.A.J. Puzik
**Datum:** 2025-10-09
**Dashboard:** http://localhost:5001
**Status:** ✅ PRODUCTION READY

🎯 **Optimalizace zisku pomocí inteligentních doporučení!**
