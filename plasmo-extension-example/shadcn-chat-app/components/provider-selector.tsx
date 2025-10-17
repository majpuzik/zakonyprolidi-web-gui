"use client"

import { AI_PROVIDERS, type AIProvider } from "@/lib/ai-providers"
import { useState } from "react"

interface ProviderSelectorProps {
  selectedProvider: AIProvider
  onProviderChange: (provider: AIProvider) => void
}

export function ProviderSelector({ selectedProvider, onProviderChange }: ProviderSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <span className="text-2xl">{AI_PROVIDERS[selectedProvider].icon}</span>
        <div className="text-left">
          <div className="text-sm font-medium">{AI_PROVIDERS[selectedProvider].displayName}</div>
          <div className="text-xs text-gray-500">{AI_PROVIDERS[selectedProvider].description}</div>
        </div>
        <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 w-full min-w-[300px] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
          {(Object.keys(AI_PROVIDERS) as AIProvider[]).map((provider) => (
            <button
              key={provider}
              onClick={() => {
                onProviderChange(provider)
                setIsOpen(false)
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                provider === selectedProvider ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              }`}
            >
              <span className="text-2xl">{AI_PROVIDERS[provider].icon}</span>
              <div className="text-left flex-1">
                <div className="text-sm font-medium">{AI_PROVIDERS[provider].displayName}</div>
                <div className="text-xs text-gray-500">{AI_PROVIDERS[provider].description}</div>
                {AI_PROVIDERS[provider].localModel && (
                  <span className="inline-block mt-1 px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded">
                    Lokální
                  </span>
                )}
                {AI_PROVIDERS[provider].apiKeyRequired && (
                  <span className="inline-block mt-1 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded">
                    Vyžaduje API klíč
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
