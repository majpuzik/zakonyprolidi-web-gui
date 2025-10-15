#!/usr/bin/env python3
"""
Zákony pro lidi - Query Tool
=============================

Jednoduché rozhraní pro dotazování lokální databáze.
"""

import sqlite3
import json
import sys
from datetime import datetime


class ZakonyQuery:
    """Dotazovací nástroj pro databázi"""

    def __init__(self, db_path="zakonyprolidi.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def search_by_title(self, keyword: str):
        """Vyhledá dokumenty podle názvu"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT quote, title, year, doc_type
            FROM documents
            WHERE title LIKE ?
            ORDER BY year DESC, number
        """, (f"%{keyword}%",))

        results = cursor.fetchall()
        print(f"\n🔍 Nalezeno {len(results)} dokumentů obsahujících '{keyword}':\n")
        print("-" * 100)

        for row in results:
            print(f"{row['quote']:15} | {row['year']} | {row['title'][:70]}")

        return results

    def list_by_year(self, year: int, doc_type: str = None):
        """Zobrazí dokumenty z daného roku"""
        cursor = self.conn.cursor()

        if doc_type:
            cursor.execute("""
                SELECT quote, title, doc_type
                FROM documents
                WHERE year = ? AND doc_type = ?
                ORDER BY number
            """, (year, doc_type))
        else:
            cursor.execute("""
                SELECT quote, title, doc_type
                FROM documents
                WHERE year = ?
                ORDER BY number
            """, (year,))

        results = cursor.fetchall()
        print(f"\n📅 Dokumenty z roku {year}" + (f" (typ: {doc_type})" if doc_type else "") + f": {len(results)}\n")
        print("-" * 100)

        for row in results:
            print(f"{row['quote']:15} | {row['title'][:70]}")

        return results

    def get_document_detail(self, code: str):
        """Zobrazí detail dokumentu"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM documents
            WHERE code = ?
        """, (code,))

        doc = cursor.fetchone()
        if not doc:
            print(f"❌ Dokument {code} nebyl nalezen")
            return None

        print("\n" + "=" * 100)
        print(f"📄 {doc['quote']}")
        print("=" * 100)
        print(f"Název:         {doc['title']}")
        print(f"Typ:           {doc['doc_type']}")
        print(f"Rok:           {doc['year']}")
        print(f"Vyhlášen:      {doc['publish_date']}")
        print(f"Účinnost od:   {doc['effect_from']}")
        print(f"Účinnost do:   {doc['effect_till'] or '(stále platný)'}")
        print(f"Aktualizace:   {doc['last_update']}")
        print(f"URL:           https://www.zakonyprolidi.cz{doc['href']}")

        if doc['content_json']:
            content = json.loads(doc['content_json'])
            print(f"\n✅ Kompletní obsah stažen (JSON: {len(doc['content_json'])} bajtů)")

            if 'Fragments' in content:
                fragments = content['Fragments']
                if isinstance(fragments, list) and len(fragments) > 0:
                    print(f"   Fragmentů: {len(fragments)}")
                    print(f"\n--- Náhled obsahu (prvních 10 fragmentů) ---")
                    for i, frag in enumerate(fragments[:10]):
                        if frag.get('Content'):
                            content_text = frag['Content'][:100]
                            print(f"   [{i+1}] {content_text}")
        else:
            print(f"\n⚠️  Kompletní obsah nebyl stažen")

        print("=" * 100 + "\n")
        return doc

    def statistics(self):
        """Zobrazí statistiky databáze"""
        cursor = self.conn.cursor()

        print("\n" + "=" * 60)
        print("📊 STATISTIKY DATABÁZE")
        print("=" * 60)

        # Celkový počet dokumentů
        cursor.execute("SELECT COUNT(*) as cnt FROM documents")
        print(f"Celkem dokumentů: {cursor.fetchone()['cnt']}")

        # Roky
        cursor.execute("SELECT MIN(year) as min_year, MAX(year) as max_year FROM documents")
        row = cursor.fetchone()
        print(f"Roky: {row['min_year']} - {row['max_year']}")

        # Podle typu
        print("\nPočet podle typu dokumentu:")
        cursor.execute("""
            SELECT doc_type, COUNT(*) as cnt
            FROM documents
            GROUP BY doc_type
            ORDER BY cnt DESC
            LIMIT 15
        """)
        for row in cursor.fetchall():
            doc_type = row['doc_type'] or '(neznámý)'
            print(f"  {doc_type:20} {row['cnt']:5}")

        # Podle roku
        print("\nPočet podle roku (top 10):")
        cursor.execute("""
            SELECT year, COUNT(*) as cnt
            FROM documents
            GROUP BY year
            ORDER BY cnt DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['year']:6} {row['cnt']:5}")

        # S obsahem
        cursor.execute("SELECT COUNT(*) as cnt FROM documents WHERE content_json IS NOT NULL")
        with_content = cursor.fetchone()['cnt']
        print(f"\nS kompletním obsahem: {with_content}")

        # Částky
        cursor.execute("SELECT COUNT(*) as cnt FROM batches")
        print(f"Částek sbírky: {cursor.fetchone()['cnt']}")

        print("=" * 60 + "\n")

    def interactive(self):
        """Interaktivní režim"""
        print("\n" + "=" * 60)
        print("🔍 ZÁKONY PRO LIDI - INTERAKTIVNÍ PROHLÍŽEČ")
        print("=" * 60)
        print("\nPříkazy:")
        print("  search <klíčové slovo>  - Vyhledávání v názvech")
        print("  year <rok>              - Dokumenty z roku")
        print("  detail <kód>            - Detail dokumentu (např. 1964-40)")
        print("  stats                   - Statistiky")
        print("  quit                    - Konec")
        print("\n")

        while True:
            try:
                cmd = input("zakonyprolidi> ").strip()

                if not cmd:
                    continue

                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()

                if action in ('quit', 'exit', 'q'):
                    print("👋 Na shledanou!")
                    break

                elif action == 'search' and len(parts) > 1:
                    self.search_by_title(parts[1])

                elif action == 'year' and len(parts) > 1:
                    try:
                        year = int(parts[1])
                        self.list_by_year(year)
                    except ValueError:
                        print("❌ Neplatný rok")

                elif action == 'detail' and len(parts) > 1:
                    self.get_document_detail(parts[1])

                elif action == 'stats':
                    self.statistics()

                elif action == 'help':
                    print("\nPříkazy:")
                    print("  search <klíčové slovo>")
                    print("  year <rok>")
                    print("  detail <kód>")
                    print("  stats")
                    print("  quit")

                else:
                    print("❌ Neznámý příkaz. Zkuste 'help'")

            except KeyboardInterrupt:
                print("\n👋 Na shledanou!")
                break
            except Exception as e:
                print(f"❌ Chyba: {e}")

    def close(self):
        """Uzavře spojení"""
        if self.conn:
            self.conn.close()


def main():
    """Hlavní funkce"""
    import argparse

    parser = argparse.ArgumentParser(description='Query nástroj pro Zákony pro lidi')
    parser.add_argument('--db', default='zakonyprolidi.db', help='Cesta k databázi')
    parser.add_argument('--search', help='Vyhledat v názvech')
    parser.add_argument('--year', type=int, help='Zobrazit rok')
    parser.add_argument('--detail', help='Detail dokumentu')
    parser.add_argument('--stats', action='store_true', help='Statistiky')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interaktivní režim')

    args = parser.parse_args()

    query = ZakonyQuery(args.db)

    try:
        if args.interactive:
            query.interactive()
        elif args.search:
            query.search_by_title(args.search)
        elif args.year:
            query.list_by_year(args.year)
        elif args.detail:
            query.get_document_detail(args.detail)
        elif args.stats:
            query.statistics()
        else:
            # Výchozí: zobraz statistiky
            query.statistics()
            print("💡 Tip: Pro interaktivní režim použijte --interactive")

    finally:
        query.close()


if __name__ == "__main__":
    main()
