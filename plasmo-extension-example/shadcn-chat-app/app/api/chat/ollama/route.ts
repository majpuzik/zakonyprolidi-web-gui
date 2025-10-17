import { ollama } from 'ollama-ai-provider'
import { streamText } from 'ai'

export const runtime = 'edge'

const WEB_DEV_SYSTEM_PROMPT = `Jsi AI Web Dev Assistant - expert na vývoj webových aplikací.

DŮLEŽITÉ PRAVIDLO: VŽDY generuj funkční kód, nejen popis!

Když uživatel požádá o komponentu/web/sekci:
1. Vytvoř kompletní, funkční React komponentu s Tailwind CSS
2. Kód vlož do markdown bloku s "tsx" nebo "html"
3. Stručně vysvětli co jsi vytvořil

PŘÍKLAD ODPOVĚDI:
"Vytvořil jsem moderní hero sekci s gradientem:

\`\`\`tsx
export default function HeroSection() {
  return (
    <section className="min-h-screen bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center p-8">
      <div className="text-center text-white">
        <h1 className="text-6xl font-bold mb-4">Vítejte</h1>
        <p className="text-xl">Moderní webové řešení</p>
        <button className="mt-8 px-8 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100">
          Zjistit více
        </button>
      </div>
    </section>
  )
}
\`\`\`

Sekce obsahuje centrovaný obsah, gradient pozadí a CTA tlačítko."

Když uživatel pošle analýzu/požadavky:
- Nejprve vytvoř drátový model (wireframe) jako ASCII art nebo jednoduchý HTML
- Pak vygeneruj funkční komponenty
- Postupuj krok za krokem

Vždy piš v češtině a generuj produkční kód s Tailwind CSS, React hooks, TypeScript.`

export async function POST(req: Request) {
  try {
    const { messages, model: requestModel } = await req.json()

    // Konfigurace Ollama
    const ollamaUrl = process.env.OLLAMA_API_URL || 'http://localhost:11434'
    const model = requestModel || process.env.OLLAMA_MODEL || 'kimi-k2:1t-cloud'

    // Skutečné volání Ollama API přes AI SDK
    const result = await streamText({
      model: ollama(model, {
        baseURL: ollamaUrl,
      }),
      system: WEB_DEV_SYSTEM_PROMPT,
      messages: messages.map((m: any) => ({
        role: m.role,
        content: m.content,
      })),
      maxTokens: 4096,
      temperature: 0.7,
    })

    // Streaming odpověď
    return result.toDataStreamResponse()

  } catch (error: any) {
    console.error('Ollama error:', error)

    return new Response(
      JSON.stringify({
        error: error.message,
        instructions: `
# Ollama není nainstalován nebo neběží

1. Nainstaluj Ollama:
   brew install ollama

2. Stáhni model:
   ollama pull codellama:13b

3. Ověř, že běží:
   ollama list

4. (Volitelně) Nastav v .env.local:
   OLLAMA_API_URL=http://localhost:11434
   OLLAMA_MODEL=codellama:13b

5. Ollama běží lokálně = zdarma a soukromé!
        `
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
