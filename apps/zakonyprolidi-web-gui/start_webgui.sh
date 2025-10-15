#!/bin/bash
# Spouštěcí skript pro Web GUI

echo "🌐 Zákony pro lidi - Web GUI s AI asistentem"
echo "=============================================="
echo ""

# Kontrola databáze
if [ ! -f "zakonyprolidi.db" ]; then
    echo "❌ Chybí databáze zakonyprolidi.db"
    echo "💡 Nejdřív spusť: python3 zakonyprolidi_scraper.py --test-only"
    exit 1
fi

# Kontrola Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask není nainstalován"
    echo "💡 Instalace: pip3 install --user flask"
    exit 1
fi

# Kontrola AI klíče (volitelné)
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  AI klíč není nastaven - AI asistent nebude fungovat"
    echo "💡 Pro plnou funkčnost nastav:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo "   nebo"
    echo "   export OPENAI_API_KEY='sk-...'"
    echo ""
    echo "📖 Vyhledávání a stahování bude fungovat i bez AI"
    echo ""
fi

# Vytvoř adresáře
mkdir -p pdfs ocr_texts attachments templates

echo "✅ Vše připraveno!"
echo ""
echo "🚀 Spouštím web server..."
echo "🌐 Otevři prohlížeč na: http://localhost:5000"
echo ""
echo "⏸️  Pro zastavení stiskni Ctrl+C"
echo ""

# Spusť server
python3 zakonyprolidi_web.py
