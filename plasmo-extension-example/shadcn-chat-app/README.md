# AI Web Dev Assistant

Next.js aplikace pro generování React komponent s AI modely (Claude, Ollama). Inspirováno v0.dev a Relume.

## 🚀 Funkce

- **Generování funkčního kódu**: AI vytváří React komponenty s Tailwind CSS (ne jen textové popisy)
- **Živý náhled kódu**: Automatický sandbox preview pro TSX/JSX/HTML
- **Multi-provider podpora**: Claude (Anthropic API) + Ollama (local/cloud modely)
- **Model selector**: 11 modelů (6 cloud, 5 lokálních) optimalizovaných pro programování
- **Code preview akce**: Copy to clipboard, Download, Open in new tab
- **Markdown rendering**: Syntax highlighting (highlight.js) + live preview

## 📦 Tech Stack

- **Next.js 15.5.6** (App Router, Edge Runtime)
- **React 19.1.0** + TypeScript
- **AI SDK 4.3.19** (Vercel) - chat hooks
- **Ollama** (ollama-ai-provider 1.2.0)
- **Anthropic** (@ai-sdk/anthropic 1.0.0)
- **Tailwind CSS 4** + shadcn/ui
- **react-markdown** + rehype-highlight + remark-gfm
- **Framer Motion** - animace

## 🎯 Dostupné Modely

### Cloud Modely (Ollama remote)
- `kimi-k2:1t-cloud` (1 trillion parametrů) - největší model
- `deepseek-v3.1:671b-cloud` (671B params)
- `qwen3-coder:480b-cloud` (480B params)
- `gpt-oss:120b-cloud` (120B params)
- `gpt-oss:20b-cloud` (20B params)
- `glm-4.6:cloud`

### Lokální Modely
- `qwen2.5:32b` ⭐ **Výchozí** - nejlepší poměr rychlost/kvalita
- `deepseek-r1:14b`
- `gpt-oss:20b`
- `qwen2.5:7b`
- `llama3.2:3b`

## 🛠️ Instalace

```bash
# Clone repository
git clone <repo-url>
cd shadcn-chat-app

# Install dependencies
npm install

# Setup environment variables
cp .env.template .env.local
```

### Environment Variables

```bash
# .env.local

# Anthropic Claude (volitelné)
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (volitelné, defaulty níže)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
```

### Ollama Setup

```bash
# Install Ollama
brew install ollama

# Start Ollama service
ollama serve

# Pull recommended model
ollama pull qwen2.5:32b

# Verify installation
ollama list
```

## 🚦 Spuštění

```bash
# Development server
npm run dev

# Production build
npm run build
npm start

# Linter
npm run lint
```

Aplikace běží na: **http://localhost:3000**

## 📁 Struktura Projektu

```
shadcn-chat-app/
├── app/
│   ├── api/chat/
│   │   ├── claude/route.ts      # Claude API endpoint
│   │   └── ollama/route.ts      # Ollama API endpoint
│   ├── page.tsx                 # Hlavní stránka
│   └── layout.tsx
├── components/
│   ├── ui/
│   │   ├── chat.tsx             # Chat container
│   │   ├── chat-message.tsx     # Message renderer
│   │   ├── markdown-renderer.tsx # Markdown parser s CodePreview
│   │   ├── message-input.tsx    # Input s attachments
│   │   └── message-list.tsx     # Message list
│   ├── code-preview.tsx         # Live preview + akce tlačítka
│   ├── model-selector.tsx       # Ollama model dropdown
│   ├── provider-selector.tsx    # Claude/Ollama switch
│   └── tool-selector.tsx        # Příklady promptů
├── lib/
│   └── ai-providers.ts          # Provider konfigurace
├── hooks/
│   ├── use-audio-recording.ts
│   └── use-autosize-textarea.ts
└── README.md
```

## 🎨 Použití

### 1. Základní Prompt

```
Vytvoř moderní hero sekci s gradientem
```

**Výstup**: Funkční TSX komponenta s live preview

### 2. Komplexní Požadavek

```
Landing page pro SaaS startup:
- Hero sekce s gradientem
- Pricing tabulka (3 tarify)
- Feature cards (6 features)
- Kontaktní formulář s validací
```

**AI vytvoří**:
1. ASCII wireframe
2. Jednotlivé komponenty krok za krokem
3. Každá s live preview

### 3. Code Preview Akce

Po vygenerování kódu:
- **Copy**: Zkopíruje kód do clipboardu
- **Download**: Stáhne jako `.tsx` soubor
- **Open**: Otevře v novém okně s live preview

## 🔧 Konfigurace

### System Prompt (Ollama)

```typescript
// app/api/chat/ollama/route.ts

const WEB_DEV_SYSTEM_PROMPT = `Jsi AI Web Dev Assistant - expert na vývoj webových aplikací.

DŮLEŽITÉ PRAVIDLO: VŽDY generuj funkční kód, nejen popis!

Když uživatel požádá o komponentu/web/sekci:
1. Vytvoř kompletní, funkční React komponentu s Tailwind CSS
2. Kód vlož do markdown bloku s "tsx" nebo "html"
3. Stručně vysvětli co jsi vytvořil

Když uživatel pošle analýzu/požadavky:
- Nejprve vytvoř drátový model (wireframe) jako ASCII art nebo jednoduchý HTML
- Pak vygeneruj funkční komponenty
- Postupuj krok za krokem

Vždy piš v češtině a generuj produkční kód s Tailwind CSS, React hooks, TypeScript.`
```

### Markdown Renderer

```typescript
// components/ui/markdown-renderer.tsx

// Automaticky detekuje code blocky a renderuje s CodePreview
if (!inline && (language === 'tsx' || language === 'jsx' || language === 'html')) {
  return (
    <CodePreview
      code={codeString}
      language={language}
      preview={language === 'tsx' || language === 'jsx' || language === 'html'}
    />
  )
}
```

## 🐛 Debugging

### Problém: Ollama nefunguje

```bash
# Check Ollama status
ollama list

# Restart Ollama
killall ollama
ollama serve

# Test API
curl http://localhost:11434/api/tags
```

### Problém: Claude API error

```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Test API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

### Problém: Odesílací tlačítko chybí

Tlačítko je na řádku 237-286 v `components/ui/message-input.tsx`. Musí být uvnitř `relative flex-1` containeru.

## 📝 Klíčové Opravy

### 1. Long Text Input Bug (Fixed)
**Problém**: Text >500 znaků se převedl na file attachment
**Fix**: Odstraněn automatický převod v `onPaste` handleru (řádky 113-127)

### 2. Code Preview Integration (Fixed)
**Problém**: Code blocks se nerendrovaly s preview
**Fix**: Import path fix `../code-preview` v `markdown-renderer.tsx`

### 3. Send Button Position (Fixed)
**Problém**: Odesílací tlačítko bylo mimo správný container
**Fix**: Přesunutí button containeru dovnitř `relative flex-1` divu

## 🎓 API Reference

### POST /api/chat/ollama

```typescript
// Request
{
  messages: Array<{ role: 'user' | 'assistant', content: string }>,
  model?: string // Default: 'qwen2.5:32b'
}

// Response
StreamTextResponse (AI SDK format)
```

### POST /api/chat/claude

```typescript
// Request
{
  messages: Array<{ role: 'user' | 'assistant', content: string }>
}

// Response
StreamTextResponse (AI SDK format)
```

## 📊 Výkon

- **qwen2.5:32b** (local): ~9s response time
- **deepseek-r1:14b** (local): ~13s response time
- **kimi-k2:1t-cloud** (remote): ~60-180s response time

## 🔐 Bezpečnost

- Code preview běží v `<iframe sandbox="allow-scripts">`
- External CDN sources: React, ReactDOM, Babel, Tailwind CSS
- No server-side code execution
- API keys v `.env.local` (gitignored)

## 📚 Odkazy

- [Next.js Docs](https://nextjs.org/docs)
- [AI SDK Docs](https://sdk.vercel.ai/docs)
- [Ollama Models](https://ollama.com/library)
- [Anthropic API](https://docs.anthropic.com/)
- [shadcn/ui](https://ui.shadcn.com/)

## 📄 License

MIT

## 👨‍💻 Autor

Created with Claude Code

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-17
