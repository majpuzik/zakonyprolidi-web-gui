#!/usr/bin/env python3
"""
Postupné stahování VŠECH zákonů - realističtější přístup
=========================================================

Stahuje data po rocích a ukládá průběh, takže můžete:
- Přerušit a pokračovat později
- Sledovat progress
- Odhadnout celkový čas
"""

import sqlite3
import time
import sys
from datetime import datetime
from zakonyprolidi_scraper import ZakonyProLidiDownloader

def get_downloaded_years(db_path="zakonyprolidi.db"):
    """Vrátí seznam již stažených roků"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM documents ORDER BY year")
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        return years
    except:
        return []

def estimate_time(years_total, years_done, elapsed_time):
    """Odhadne zbývající čas"""
    if years_done == 0:
        return "neznámý"

    avg_time_per_year = elapsed_time / years_done
    years_remaining = years_total - years_done
    seconds_remaining = avg_time_per_year * years_remaining

    hours = int(seconds_remaining / 3600)
    minutes = int((seconds_remaining % 3600) / 60)

    return f"{hours}h {minutes}m"

def main():
    print("="*70)
    print("📚 POSTUPNÉ STAHOVÁNÍ VŠECH ZÁKONŮ PRO LIDI (1918-2025)")
    print("="*70)
    print("")

    # Zjisti, co už máme
    downloaded_years = get_downloaded_years()
    if downloaded_years:
        print(f"✅ Již staženo: {len(downloaded_years)} roků")
        print(f"   První: {min(downloaded_years)}, Poslední: {max(downloaded_years)}")
        print("")

    # Všechny roky, které chceme
    all_years = list(range(1918, 2026))
    remaining_years = [y for y in all_years if y not in downloaded_years]

    if not remaining_years:
        print("🎉 Všechny roky již byly staženy!")
        return

    print(f"📋 Zbývá stáhnout: {len(remaining_years)} roků")
    print(f"⏱️  Odhadovaný čas: ~{len(remaining_years) * 2} minut (API) až ~{len(remaining_years) * 60} minut (HTML)")
    print("")

    response = input("Pokračovat? (ano/ne): ")
    if response.lower() not in ['ano', 'a', 'y', 'yes']:
        print("❌ Zrušeno")
        return

    print("")
    print("🚀 Začínám stahování...")
    print("💡 Tip: Můžete kdykoliv přerušit (Ctrl+C) a pokračovat později")
    print("")

    downloader = ZakonyProLidiDownloader(apikey="test")
    start_time = time.time()
    successful = 0
    failed = []

    try:
        for i, year in enumerate(remaining_years, 1):
            print(f"\n[{i}/{len(remaining_years)}] Rok {year}...")

            try:
                # Zkus API (funguje jen pro 1964, 2012)
                count = downloader.download_year('cs', year)

                if count > 0:
                    successful += 1
                    print(f"  ✅ Staženo {count} dokumentů")
                else:
                    print(f"  ⚠️  API nedostupné pro rok {year}")
                    print(f"  💡 Pro tento rok použijte: python3 zakonyprolidi_scraper.py --mode scrape --year {year}")

                # Progress
                elapsed = time.time() - start_time
                eta = estimate_time(len(remaining_years), successful, elapsed)
                print(f"  📊 Progress: {successful}/{len(remaining_years)} | ETA: {eta}")

                # Respektuj server
                time.sleep(2)

            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"  ❌ Chyba: {e}")
                failed.append(year)

    except KeyboardInterrupt:
        print("\n\n⏸️  Přerušeno uživatelem")
        print(f"📊 Staženo {successful} roků před přerušením")
        print("💡 Pro pokračování spusťte skript znovu - přeskočí již stažené roky")
    finally:
        downloader.close()

    # Finální statistiky
    print("\n" + "="*70)
    print("📊 STATISTIKY STAHOVÁNÍ")
    print("="*70)
    print(f"Úspěšně staženo:    {successful} roků")
    print(f"Selhalo:            {len(failed)} roků")
    if failed:
        print(f"Selhané roky:       {failed}")

    elapsed = time.time() - start_time
    print(f"Celkový čas:        {int(elapsed/60)} minut")
    print("")

    downloader.show_statistics()

    print("\n💡 PRO STAŽENÍ VŠECH DAT:")
    print("   1. HTML scraping:  bash stahnout_vsechno.sh")
    print("   2. Partnerský klíč: python3 zakonyprolidi_scraper.py --apikey YOUR_KEY --start-year 1918 --end-year 2025")
    print("")

if __name__ == "__main__":
    main()
