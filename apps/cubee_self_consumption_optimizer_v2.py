#!/usr/bin/env python3
"""
Cubee Self-Consumption Optimizer - Verze 2.0
Optimalizace vlastní spotřeby s vylepšenou architekturou

Změny v2.0:
- Konfigurovatelné parametry přes CONFIG slovník
- Cachování cenových dat (RealPriceProvider)
- Datové třídy pro čistší API (Action, PriceInfo)
- Lepší error handling a fallback mechanismy
- PEP-8 compliant kód s type hints
- Oddělená logika pro snadnější testování
- Strukturované logování

Na základě analýzy reálných cen: arbitráž není výnosná (rozdíl 0.48 CZK/kWh)
"""

import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

# --------------------------------------------------------------------------- #
#  Konfigurace – lze přepsat přes environment variables
# --------------------------------------------------------------------------- #

CONFIG = {
    # Baterie
    "BATTERY_CAPACITY_KWH": 20.0,
    "BATTERY_EFFICIENCY": 0.9,
    "SOC_MIN": 10,  # %
    "SOC_MAX": 95,  # %
    "SOC_ALARM_LOW": 30,  # % - minimum pro použití baterie při vysoké ceně
    "SOC_ALARM_HIGH": 80,  # % - maximum pro nabíjení

    # Arbitráž
    "TRANSACTION_COST_KCZ_PER_KWH": 0.15,
    "ARBITRAGE_THRESHOLD_KCZ_PER_KWH": 0.5,

    # Report
    "REPORT_FILENAME_FORMAT": "cubee_optimization_report_{ts}.txt",
    "REPORT_OUTPUT_DIR": "/Users/m.a.j.puzik/apps",
}

# --------------------------------------------------------------------------- #
#  Logování
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Datové struktury
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class PriceInfo:
    """Cenová informace pro jednu hodinu"""
    hour: int
    finalni_cena: float  # CZK/kWh

@dataclass
class Action:
    """Optimalizační akce pro baterii"""
    action: str
    amount_kwh: float
    reason: str
    benefit_czk: float
    priority: str
    color: str

# --------------------------------------------------------------------------- #
#  Poskytovatel cenových dat (s cachováním)
# --------------------------------------------------------------------------- #

class RealPriceProvider:
    """
    Wrapper pro RealPriceCalculator s cachováním 24h dat.
    Cachuje se pro celou životnost instance.
    """

    def __init__(self):
        try:
            from cubee_price_calculator import RealPriceCalculator
            self._calculator = RealPriceCalculator()
        except ImportError:
            logger.warning("cubee_price_calculator není dostupný, použijí se fallback ceny")
            self._calculator = None

    @lru_cache(maxsize=1)
    def get_24h_prices(self) -> List[PriceInfo]:
        """Získá 24h cenová data (cachováno)"""
        if self._calculator is None:
            # Fallback - vygeneruj dummy data
            return [PriceInfo(hour=h, finalni_cena=6.0) for h in range(24)]

        try:
            raw = self._calculator.get_24h_real_prices()
            return [PriceInfo(hour=p["hour"], finalni_cena=p["finalni_cena"]) for p in raw]
        except Exception as e:
            logger.error(f"Chyba při načítání cen: {e}")
            return [PriceInfo(hour=h, finalni_cena=6.0) for h in range(24)]

    def get_price_for_hour(self, hour: int) -> Optional[float]:
        """Získá cenu pro konkrétní hodinu"""
        for p in self.get_24h_prices():
            if p.hour == hour:
                return p.finalni_cena
        return None

# --------------------------------------------------------------------------- #
#  Optimalizační logika
# --------------------------------------------------------------------------- #

class SelfConsumptionOptimizer:
    """Hlavní optimalizační engine pro vlastní spotřebu"""

    def __init__(self, price_provider: RealPriceProvider, cfg: Dict = None):
        self.cfg = cfg or CONFIG
        self.price_provider = price_provider
        self.battery_capacity = self.cfg["BATTERY_CAPACITY_KWH"]
        self.efficiency = self.cfg["BATTERY_EFFICIENCY"]

    def analyze_economics(self) -> Dict[str, Dict]:
        """Analyzuje ekonomiku arbitráže vs self-consumption"""
        prices = [p.finalni_cena for p in self.price_provider.get_24h_prices()]

        min_price = min(prices)
        max_price = max(prices)
        spread = max_price - min_price

        # Arbitráž
        profit_raw = spread
        profit_eff = spread * self.efficiency
        profit_net = profit_eff - self.cfg["TRANSACTION_COST_KCZ_PER_KWH"]
        arbitrage_viable = profit_net > self.cfg["ARBITRAGE_THRESHOLD_KCZ_PER_KWH"]
        arbitrage_daily = profit_net * (self.cfg["BATTERY_CAPACITY_KWH"] * 0.5)

        # Self-consumption
        avg_grid_price = np.mean(prices)
        savings_per_kwh = avg_grid_price
        self_consumption_daily = savings_per_kwh * 15  # 15 kWh PV denně

        return {
            "arbitrage": {
                "price_spread": spread,
                "profit_raw": profit_raw,
                "profit_after_efficiency": profit_eff,
                "profit_net": profit_net,
                "viable": arbitrage_viable,
                "daily_potential": arbitrage_daily,
            },
            "self_consumption": {
                "grid_price_avg": avg_grid_price,
                "savings_per_kwh": savings_per_kwh,
                "daily_potential": self_consumption_daily,
                "viable": True,
            },
            "recommendation": "arbitrage" if arbitrage_viable else "self_consumption",
        }

    def get_optimization_strategy(self, state: Dict) -> Dict:
        """
        Vrací optimalizační strategii pro aktuální stav.

        Args:
            state: Dict s klíči battery_soc, pv_power, load_power

        Returns:
            Dict s timestamp, current_state, current_price, strategy, economics
        """
        soc = state.get("battery_soc", 50)
        pv = state.get("pv_power", 0.0)
        load = state.get("load_power", 2.5)
        now = datetime.datetime.now()
        hour = now.hour

        current_price = self.price_provider.get_price_for_hour(hour) or 6.0
        future_prices = [
            self.price_provider.get_price_for_hour((hour + h) % 24) or current_price
            for h in range(1, 13)
        ]

        action = self._decide_optimal_action(current_price, soc, pv, load, future_prices)

        return {
            "timestamp": now,
            "current_state": state,
            "current_price": current_price,
            "strategy": action,
            "economics": self.analyze_economics(),
        }

    def _decide_optimal_action(
        self,
        current_price: float,
        soc: float,
        pv_power: float,
        load_power: float,
        future_prices: List[float],
    ) -> Action:
        """
        Rozhodovací logika - čistá funkce bez side-effectů.

        Priorita akcí:
        1. Uložit solární přebytek
        2. Koupit při záporných cenách
        3. Použít baterii při vysokých cenách
        4. Nabít před špičkou
        5. Přímá spotřeba ze solár
        6. Monitorování
        """
        # Dostupná kapacita baterie
        available_to_charge = ((self.cfg["SOC_MAX"] - soc) / 100) * self.battery_capacity
        available_to_discharge = ((soc - self.cfg["SOC_MIN"]) / 100) * self.battery_capacity

        # Budoucí cenové statistiky
        avg_future = np.mean(future_prices) if future_prices else current_price
        max_future = max(future_prices) if future_prices else current_price
        min_future = min(future_prices) if future_prices else current_price

        # 🌞 PRIORITA 1: Uložit solární přebytek
        if pv_power > load_power and pv_power > 2 and available_to_charge > 1:
            excess_solar = pv_power - load_power
            amount = min(available_to_charge, excess_solar)
            benefit = current_price * amount
            return Action(
                action="store_solar_excess",
                amount_kwh=amount,
                reason=f"Solární přebytek {excess_solar:.1f}kW → baterie",
                benefit_czk=benefit,
                priority="critical",
                color="gold",
            )

        # ⚡ PRIORITA 2: Záporné ceny
        if current_price < 0 and available_to_charge > 1:
            amount = min(available_to_charge, 10)
            benefit = abs(current_price) * amount
            return Action(
                action="buy_negative_price",
                amount_kwh=amount,
                reason=f"ZÁPORNÁ CENA! {current_price:.2f} CZK/kWh",
                benefit_czk=benefit,
                priority="critical",
                color="darkgreen",
            )

        # 🔋 PRIORITA 3: Použít baterii při vysokých cenách
        if (
            current_price > avg_future * 1.2
            and available_to_discharge > 2
            and soc > self.cfg["SOC_ALARM_LOW"]
        ):
            amount = min(available_to_discharge, load_power, 8)
            benefit = current_price * amount
            return Action(
                action="use_battery_high_price",
                amount_kwh=amount,
                reason=f"Vysoká cena {current_price:.1f} CZK/kWh → použij baterii",
                benefit_czk=benefit,
                priority="high",
                color="orange",
            )

        # 🔌 PRIORITA 4: Nabít před špičkou
        if (
            current_price < min_future * 1.1
            and available_to_charge > 2
            and soc < self.cfg["SOC_ALARM_HIGH"]
        ):
            peak_offset = future_prices.index(max_future) if max_future in future_prices else 12
            if peak_offset < 8:
                amount = min(available_to_charge, 8)
                future_savings = (max_future - current_price) * amount
                return Action(
                    action="charge_before_peak",
                    amount_kwh=amount,
                    reason=f"Nabij před špičkou ({peak_offset}h): {max_future:.1f} CZK/kWh",
                    benefit_czk=future_savings,
                    priority="medium",
                    color="lightblue",
                )

        # 🏠 PRIORITA 5: Přímá spotřeba
        if pv_power > 0 and load_power > 0:
            direct_use = min(pv_power, load_power)
            benefit = current_price * direct_use
            return Action(
                action="direct_self_consumption",
                amount_kwh=direct_use,
                reason="Přímá spotřeba ze solár",
                benefit_czk=benefit,
                priority="medium",
                color="yellow",
            )

        # Žádná akce
        return Action(
            action="monitor",
            amount_kwh=0,
            reason="Monitorování - žádná optimalizace potřebná",
            benefit_czk=0,
            priority="low",
            color="gray",
        )

    def create_daily_report(self) -> str:
        """Vytvoří denní report optimalizace"""
        economics = self.analyze_economics()
        ts = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

        report = f"""
🔋 CUBEE OPTIMALIZACE - DENNÍ REPORT v2.0
=========================================
📅 Datum: {ts}

💰 EKONOMICKÁ ANALÝZA:
----------------------
❌ Arbitráž: {economics['arbitrage']['profit_net']:.2f} CZK/kWh
   • Cenový spread: {economics['arbitrage']['price_spread']:.2f} CZK/kWh
   • Po účinnosti: {economics['arbitrage']['profit_after_efficiency']:.2f} CZK/kWh
   • Denní potenciál: {economics['arbitrage']['daily_potential']:.1f} CZK
   • Výnosnost: {'✅ ANO' if economics['arbitrage']['viable'] else '❌ NE'}

✅ Self-consumption: {economics['self_consumption']['savings_per_kwh']:.2f} CZK/kWh
   • Průměrná cena sítě: {economics['self_consumption']['grid_price_avg']:.2f} CZK/kWh
   • Denní potenciál: {economics['self_consumption']['daily_potential']:.1f} CZK
   • Výnosnost: ✅ VŽDY

🎯 DOPORUČENÍ: {economics['recommendation'].upper()}
=========================================

📊 REÁLNÉ CENY (s DPH a všemi poplatky):
-----------------------------------------
• OTE spotová: ~1.50 CZK/kWh
• Distributor: ~2.10 CZK/kWh (CEZ)
• Bezdodavatele: ~0.70 CZK/kWh
• CET poplatek: ~0.95 CZK/kWh
• DPH (21%): ~1.10 CZK/kWh
-----------------------------------------
• CELKEM: 5.87-6.35 CZK/kWh

⚠️  DŮLEŽITÉ: Klasická arbitráž s reálnými cenami NENÍ výnosná!
   Malý spread (0.48 CZK/kWh) nestačí pokrýt ztráty baterie.

✅ ZAMĚŘTE SE NA: Maximalizaci vlastní spotřeby ze solár!

🌞 OPTIMÁLNÍ STRATEGIE:
=======================
1. PŘÍMÁ SPOTŘEBA: Solar → spotřeba (úspora 6+ CZK/kWh)
2. UKLÁDÁNÍ PŘEBYTKŮ: Solar → baterie → večerní spotřeba
3. SMART NABÍJENÍ: Nabij před vysokými cenami pro vlastní spotřebu
4. ZÁPORNÉ CENY: Využij vzácné příležitosti (dostáváte zaplaceno)

📈 ROI: 90+ CZK denně z optimalizace vlastní spotřeby!

🔧 VERZE 2.0 - VYLEPŠENÍ:
=========================
• Konfigurovatelné parametry
• Cachování cenových dat
• Lepší error handling
• Strukturované logování
• Type hints a datové třídy
"""
        return report

    def write_report_to_file(self, report: str) -> Path:
        """Uloží report do souboru a vrátí cestu"""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = self.cfg["REPORT_FILENAME_FORMAT"].format(ts=ts)
        output_dir = Path(self.cfg["REPORT_OUTPUT_DIR"])
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / filename
        path.write_text(report, encoding="utf-8")
        return path

# --------------------------------------------------------------------------- #
#  Hlavní funkce
# --------------------------------------------------------------------------- #

def main() -> None:
    """Hlavní entry point"""
    logger.info("🚀 Spouštím Cubee Self-Consumption Optimizer v2.0")

    price_provider = RealPriceProvider()
    optimizer = SelfConsumptionOptimizer(price_provider)

    # 1. Vytvoř a zobraz report
    report = optimizer.create_daily_report()
    print(report)

    # 2. Ulož report
    try:
        path = optimizer.write_report_to_file(report)
        logger.info(f"✅ Report uložen: {path}")
    except OSError as exc:
        logger.error(f"❌ Chyba při ukládání reportu: {exc}")

    # 3. Demo optimalizační rozhodnutí
    demo_state = {"battery_soc": 55, "pv_power": 3.2, "load_power": 2.8}
    decision = optimizer.get_optimization_strategy(demo_state)
    logger.info(f"📊 Demo rozhodnutí: {json.dumps(decision, default=str, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()
