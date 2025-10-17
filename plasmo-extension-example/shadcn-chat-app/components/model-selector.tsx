"use client"

import { useState } from "react"
import { ChevronDown } from "lucide-react"

export type OllamaModel =
  // Remote modely (cloud)
  | "kimi-k2:1t-cloud"
  | "deepseek-v3.1:671b-cloud"
  | "qwen3-coder:480b-cloud"
  | "gpt-oss:120b-cloud"
  | "gpt-oss:20b-cloud"
  | "glm-4.6:cloud"
  // Lokální modely
  | "qwen2.5:32b"
  | "deepseek-r1:14b"
  | "gpt-oss:20b"
  | "qwen2.5:7b"
  | "llama3.2:3b"

interface ModelInfo {
  name: OllamaModel
  displayName: string
  description: string
  size: string
  speed: "fast" | "medium" | "slow"
  isRemote: boolean
}

const CODING_MODELS: Record<OllamaModel, ModelInfo> = {
  // Remote modely
  "kimi-k2:1t-cloud": {
    name: "kimi-k2:1t-cloud",
    displayName: "Kimi K2 1T Cloud",
    description: "☁️ Největší model - 1 trilion parametrů",
    size: "Cloud",
    speed: "medium",
    isRemote: true
  },
  "deepseek-v3.1:671b-cloud": {
    name: "deepseek-v3.1:671b-cloud",
    displayName: "DeepSeek V3.1 671B Cloud",
    description: "☁️ Reasoning gigant - 671 miliard parametrů",
    size: "Cloud",
    speed: "medium",
    isRemote: true
  },
  "qwen3-coder:480b-cloud": {
    name: "qwen3-coder:480b-cloud",
    displayName: "Qwen3 Coder 480B Cloud",
    description: "☁️ Coding expert - 480 miliard parametrů",
    size: "Cloud",
    speed: "medium",
    isRemote: true
  },
  "gpt-oss:120b-cloud": {
    name: "gpt-oss:120b-cloud",
    displayName: "GPT-OSS 120B Cloud",
    description: "☁️ Open source GPT - 120 miliard parametrů",
    size: "Cloud",
    speed: "fast",
    isRemote: true
  },
  "gpt-oss:20b-cloud": {
    name: "gpt-oss:20b-cloud",
    displayName: "GPT-OSS 20B Cloud",
    description: "☁️ Kompaktní GPT reasoning",
    size: "Cloud",
    speed: "fast",
    isRemote: true
  },
  "glm-4.6:cloud": {
    name: "glm-4.6:cloud",
    displayName: "GLM 4.6 Cloud",
    description: "☁️ Multimodální reasoning model",
    size: "Cloud",
    speed: "fast",
    isRemote: true
  },
  // Lokální modely
  "qwen2.5:32b": {
    name: "qwen2.5:32b",
    displayName: "Qwen2.5 32B",
    description: "💻 Nejlepší lokální pro kódování",
    size: "19GB",
    speed: "fast",
    isRemote: false
  },
  "gpt-oss:20b": {
    name: "gpt-oss:20b",
    displayName: "GPT-OSS 20B",
    description: "💻 Reasoning model s CoT",
    size: "13GB",
    speed: "fast",
    isRemote: false
  },
  "deepseek-r1:14b": {
    name: "deepseek-r1:14b",
    displayName: "DeepSeek-R1 14B",
    description: "💻 Reasoning pro komplexní problémy",
    size: "9GB",
    speed: "medium",
    isRemote: false
  },
  "qwen2.5:7b": {
    name: "qwen2.5:7b",
    displayName: "Qwen2.5 7B",
    description: "💻 Rychlý kompaktní model",
    size: "4.7GB",
    speed: "fast",
    isRemote: false
  },
  "llama3.2:3b": {
    name: "llama3.2:3b",
    displayName: "Llama 3.2 3B",
    description: "💻 Nejrychlejší - základní použití",
    size: "2GB",
    speed: "fast",
    isRemote: false
  }
}

interface ModelSelectorProps {
  selectedModel: OllamaModel
  onModelChange: (model: OllamaModel) => void
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const currentModel = CODING_MODELS[selectedModel]

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-left min-w-[200px]"
      >
        <div className="flex-1">
          <div className="text-sm font-medium">{currentModel.displayName}</div>
          <div className="text-xs opacity-75">{currentModel.size}</div>
        </div>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full mt-2 w-full min-w-[380px] bg-white dark:bg-gray-900 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-20">
            <div className="p-2 border-b border-gray-200 dark:border-gray-700">
              <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase px-2">
                ☁️ Remote Modely (Cloud)
              </div>
            </div>
            <div className="max-h-[500px] overflow-y-auto">
              {(Object.values(CODING_MODELS) as ModelInfo[])
                .filter(m => m.isRemote)
                .map((model) => (
                <button
                  key={model.name}
                  onClick={() => {
                    onModelChange(model.name)
                    setIsOpen(false)
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
                    selectedModel === model.name ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="font-medium text-sm">{model.displayName}</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {model.description}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                        {model.size}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        model.speed === 'fast' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' :
                        model.speed === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300' :
                        'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                      }`}>
                        {model.speed === 'fast' ? '⚡ Rychlý' :
                         model.speed === 'medium' ? '🔄 Střední' : '🐌 Pomalý'}
                      </span>
                    </div>
                  </div>
                  {selectedModel === model.name && (
                    <div className="mt-2 text-xs text-indigo-600 dark:text-indigo-400">
                      ✓ Aktivní
                    </div>
                  )}
                </button>
              ))}

              <div className="p-2 border-t border-b border-gray-200 dark:border-gray-700 mt-2">
                <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase px-2">
                  💻 Lokální Modely
                </div>
              </div>

              {(Object.values(CODING_MODELS) as ModelInfo[])
                .filter(m => !m.isRemote)
                .map((model) => (
                <button
                  key={model.name}
                  onClick={() => {
                    onModelChange(model.name)
                    setIsOpen(false)
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
                    selectedModel === model.name ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="font-medium text-sm">{model.displayName}</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {model.description}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        {model.size}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        model.speed === 'fast' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' :
                        model.speed === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300' :
                        'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                      }`}>
                        {model.speed === 'fast' ? '⚡ Rychlý' :
                         model.speed === 'medium' ? '🔄 Střední' : '🐌 Pomalý'}
                      </span>
                    </div>
                  </div>
                  {selectedModel === model.name && (
                    <div className="mt-2 text-xs text-indigo-600 dark:text-indigo-400">
                      ✓ Aktivní
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
