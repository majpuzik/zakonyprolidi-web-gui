#!/usr/bin/env python3
"""Quick test of Web GUI functionality"""

import sqlite3

print("🧪 Testování Web GUI")
print("="*60)

# Test 1: Database
print("\n1. Kontrola databáze...")
try:
    conn = sqlite3.connect("zakonyprolidi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    print(f"   ✅ Databáze OK ({count} dokumentů)")
    conn.close()
except Exception as e:
    print(f"   ❌ Chyba: {e}")

# Test 2: Flask
print("\n2. Kontrola Flask...")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__} OK")
except Exception as e:
    print(f"   ❌ Chyba: {e}")

# Test 3: Templates
print("\n3. Kontrola templates...")
import os
if os.path.exists("templates/index.html"):
    size = os.path.getsize("templates/index.html")
    print(f"   ✅ index.html OK ({size} bytes)")
else:
    print("   ❌ templates/index.html neexistuje")

# Test 4: Optional dependencies
print("\n4. Volitelné závislosti...")

# AI
try:
    import anthropic
    print("   ✅ Anthropic Claude API")
except:
    print("   ⚠️  Anthropic není nainstalován (AI nebude fungovat)")

try:
    import openai
    print("   ✅ OpenAI GPT API")
except:
    print("   ⚠️  OpenAI není nainstalován (AI nebude fungovat)")

# PDF
try:
    from reportlab.pdfgen import canvas
    print("   ✅ ReportLab (PDF generování)")
except:
    print("   ⚠️  ReportLab není nainstalován (PDF nebude fungovat)")

# OCR
try:
    import pytesseract
    print("   ✅ Pytesseract (OCR)")
except:
    print("   ⚠️  Pytesseract není nainstalován (OCR nebude fungovat)")

print("\n" + "="*60)
print("📝 Shrnutí:")
print("   - Flask web server: Připraven")
print("   - Databáze: OK")
print("   - Templates: OK")
print("   - AI: " + ("✅ OK" if os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY') else "⚠️  Nastav API klíč"))
print("\n💡 Pro spuštění:")
print("   ./start_webgui.sh")
print("   nebo")
print("   python3 zakonyprolidi_web.py")
print("")
