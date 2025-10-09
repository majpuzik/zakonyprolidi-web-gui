# Changelog - Cubee Self-Consumption Optimizer

## [2.0.0] - 2025-10-08

### 🎉 Přidáno
- **Konfigurace**: Centrální `CONFIG` slovník pro všechny parametry (kapacita baterie, účinnost, limity SOC, transakční náklady)
- **Datové struktury**:
  - `PriceInfo` dataclass pro cenová data
  - `Action` dataclass pro optimalizační akce
- **Cachování**: `RealPriceProvider` s `lru_cache` pro efektivní práci s 24h cenovými daty
- **Error handling**: Graceful fallback při selhání API (použití výchozích cen)
- **Type hints**: Kompletní anotace typů pro lepší IDE support a bezpečnost
- **Dokumentace**: Docstringy pro všechny třídy a metody

### 🔧 Vylepšeno
- **Logování**: Strukturované logování s jednotným formátem
- **Rozhodovací logika**: Oddělená čistá funkce `_decide_optimal_action` bez side-effectů
- **Persistence**: Použití `pathlib.Path` místo string manipulace s cestami
- **Kódový styl**: PEP-8 compliant, konzistentní pojmenování
- **Testovatelnost**: Oddělená business logika od I/O operací

### 📝 Změněno
- Přejmenování: `cubee_self_consumption_optimizer.py` → `cubee_self_consumption_optimizer_v2.py`
- Report nyní obsahuje informaci o verzi
- `get_24h_prices()` vrací List[PriceInfo] místo List[Dict]
- `_decide_optimal_action()` vrací `Action` objekt místo dictu

### 🐛 Opraveno
- Potenciální crash při nedostupnosti API (nyní fallback na výchozí ceny)
- Hard-coded cesty v kódu
- Opakované volání API pro stejná data

## [1.0.0] - 2025-09-28

### Původní verze
- Základní analýza arbitráže vs self-consumption
- Rozhodovací logika pro optimalizaci baterie
- Generování denního reportu
- 5 prioritních akcí (store solar, negative price, high price discharge, charge before peak, direct consumption)

---

## Migrace z v1.0 na v2.0

### Kompatibilita
- V2.0 je **zpětně kompatibilní** v tom, že výstupní report má stejný formát
- API se změnilo (dataclassy místo dictů), ale `main()` funkce funguje stejně

### Postup upgrade
1. Nainstalujte v2.0 vedle v1.0:
   ```bash
   cp cubee_self_consumption_optimizer.py cubee_self_consumption_optimizer_v1_backup.py
   # nebo použijte v2 jako nový soubor
   ```

2. Přizpůsobte konfiguraci v `CONFIG` slovníku podle vašich potřeb

3. Spusťte v2.0:
   ```bash
   python3 cubee_self_consumption_optimizer_v2.py
   ```

4. Porovnejte výstupy obou verzí

### Breaking changes
- Pokud importujete třídu `SelfConsumptionOptimizer` do jiného kódu:
  - `_decide_optimal_action()` nyní vrací `Action` objekt
  - `get_24h_prices()` vrací `List[PriceInfo]`
  - Constructor nyní přijímá `price_provider` jako argument

---

## Plánované vylepšení (v2.1+)

- [ ] CLI interface (argparse) pro různé módy (demo, live, dry-run)
- [ ] Persistence stavu SOC mezi restarty
- [ ] HTTP API endpoint (FastAPI) pro integraci s Home Assistant
- [ ] Unit testy pro rozhodovací logiku
- [ ] Grafické vizualizace optimalizačních rozhodnutí
- [ ] WebSocket pro real-time monitoring
- [ ] Integrace s MQTT pro IoT komunikaci
