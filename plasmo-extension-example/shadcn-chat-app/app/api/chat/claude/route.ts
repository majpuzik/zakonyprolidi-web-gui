import { anthropic } from '@ai-sdk/anthropic'
import { streamText } from 'ai'

export const runtime = 'edge'

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

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    // Zkontroluj API klíč
    const apiKey = process.env.ANTHROPIC_API_KEY
    if (!apiKey) {
      return new Response(
        JSON.stringify({
          error: 'ANTHROPIC_API_KEY není nastaven. Přidej ho do .env.local:',
          instructions: `
# V projektu vytvoř soubor .env.local:
ANTHROPIC_API_KEY=sk-ant-...

# Získej API klíč na: https://console.anthropic.com/

# Pak restartuj server: npm run dev
          `
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Skutečné volání Claude API přes AI SDK
    const result = await streamText({
      model: anthropic('claude-3-5-sonnet-20241022', {
        apiKey,
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
    console.error('Claude API error:', error)

    if (error.message?.includes('401') || error.message?.includes('authentication')) {
      return new Response('Neplatný ANTHROPIC_API_KEY. Zkontroluj ho v .env.local', { status: 401 })
    }

    return new Response(`Claude API error: ${error.message}`, { status: 500 })
  }
}
