// AI Provider Configuration
export type AIProvider = 'claude' | 'ollama' | 'openai'

export interface AIProviderConfig {
  name: string
  displayName: string
  description: string
  icon: string
  apiKeyRequired: boolean
  localModel: boolean
  capabilities: {
    code: boolean
    design: boolean
    reasoning: boolean
  }
}

export const AI_PROVIDERS: Record<AIProvider, AIProviderConfig> = {
  claude: {
    name: 'claude',
    displayName: 'Claude (Anthropic)',
    description: 'Nejlepší pro coding a web development',
    icon: '🤖',
    apiKeyRequired: true,
    localModel: false,
    capabilities: {
      code: true,
      design: true,
      reasoning: true,
    },
  },
  ollama: {
    name: 'ollama',
    displayName: 'Ollama (Lokální)',
    description: 'Běží na vašem počítači, zdarma a soukromé',
    icon: '🦙',
    apiKeyRequired: false,
    localModel: true,
    capabilities: {
      code: true,
      design: false,
      reasoning: true,
    },
  },
  openai: {
    name: 'openai',
    displayName: 'OpenAI GPT-4',
    description: 'Všestranný asistent',
    icon: '🔵',
    apiKeyRequired: true,
    localModel: false,
    capabilities: {
      code: true,
      design: true,
      reasoning: true,
    },
  },
}

// Web Development Tool Commands
export const WEB_DEV_TOOLS = {
  v0: {
    name: 'v0.dev Style',
    description: 'Generuj React komponenty ve stylu v0.dev',
    prompt: 'Vytvoř React komponentu s shadcn/ui ve stylu v0.dev:',
    icon: '✨',
  },
  relume: {
    name: 'Relume Wireframe',
    description: 'Generuj wireframe layouty',
    prompt: 'Vytvoř wireframe layout pro web stránku:',
    icon: '🎨',
  },
  component: {
    name: 'UI Component',
    description: 'Vytvoř jednotlivou UI komponentu',
    prompt: 'Navrhni a implementuj UI komponentu:',
    icon: '🧩',
  },
  page: {
    name: 'Celá stránka',
    description: 'Generuj kompletní web stránku',
    prompt: 'Vytvoř kompletní responzivní web stránku:',
    icon: '📄',
  },
  style: {
    name: 'Styling',
    description: 'Pomoc s CSS/Tailwind',
    prompt: 'Pomoz se stylingem:',
    icon: '🎨',
  },
  debug: {
    name: 'Debug kódu',
    description: 'Najdi a oprav chyby',
    prompt: 'Najdi a oprav problém v kódu:',
    icon: '🐛',
  },
}

export const EXAMPLE_PROMPTS = [
  'Vytvoř pricing sekci s 3 tarify',
  'Udělej hero sekci s gradientem',
  'Navbar s mobilním menu',
  'Contact form s validací',
  'Dashboard s grafy',
  'Landing page pro SaaS',
]
