"use client"

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import { CodePreview } from '../code-preview'
import 'highlight.js/styles/github-dark.css'

interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight, rehypeRaw]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const language = match ? match[1] : ''
          const codeString = String(children).replace(/\n$/, '')

          // Pokud je to code block (ne inline), zobraz s CodePreview
          if (!inline && (language === 'tsx' || language === 'jsx' || language === 'html' || language === 'javascript' || language === 'js')) {
            return (
              <CodePreview
                code={codeString}
                language={language}
                preview={language === 'tsx' || language === 'jsx' || language === 'html'}
              />
            )
          }

          // Inline kód
          return (
            <code className={className} {...props}>
              {children}
            </code>
          )
        },
        pre({ children }) {
          // Pre tag nechceme duplikovat (už je v CodePreview)
          return <>{children}</>
        },
        // Styling pro ostatní markdown elementy
        h1({ children }) {
          return <h1 className="text-2xl font-bold mt-6 mb-4">{children}</h1>
        },
        h2({ children }) {
          return <h2 className="text-xl font-bold mt-5 mb-3">{children}</h2>
        },
        h3({ children }) {
          return <h3 className="text-lg font-semibold mt-4 mb-2">{children}</h3>
        },
        p({ children }) {
          return <p className="mb-3 leading-relaxed">{children}</p>
        },
        ul({ children }) {
          return <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>
        },
        ol({ children }) {
          return <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>
        },
        li({ children }) {
          return <li className="ml-4">{children}</li>
        },
        a({ href, children }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {children}
            </a>
          )
        },
        blockquote({ children }) {
          return (
            <blockquote className="border-l-4 border-gray-300 pl-4 italic my-3 text-gray-700">
              {children}
            </blockquote>
          )
        },
        strong({ children }) {
          return <strong className="font-bold">{children}</strong>
        },
        em({ children }) {
          return <em className="italic">{children}</em>
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
