import { StreamingTextResponse } from 'ai'

export const runtime = 'edge'

export async function POST(req: Request) {
  const { messages } = await req.json()

  // Simulace AI odpovědi (bez potřeby API klíče)
  const lastMessage = messages[messages.length - 1]?.content || ''

  const responses = [
    `Slyším tě! Napsal jsi: "${lastMessage}". Jak ti mohu pomoci?`,
    `To je zajímavé! Říkáš "${lastMessage}". Řekni mi více.`,
    `Rozumím. Tvoje zpráva "${lastMessage}" je zajímavá. Co bys chtěl vědět?`,
    `Ahoj! Vidím, že jsi napsal "${lastMessage}". Můžu ti s tím pomoct?`,
    `Díky za zprávu "${lastMessage}". Co dalšího tě zajímá?`
  ]

  const randomResponse = responses[Math.floor(Math.random() * responses.length)]

  // Vytvoření simulovaného streamingu
  const stream = new ReadableStream({
    async start(controller) {
      const words = randomResponse.split(' ')

      for (const word of words) {
        controller.enqueue(new TextEncoder().encode(word + ' '))
        // Pauza mezi slovy pro efekt psaní
        await new Promise(resolve => setTimeout(resolve, 50))
      }

      controller.close()
    }
  })

  return new StreamingTextResponse(stream)
}
