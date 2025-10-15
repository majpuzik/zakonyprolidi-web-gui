#!/usr/bin/env python3
"""
Zákony pro lidi - Web GUI s AI asistentem
==========================================

Webové rozhraní pro:
- AI dotazy na stažené zákony
- Inteligentní vyhledávání
- Stahování s PDF+OCR
- Indexování a tagování
- Download manager
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import threading
import hashlib

# AI knihovny (volitelné)
try:
    import anthropic
    HAS_ANTHROPIC = True
except:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except:
    HAS_OPENAI = False

# PDF a OCR knihovny
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import simpleSplit
    HAS_PDF = True
except:
    HAS_PDF = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_OCR = True
except:
    HAS_OCR = False

from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Konfigurace
DB_PATH = "zakonyprolidi.db"
PDF_DIR = "pdfs"
OCR_DIR = "ocr_texts"
ATTACHMENTS_DIR = "attachments"

# Vytvoř adresáře
Path(PDF_DIR).mkdir(exist_ok=True)
Path(OCR_DIR).mkdir(exist_ok=True)
Path(ATTACHMENTS_DIR).mkdir(exist_ok=True)

# Globální stav stahování
download_status = {
    'is_running': False,
    'current_doc': None,
    'total': 0,
    'completed': 0,
    'errors': []
}


class AIQueryEngine:
    """AI asistent pro dotazy na zákony"""

    def __init__(self, provider='anthropic', api_key=None):
        self.provider = provider
        self.api_key = api_key or os.getenv(f'{provider.upper()}_API_KEY')

        if provider == 'anthropic' and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif provider == 'openai' and HAS_OPENAI:
            openai.api_key = self.api_key
            self.client = openai

    def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Vyhledá relevantní dokumenty pro dotaz"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # FTS vyhledávání (pokud je k dispozici) nebo LIKE
        cursor.execute("""
            SELECT doc_id, quote, title, year, content_json, tags
            FROM documents
            WHERE title LIKE ? OR content_json LIKE ?
            ORDER BY year DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        docs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return docs

    def ask_ai(self, question: str, context_docs: List[Dict]) -> str:
        """Zeptá se AI s kontextem z dokumentů"""

        # Připrav kontext
        context = "Relevantní právní dokumenty:\n\n"
        for doc in context_docs:
            context += f"**{doc['quote']} - {doc['title']}** (rok {doc['year']})\n"

            # Přidej část obsahu
            if doc.get('content_json'):
                try:
                    content = json.loads(doc['content_json'])
                    if 'Fragments' in content:
                        fragments = content['Fragments'][:5]  # Prvních 5 fragmentů
                        for frag in fragments:
                            if frag.get('Content'):
                                context += f"  {frag['Content'][:200]}...\n"
                except:
                    pass
            context += "\n"

        # Zeptej se AI
        prompt = f"""Jsi právní AI asistent specializující se na české zákony.

{context}

Otázka uživatele: {question}

Odpověz na základě výše uvedených právních dokumentů. Pokud informace nejsou v dokumentech,
jasně to uveď. Odkazuj na konkrétní zákony (číslo Sb.)."""

        if self.provider == 'anthropic' and HAS_ANTHROPIC:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            except Exception as e:
                return f"AI není k dispozici: {e}\n\nKontext:\n{context}"

        elif self.provider == 'openai' and HAS_OPENAI:
            try:
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2048
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"AI není k dispozici: {e}\n\nKontext:\n{context}"

        else:
            # Fallback bez AI - jen zobraz kontext
            return f"AI není nakonfigurováno. Zde jsou relevantní dokumenty:\n\n{context}"


class DocumentIndexer:
    """Indexování a tagování dokumentů"""

    @staticmethod
    def get_tags_from_web(doc_code: str) -> List[str]:
        """Získá tagy z původního webu"""
        try:
            url = f"https://www.zakonyprolidi.cz/cs/{doc_code}"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            tags = []

            # Hledej meta keywords
            meta = soup.find('meta', {'name': 'keywords'})
            if meta and meta.get('content'):
                tags.extend([t.strip() for t in meta['content'].split(',')])

            # Hledej kategorie v breadcrumbs
            breadcrumbs = soup.find_all('a', class_='breadcrumb')
            for bc in breadcrumbs:
                if bc.text.strip():
                    tags.append(bc.text.strip())

            return list(set(tags))  # Unikátní
        except:
            return []

    @staticmethod
    def auto_tag_document(doc: Dict) -> List[str]:
        """Automatické tagování podle obsahu"""
        tags = []
        title = doc.get('title', '').lower()

        # Právní oblasti
        if any(x in title for x in ['trestní', 'trest']):
            tags.append('trestní právo')
        if any(x in title for x in ['občanský', 'obchodní']):
            tags.append('občanské právo')
        if any(x in title for x in ['daň', 'daní']):
            tags.append('daňové právo')
        if any(x in title for x in ['práce', 'zaměstnan']):
            tags.append('pracovní právo')
        if any(x in title for x in ['správní', 'úřad']):
            tags.append('správní právo')
        if any(x in title for x in ['staveb', 'územ']):
            tags.append('stavební právo')
        if any(x in title for x in ['doprav', 'silnič']):
            tags.append('dopravní právo')
        if any(x in title for x in ['životní prostředí', 'ekolog', 'ochrana přírody']):
            tags.append('environmentální právo')

        # Typ dokumentu
        doc_type = doc.get('doc_type', '')
        if doc_type == '4':
            tags.append('zákon')
        elif doc_type == '2':
            tags.append('vyhláška')
        elif doc_type == '1':
            tags.append('nařízení vlády')

        # Rok
        year = doc.get('year')
        if year:
            if year >= 2020:
                tags.append('nové')
            elif year >= 2000:
                tags.append('platné')
            else:
                tags.append('historické')

        return tags

    @staticmethod
    def save_tags(doc_id: int, tags: List[str]):
        """Uloží tagy do databáze"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Aktualizuj tagy jako JSON
        cursor.execute("""
            UPDATE documents
            SET tags = ?
            WHERE doc_id = ?
        """, (json.dumps(tags, ensure_ascii=False), doc_id))

        conn.commit()
        conn.close()


class PDFDownloader:
    """Stahování a konverze do PDF s OCR"""

    @staticmethod
    def download_document_as_pdf(doc_code: str) -> Optional[str]:
        """Stáhne dokument a uloží jako PDF"""
        try:
            url = f"https://www.zakonyprolidi.cz/cs/{doc_code}"
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Najdi hlavní obsah
            content = soup.find('div', class_='Paper')
            if not content:
                return None

            # Vytvoř PDF
            pdf_path = os.path.join(PDF_DIR, f"{doc_code}.pdf")

            if HAS_PDF:
                c = canvas.Canvas(pdf_path, pagesize=A4)
                width, height = A4

                # Registruj české fonty (pokud jsou k dispozici)
                # pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

                y = height - 50

                # Titulek
                title = soup.find('title')
                if title:
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, y, title.text[:80])
                    y -= 30

                # Obsah
                c.setFont("Helvetica", 10)
                text = content.get_text(separator='\n')

                for line in text.split('\n')[:100]:  # Max 100 řádků
                    if y < 50:
                        c.showPage()
                        y = height - 50

                    # Ošetři dlouhé řádky
                    if len(line) > 80:
                        line = line[:80] + '...'

                    try:
                        c.drawString(50, y, line.strip())
                    except:
                        # Ignoruj chyby s neASCII znaky
                        pass
                    y -= 15

                c.save()
                return pdf_path
            else:
                # Fallback - ulož jako text
                txt_path = pdf_path.replace('.pdf', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(content.get_text())
                return txt_path

        except Exception as e:
            print(f"Chyba při stahování PDF: {e}")
            return None

    @staticmethod
    def ocr_pdf(pdf_path: str) -> str:
        """Provede OCR na PDF"""
        if not HAS_OCR:
            return "OCR není k dispozici"

        try:
            # Převeď PDF na obrázky
            images = convert_from_path(pdf_path)

            # OCR na každé stránce
            text = ""
            for i, img in enumerate(images):
                text += f"\n--- Stránka {i+1} ---\n"
                text += pytesseract.image_to_string(img, lang='ces+eng')

            # Ulož OCR text
            ocr_path = os.path.join(OCR_DIR, Path(pdf_path).stem + '.txt')
            with open(ocr_path, 'w', encoding='utf-8') as f:
                f.write(text)

            return ocr_path
        except Exception as e:
            return f"OCR chyba: {e}"

    @staticmethod
    def download_attachments(doc_code: str) -> List[str]:
        """Stáhne všechny přílohy dokumentu"""
        try:
            url = f"https://www.zakonyprolidi.cz/cs/{doc_code}"
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            attachments = []

            # Hledej odkazy na přílohy
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                    # Stáhni přílohu
                    if not href.startswith('http'):
                        href = 'https://www.zakonyprolidi.cz' + href

                    filename = os.path.basename(href.split('?')[0])
                    filepath = os.path.join(ATTACHMENTS_DIR, doc_code, filename)

                    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

                    att_response = requests.get(href, timeout=30)
                    with open(filepath, 'wb') as f:
                        f.write(att_response.content)

                    attachments.append(filepath)

            return attachments
        except Exception as e:
            print(f"Chyba při stahování příloh: {e}")
            return []


class DownloadManager:
    """Správa stahování s kontrolou duplikátů"""

    def __init__(self):
        self.pause_seconds = 2
        self.max_docs = 100

    def is_downloaded(self, doc_code: str) -> bool:
        """Zkontroluje, zda už je dokument stažen"""
        pdf_path = os.path.join(PDF_DIR, f"{doc_code}.pdf")
        txt_path = os.path.join(PDF_DIR, f"{doc_code}.txt")
        return os.path.exists(pdf_path) or os.path.exists(txt_path)

    def download_batch(self, criteria: Dict):
        """Stáhne dávku dokumentů podle kritérií"""
        global download_status

        download_status['is_running'] = True
        download_status['errors'] = []
        download_status['completed'] = 0

        try:
            # Získej dokumenty podle kritérií
            docs = self.get_documents_by_criteria(criteria)
            download_status['total'] = len(docs)

            for doc in docs:
                if not download_status['is_running']:
                    break

                doc_code = doc['code']
                download_status['current_doc'] = doc_code

                # Kontrola, zda už není stažen
                if self.is_downloaded(doc_code):
                    print(f"⏭️  {doc_code} již stažen")
                    download_status['completed'] += 1
                    continue

                try:
                    # Stáhni PDF
                    pdf_path = PDFDownloader.download_document_as_pdf(doc_code)

                    if pdf_path:
                        # OCR (pokud je k dispozici)
                        if HAS_OCR and pdf_path.endswith('.pdf'):
                            PDFDownloader.ocr_pdf(pdf_path)

                        # Stáhni přílohy
                        PDFDownloader.download_attachments(doc_code)

                        # Indexuj a taguj
                        tags_web = DocumentIndexer.get_tags_from_web(doc_code)
                        tags_auto = DocumentIndexer.auto_tag_document(doc)
                        all_tags = list(set(tags_web + tags_auto))
                        DocumentIndexer.save_tags(doc['doc_id'], all_tags)

                        download_status['completed'] += 1

                except Exception as e:
                    error_msg = f"{doc_code}: {str(e)}"
                    download_status['errors'].append(error_msg)
                    print(f"❌ {error_msg}")

                # Pauza
                time.sleep(self.pause_seconds)

        finally:
            download_status['is_running'] = False

    def get_documents_by_criteria(self, criteria: Dict) -> List[Dict]:
        """Získá dokumenty podle kritérií"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        # Datum od-do
        if criteria.get('date_from'):
            query += " AND publish_date >= ?"
            params.append(criteria['date_from'])

        if criteria.get('date_to'):
            query += " AND publish_date <= ?"
            params.append(criteria['date_to'])

        # Stáří ve dnech
        if criteria.get('days_old'):
            days_ago = (datetime.now() - timedelta(days=criteria['days_old'])).strftime('%Y-%m-%d')
            query += " AND publish_date >= ?"
            params.append(days_ago)

        # Typ dokumentu
        if criteria.get('doc_type'):
            query += " AND doc_type = ?"
            params.append(criteria['doc_type'])

        # Rok
        if criteria.get('year'):
            query += " AND year = ?"
            params.append(criteria['year'])

        # Řazení a limit
        query += " ORDER BY publish_date DESC"

        if criteria.get('max_docs'):
            query += " LIMIT ?"
            params.append(criteria['max_docs'])
        else:
            query += " LIMIT ?"
            params.append(self.max_docs)

        cursor.execute(query, params)
        docs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return docs


# ========== FLASK ROUTES ==========

ai_engine = AIQueryEngine(provider='anthropic')
download_manager = DownloadManager()


@app.route('/')
def index():
    """Hlavní stránka"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """API pro vyhledávání"""
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Prázdný dotaz'}), 400

    # Vyhledej dokumenty
    docs = ai_engine.search_documents(query, limit=10)

    return jsonify({
        'query': query,
        'count': len(docs),
        'documents': docs
    })


@app.route('/api/ask', methods=['POST'])
def ask_ai():
    """API pro AI dotazy"""
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'Prázdná otázka'}), 400

    # Najdi relevantní dokumenty
    context_docs = ai_engine.search_documents(question, limit=5)

    # Zeptej se AI
    answer = ai_engine.ask_ai(question, context_docs)

    return jsonify({
        'question': question,
        'answer': answer,
        'sources': [{'quote': d['quote'], 'title': d['title']} for d in context_docs]
    })


@app.route('/api/download/start', methods=['POST'])
def start_download():
    """Spustí stahování"""
    if download_status['is_running']:
        return jsonify({'error': 'Stahování už běží'}), 400

    criteria = request.json

    # Validace
    if criteria.get('max_docs', 0) > 1000:
        return jsonify({'error': 'Max 1000 dokumentů najednou'}), 400

    # Spusť v threadu
    thread = threading.Thread(target=download_manager.download_batch, args=(criteria,))
    thread.start()

    return jsonify({'status': 'started'})


@app.route('/api/download/stop', methods=['POST'])
def stop_download():
    """Zastaví stahování"""
    download_status['is_running'] = False
    return jsonify({'status': 'stopped'})


@app.route('/api/download/status')
def get_download_status():
    """Vrátí stav stahování"""
    return jsonify(download_status)


@app.route('/api/stats')
def get_stats():
    """Statistiky databáze"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM documents WHERE tags IS NOT NULL")
    tagged_docs = cursor.fetchone()[0]

    # Dokumenty s PDF
    pdf_count = len([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')])

    conn.close()

    return jsonify({
        'total_documents': total_docs,
        'tagged_documents': tagged_docs,
        'pdf_documents': pdf_count,
        'ocr_documents': len(os.listdir(OCR_DIR)) if os.path.exists(OCR_DIR) else 0
    })


@app.route('/api/document/<doc_code>')
def get_document(doc_code):
    """Detail dokumentu"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents WHERE code = ?", (doc_code,))
    doc = cursor.fetchone()
    conn.close()

    if not doc:
        return jsonify({'error': 'Dokument nenalezen'}), 404

    doc_dict = dict(doc)

    # Přidej info o PDF
    pdf_path = os.path.join(PDF_DIR, f"{doc_code}.pdf")
    doc_dict['has_pdf'] = os.path.exists(pdf_path)

    # Přidej tagy
    if doc_dict.get('tags'):
        doc_dict['tags'] = json.loads(doc_dict['tags'])

    return jsonify(doc_dict)


if __name__ == '__main__':
    print("🚀 Zákony pro lidi - Web GUI")
    print("="*60)
    print(f"📊 Databáze: {DB_PATH}")
    print(f"📁 PDF adresář: {PDF_DIR}")
    print(f"🔍 OCR adresář: {OCR_DIR}")
    print(f"📎 Přílohy: {ATTACHMENTS_DIR}")
    print("="*60)
    print(f"AI: Anthropic {'✅' if HAS_ANTHROPIC else '❌'}, OpenAI {'✅' if HAS_OPENAI else '❌'}")
    print(f"PDF: {'✅' if HAS_PDF else '❌'}")
    print(f"OCR: {'✅' if HAS_OCR else '❌'}")
    print("="*60)
    print("🌐 Server běží na: http://localhost:5000")
    print("="*60)

    app.run(debug=True, port=5000, host='0.0.0.0')
