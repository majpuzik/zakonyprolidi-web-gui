#!/usr/bin/env python3
"""
Zákony pro lidi - Kompletní Scraper & Lokální Replika
======================================================

Tento nástroj stahuje data ze Zákonů pro lidi přes API i HTML scraping
a vytváří lokální repliku v SQLite databázi.

Použití:
    python zakonyprolidi_scraper.py --mode api --apikey test
    python zakonyprolidi_scraper.py --mode scrape --full
    python zakonyprolidi_scraper.py --mode both --apikey YOUR_KEY

API Dokumentace: https://www.zakonyprolidi.cz/help/api.htm
"""

import requests
import sqlite3
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# Nastavení loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zakonyprolidi_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ZakonyProLidiAPI:
    """Klient pro práci s API Zákonů pro lidi"""

    BASE_URL = "http://www.zakonyprolidi.cz/api/v1"
    WEB_URL = "https://www.zakonyprolidi.cz"

    def __init__(self, apikey: str = "test"):
        self.apikey = apikey
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ZakonyProLidi-Scraper/1.0'
        })

    def _call_api(self, method: str, params: Dict = None, format: str = "json") -> Any:
        """Zavolá API metodu a vrátí výsledek"""
        if params is None:
            params = {}
        params['apikey'] = self.apikey

        url = f"{self.BASE_URL}/data.{format}/{method}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            if format == "json":
                data = response.json()
                # API vrací data v struktuře {Version, Base, Result}
                if 'Result' in data:
                    return data['Result']
                return data
            else:  # XML
                return ET.fromstring(response.content)

        except requests.exceptions.RequestException as e:
            logger.error(f"API chyba při volání {method}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode chyba: {e}")
            return None

    def get_collections(self) -> List[Dict]:
        """Získá seznam dostupných sbírek"""
        logger.info("Stahuji seznam sbírek...")
        result = self._call_api("CollectionList")
        if result and 'Collections' in result:
            return result['Collections']
        return []

    def get_doc_types(self) -> List[Dict]:
        """Získá seznam typů dokumentů"""
        logger.info("Stahuji typy dokumentů...")
        result = self._call_api("DocTypeList")
        return result if result else []

    def get_year(self, collection: str, year: int) -> Dict:
        """Získá informace o roce včetně všech dokumentů"""
        logger.info(f"Stahuji rok {year} ze sbírky {collection}...")
        return self._call_api("Year", {
            'Collection': collection,
            'Year': year
        })

    def get_year_doc_list(self, collection: str, year: int) -> List[Dict]:
        """Získá seznam dokumentů v roce"""
        logger.info(f"Stahuji seznam dokumentů {year}/{collection}...")
        result = self._call_api("YearDocList", {
            'Collection': collection,
            'Year': year
        })
        return result if result else []

    def get_document(self, collection: str, document: str, format: str = "json") -> Dict:
        """Získá konkrétní dokument"""
        logger.info(f"Stahuji dokument {document} ze sbírky {collection}...")
        return self._call_api("DocData", {
            'Collection': collection,
            'Document': document
        }, format=format)

    def get_document_versions(self, collection: str, document: str) -> List[Dict]:
        """Získá seznam verzí dokumentu"""
        result = self._call_api("DocVersions", {
            'Collection': collection,
            'Document': document
        })
        return result if result else []

    def get_publish_list(self, collection: str, date_from: str, date_to: str) -> List[Dict]:
        """Získá seznam publikovaných dokumentů v období"""
        result = self._call_api("PublishList", {
            'Collection': collection,
            'DateFrom': date_from,
            'DateTo': date_to
        })
        return result if result else []


class ZakonyProLidiScraper:
    """Web scraper pro stahování dat z HTML stránek"""

    BASE_URL = "https://www.zakonyprolidi.cz"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ZakonyProLidi-Scraper/1.0)'
        })

    def scrape_document(self, url: str) -> Dict:
        """Stáhne a parsuje dokument z HTML"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extrakce metadat
            title = soup.find('title')
            title_text = title.text if title else ""

            # Extrakce obsahu dokumentu
            content = soup.find('div', class_='Paper')
            content_text = content.get_text(strip=True) if content else ""

            return {
                'url': url,
                'title': title_text,
                'content': content_text,
                'html': str(content) if content else ""
            }

        except Exception as e:
            logger.error(f"Chyba při scrapování {url}: {e}")
            return None

    def scrape_collection(self, collection: str, start_year: int, end_year: int) -> List[str]:
        """Stáhne odkazy na všechny dokumenty v rozmezí let"""
        documents = []

        for year in range(start_year, end_year + 1):
            url = f"{self.BASE_URL}/{collection}/rocnik/{year}"
            try:
                response = self.session.get(url, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Najdi všechny odkazy na dokumenty
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if f"/{collection}/" in href and href.count('/') == 2:
                        full_url = urljoin(self.BASE_URL, href)
                        documents.append(full_url)

                logger.info(f"Rok {year}: nalezeno {len(documents)} dokumentů")
                time.sleep(1)  # Respektujeme server

            except Exception as e:
                logger.error(f"Chyba při scrapování roku {year}: {e}")

        return list(set(documents))  # Odstraň duplikáty


class LocalDatabase:
    """Správa lokální SQLite databáze"""

    def __init__(self, db_path: str = "zakonyprolidi.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Vytvoří databázovou strukturu"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Tabulka sbírek
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                collection_id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT,
                first_year INTEGER,
                last_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabulka typů dokumentů
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doc_types (
                doc_type_id INTEGER PRIMARY KEY,
                code TEXT UNIQUE,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabulka dokumentů
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
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
                content_json TEXT,
                content_html TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(collection, code)
            )
        """)

        # Tabulka verzí dokumentů
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                version_number INTEGER,
                effect_from DATE,
                effect_till DATE,
                content_json TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
            )
        """)

        # Tabulka částek (batches)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                batch_id INTEGER PRIMARY KEY,
                collection TEXT,
                year INTEGER,
                number INTEGER,
                code TEXT,
                quote TEXT,
                publish_date DATE,
                href TEXT,
                file TEXT,
                UNIQUE(collection, year, number)
            )
        """)

        # Indexy pro rychlejší vyhledávání
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_year ON documents(year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_code ON documents(code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_effect_from ON documents(effect_from)")

        self.conn.commit()
        logger.info(f"Databáze inicializována: {self.db_path}")

    def save_collection(self, collection: Dict):
        """Uloží sbírku do databáze"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO collections (collection_id, code, name, first_year, last_year)
            VALUES (?, ?, ?, ?, ?)
        """, (
            collection.get('CollectionId'),
            collection.get('Code'),
            collection.get('Name'),
            collection.get('FirstYear'),
            collection.get('LastYear')
        ))
        self.conn.commit()

    def save_doc_type(self, doc_type: Dict):
        """Uloží typ dokumentu"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO doc_types (doc_type_id, code, name)
            VALUES (?, ?, ?)
        """, (
            doc_type.get('DocTypeId'),
            doc_type.get('Code'),
            doc_type.get('Name')
        ))
        self.conn.commit()

    def save_document(self, doc: Dict, content_json: str = None, content_html: str = None):
        """Uloží dokument do databáze"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents (
                doc_id, collection, code, year, number, quote, title, doc_type,
                declare_date, publish_date, effect_from, effect_till, last_update,
                href, content_json, content_html
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.get('DocId'),
            doc.get('Collection'),
            doc.get('Code'),
            doc.get('Year'),
            doc.get('Number'),
            doc.get('Quote'),
            doc.get('Title'),
            doc.get('DocType'),
            doc.get('DeclareDate'),
            doc.get('PublishDate'),
            doc.get('EffectFrom'),
            doc.get('EffectTill'),
            doc.get('LastUpdate'),
            doc.get('Href'),
            content_json,
            content_html
        ))
        self.conn.commit()
        return cursor.lastrowid

    def save_batch(self, batch: Dict):
        """Uloží částku do databáze"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO batches (
                batch_id, collection, year, number, code, quote, publish_date, href, file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch.get('BatchId'),
            batch.get('Collection'),
            batch.get('Year'),
            batch.get('Number'),
            batch.get('Code'),
            batch.get('Quote'),
            batch.get('PublishDate'),
            batch.get('Href'),
            batch.get('File')
        ))
        self.conn.commit()

    def get_statistics(self) -> Dict:
        """Vrátí statistiky databáze"""
        cursor = self.conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM collections")
        stats['collections'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM documents")
        stats['documents'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM doc_types")
        stats['doc_types'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM batches")
        stats['batches'] = cursor.fetchone()['count']

        cursor.execute("""
            SELECT collection, COUNT(*) as count
            FROM documents
            GROUP BY collection
        """)
        stats['by_collection'] = {row['collection']: row['count'] for row in cursor.fetchall()}

        return stats

    def close(self):
        """Zavře databázové spojení"""
        if self.conn:
            self.conn.close()


class ZakonyProLidiDownloader:
    """Hlavní třída pro stahování a správu dat"""

    def __init__(self, apikey: str = "test", db_path: str = "zakonyprolidi.db"):
        self.api = ZakonyProLidiAPI(apikey)
        self.scraper = ZakonyProLidiScraper()
        self.db = LocalDatabase(db_path)

    def download_metadata(self):
        """Stáhne metadata (sbírky, typy dokumentů)"""
        logger.info("=== Stahování metadat ===")

        # Sbírky
        collections = self.api.get_collections()
        for coll in collections:
            self.db.save_collection(coll)
            logger.info(f"  Uložena sbírka: {coll.get('Name')}")

        # Typy dokumentů
        doc_types = self.api.get_doc_types()
        if 'DocTypes' in doc_types:
            for dt in doc_types['DocTypes']:
                self.db.save_doc_type(dt)
                logger.info(f"  Uložen typ: {dt.get('Name')}")

    def download_year(self, collection: str, year: int):
        """Stáhne všechny dokumenty z daného roku"""
        logger.info(f"=== Stahování roku {year} ({collection}) ===")

        year_data = self.api.get_year(collection, year)
        if not year_data or 'Batches' not in year_data:
            logger.warning(f"⚠️  Rok {year} není dostupný s tímto API klíčem")
            logger.info(f"💡 Tip: Použijte --mode scrape pro HTML stahování")
            return 0

        batches = year_data['Batches']
        if isinstance(batches, dict):
            batches = [batches]

        doc_count = 0
        for batch in batches:
            # Ulož částku
            self.db.save_batch(batch)

            # Zpracuj dokumenty v částce
            docs = batch.get('Docs', [])
            if not docs:
                continue
            if isinstance(docs, dict):
                docs = [docs]

            for doc in docs:
                self.db.save_document(doc)
                doc_count += 1

        logger.info(f"  Uloženo {doc_count} dokumentů z roku {year}")
        return doc_count

    def download_document_content(self, collection: str, document_code: str):
        """Stáhne kompletní obsah dokumentu"""
        logger.info(f"Stahování obsahu: {document_code}")

        # Stáhni přes API
        doc_data = self.api.get_document(collection, document_code)
        if doc_data:
            content_json = json.dumps(doc_data, ensure_ascii=False, indent=2)

            # Aktualizuj v databázi
            cursor = self.db.conn.cursor()
            cursor.execute("""
                UPDATE documents
                SET content_json = ?
                WHERE collection = ? AND code = ?
            """, (content_json, collection, document_code))
            self.db.conn.commit()

    def download_collection_years(self, collection: str, start_year: int, end_year: int):
        """Stáhne všechny roky ze sbírky"""
        logger.info(f"=== Stahování sbírky {collection}: {start_year}-{end_year} ===")

        total_docs = 0
        for year in range(start_year, end_year + 1):
            try:
                count = self.download_year(collection, year)
                total_docs += count
                time.sleep(1)  # Respektuj server
            except Exception as e:
                logger.error(f"Chyba při stahování roku {year}: {e}")

        logger.info(f"Celkem staženo {total_docs} dokumentů")
        return total_docs

    def download_all_test_data(self):
        """Stáhne všechna testovací data dostupná s klíčem 'test'"""
        logger.info("=== Stahování všech testovacích dat ===")

        # Metadata
        self.download_metadata()

        # Testovací předpisy podle dokumentace:
        # 40/1964 Sb., 121/2000 Sb., 1/2011 Sb., 307/2002 Sb., 89/2012 Sb., 262/2006 Sb.
        # Registry ročníku jen 1964 a 2012

        test_years = [1964, 2012]

        for year in test_years:
            self.download_year('cs', year)
            time.sleep(2)

        # Stáhni kompletní obsah testovacích předpisů
        test_documents = [
            '1964-40',  # Občanský zákoník
            '2000-121', # Autorský zákon
            '2011-1',   # ?
            '2002-307', # ?
            '2012-89',  # Občanský zákoník (nový)
            '2006-262'  # Zákoník práce
        ]

        for doc_code in test_documents:
            try:
                self.download_document_content('cs', doc_code)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Chyba při stahování {doc_code}: {e}")

    def scrape_all_documents(self, collection: str, start_year: int, end_year: int):
        """Stáhne všechny dokumenty pomocí HTML scrapingu"""
        logger.info(f"=== HTML Scraping: {collection} ({start_year}-{end_year}) ===")

        documents = self.scraper.scrape_collection(collection, start_year, end_year)

        logger.info(f"Nalezeno {len(documents)} dokumentů ke stažení")

        for i, url in enumerate(documents, 1):
            try:
                doc_data = self.scraper.scrape_document(url)
                if doc_data:
                    # Extrahuj kód dokumentu z URL
                    parts = url.split('/')
                    if len(parts) >= 4:
                        doc_code = parts[-1]

                        # Aktualizuj v databázi
                        cursor = self.db.conn.cursor()
                        cursor.execute("""
                            UPDATE documents
                            SET content_html = ?
                            WHERE code = ?
                        """, (doc_data['html'], doc_code))
                        self.db.conn.commit()

                if i % 10 == 0:
                    logger.info(f"  Staženo {i}/{len(documents)} dokumentů")

                time.sleep(2)  # Respektuj server

            except Exception as e:
                logger.error(f"Chyba při scrapování {url}: {e}")

    def show_statistics(self):
        """Zobrazí statistiky databáze"""
        stats = self.db.get_statistics()

        print("\n" + "="*60)
        print("STATISTIKY LOKÁLNÍ REPLIKY")
        print("="*60)
        print(f"Sbírky:         {stats['collections']}")
        print(f"Typy dokumentů: {stats['doc_types']}")
        print(f"Dokumenty:      {stats['documents']}")
        print(f"Částky:         {stats['batches']}")
        print("\nDokumenty podle sbírek:")
        for coll, count in stats['by_collection'].items():
            print(f"  {coll}: {count}")
        print("="*60 + "\n")

    def close(self):
        """Uzavře všechna spojení"""
        self.db.close()


def main():
    """Hlavní funkce"""
    parser = argparse.ArgumentParser(
        description='Zákony pro lidi - Scraper & Lokální Replika',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mode', choices=['api', 'scrape', 'both', 'stats'],
                       default='api', help='Režim stahování')
    parser.add_argument('--apikey', default='test', help='API klíč')
    parser.add_argument('--collection', default='cs', help='Kód sbírky')
    parser.add_argument('--year', type=int, help='Konkrétní rok')
    parser.add_argument('--start-year', type=int, default=1964, help='Počáteční rok')
    parser.add_argument('--end-year', type=int, default=2012, help='Koncový rok')
    parser.add_argument('--db', default='zakonyprolidi.db', help='Cesta k databázi')
    parser.add_argument('--test-only', action='store_true', help='Stáhnout jen testovací data')

    args = parser.parse_args()

    downloader = ZakonyProLidiDownloader(args.apikey, args.db)

    try:
        if args.mode == 'stats':
            downloader.show_statistics()

        elif args.mode == 'api':
            if args.test_only:
                downloader.download_all_test_data()
            elif args.year:
                downloader.download_year(args.collection, args.year)
            else:
                downloader.download_collection_years(
                    args.collection, args.start_year, args.end_year
                )
            downloader.show_statistics()

        elif args.mode == 'scrape':
            downloader.scrape_all_documents(
                args.collection, args.start_year, args.end_year
            )
            downloader.show_statistics()

        elif args.mode == 'both':
            if args.test_only:
                downloader.download_all_test_data()
            else:
                # Nejdřív API
                downloader.download_collection_years(
                    args.collection, args.start_year, args.end_year
                )
                # Pak scraping pro kompletní obsah
                downloader.scrape_all_documents(
                    args.collection, args.start_year, args.end_year
                )
            downloader.show_statistics()

        logger.info("=== Hotovo! ===")

    except KeyboardInterrupt:
        logger.info("\n=== Přerušeno uživatelem ===")
    except Exception as e:
        logger.error(f"Neočekávaná chyba: {e}", exc_info=True)
    finally:
        downloader.close()


if __name__ == "__main__":
    main()
