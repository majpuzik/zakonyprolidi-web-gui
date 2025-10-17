"use client"

import { WEB_DEV_TOOLS } from "@/lib/ai-providers"

interface ToolSelectorProps {
  onToolSelect: (prompt: string) => void
}

export function ToolSelector({ onToolSelect }: ToolSelectorProps) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800/50">
      <h3 className="text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">🛠️ Web Dev Nástroje</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {Object.values(WEB_DEV_TOOLS).map((tool) => (
          <button
            key={tool.name}
            onClick={() => onToolSelect(tool.prompt)}
            className="flex flex-col items-center gap-1 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 transition-all text-center group"
            title={tool.description}
          >
            <span className="text-2xl group-hover:scale-110 transition-transform">{tool.icon}</span>
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{tool.name}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
