import { openai } from '@ai-sdk/openai'
import { streamText } from 'ai'

export const runtime = 'edge'

const WEB_DEV_SYSTEM_PROMPT = `You are an expert web developer specializing in React, Next.js, TypeScript, Tailwind CSS, and modern web technologies. Provide production-ready code with detailed explanations. Respond in Czech language.`

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    // Zkontroluj API klíč
    const apiKey = process.env.OPENAI_API_KEY
    if (!apiKey) {
      return new Response(
        JSON.stringify({
          error: 'OPENAI_API_KEY není nastaven',
          instructions: `
# V projektu vytvoř soubor .env.local:
OPENAI_API_KEY=sk-...

# Získej API klíč na: https://platform.openai.com/api-keys

# Pak restartuj server: npm run dev
          `
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Skutečné volání OpenAI API přes AI SDK
    const result = await streamText({
      model: openai('gpt-4-turbo-preview', {
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
    console.error('OpenAI API error:', error)

    if (error.message?.includes('401') || error.message?.includes('authentication')) {
      return new Response('Neplatný OPENAI_API_KEY. Zkontroluj ho v .env.local', { status: 401 })
    }

    return new Response(`OpenAI API error: ${error.message}`, { status: 500 })
  }
}
