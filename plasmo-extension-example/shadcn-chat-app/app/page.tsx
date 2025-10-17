"use client"

import { useChat } from "ai/react"
import { Chat } from "@/components/ui/chat"
import { useEffect, useState } from "react"
import { ProviderSelector } from "@/components/provider-selector"
import { ModelSelector, type OllamaModel } from "@/components/model-selector"
import { ToolSelector } from "@/components/tool-selector"
import { EXAMPLE_PROMPTS, type AIProvider } from "@/lib/ai-providers"

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'assistant' as const,
  content: `🚀 **AI Web Dev Assistant**

Generuji **funkční kód** pro webové aplikace!

**Co umím:**
✨ Vytvořit React komponenty s Tailwind CSS
🎨 Navrhnout drátové modely (wireframes)
🧩 Vygenerovat kompletní stránky
💅 Implementovat moderní UI/UX design

**Jak to funguje:**
1. Popiš co chceš vytvořit (např. "Hero sekce s gradientem")
2. Dostaneš **funkční kód + živý náhled**
3. Stáhni si kód nebo otevři v novém okně

**Příklady promptů:**
- "Vytvoř moderní pricing sekci s 3 tarify"
- "Landing page pro SaaS startup"
- "Kontaktní formulář s validací"
- "Dashboard s grafy"

**Tip:** Pošli analýzu projektu → dostaneš wireframe + komponenty!
`
}

export default function Home() {
  const [selectedProvider, setSelectedProvider] = useState<AIProvider>('ollama')
  const [selectedModel, setSelectedModel] = useState<OllamaModel>('qwen2.5:32b')
  const { messages, input, handleInputChange, handleSubmit, isLoading, stop, setMessages, setInput, append } = useChat({
    api: `/api/chat/${selectedProvider}`,
    body: {
      model: selectedModel
    }
  })

  // Přidej uvítací zprávu
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([WELCOME_MESSAGE])
    }
  }, [])

  const handleToolSelect = (promptTemplate: string) => {
    setInput(promptTemplate + " ")
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white">
        <div className="p-4 flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              🚀 AI Web Dev Assistant
            </h1>
            <p className="text-sm opacity-90">
              Claude • Ollama • Relume • v0.dev • Penpot
            </p>
          </div>
          <div className="flex items-center gap-3">
            {selectedProvider === 'ollama' && (
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
              />
            )}
            <ProviderSelector
              selectedProvider={selectedProvider}
              onProviderChange={setSelectedProvider}
            />
          </div>
        </div>
      </header>

      <ToolSelector onToolSelect={handleToolSelect} />

      <main className="flex-1 overflow-hidden">
        <Chat
          messages={messages}
          input={input}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          isGenerating={isLoading}
          stop={stop}
          placeholder="Napiš co chceš vytvořit... (např. 'Hero sekce s gradientem')"
          append={append}
          suggestions={messages.length <= 1 ? EXAMPLE_PROMPTS : undefined}
          setMessages={setMessages}
        />
      </main>
    </div>
  );
}
