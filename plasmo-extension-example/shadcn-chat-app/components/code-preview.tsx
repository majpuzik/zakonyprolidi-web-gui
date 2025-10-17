"use client"

import { useState } from "react"
import { Check, Copy, Download, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CodePreviewProps {
  code: string
  language?: string
  title?: string
  preview?: boolean
}

export function CodePreview({ code, language = "tsx", title, preview = true }: CodePreviewProps) {
  const [copied, setCopied] = useState(false)
  const [showPreview, setShowPreview] = useState(preview)

  const copyCode = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadCode = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || 'component'}.${language}`
    a.click()
    URL.revokeObjectURL(url)
  }

  const openInNewTab = () => {
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body class="bg-gray-50">
  <div id="root"></div>
  <script type="text/babel">
    ${code}

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>
    `
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  }

  return (
    <div className="my-4 rounded-lg border bg-white overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-gray-600">{language}</span>
          {title && <span className="text-sm font-medium">{title}</span>}
        </div>
        <div className="flex gap-1">
          {preview && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowPreview(!showPreview)}
              className="h-7 text-xs"
            >
              {showPreview ? 'Skrýt náhled' : 'Zobrazit náhled'}
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={openInNewTab}
            className="h-7 px-2"
          >
            <ExternalLink className="h-3.5 w-3.5" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={downloadCode}
            className="h-7 px-2"
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={copyCode}
            className="h-7 px-2"
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-green-600" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </Button>
        </div>
      </div>

      {showPreview && preview && (
        <div className="p-4 bg-white border-b">
          <div className="rounded border bg-gray-50 p-4">
            <iframe
              srcDoc={`
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  ${code.includes('function') || code.includes('const') ?
    `<div id="root"></div>
     <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
     <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
     <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
     <script type="text/babel">
       ${code}
       if (typeof App !== 'undefined') {
         const root = ReactDOM.createRoot(document.getElementById('root'));
         root.render(<App />);
       }
     </script>` :
    code}
</body>
</html>
              `}
              className="w-full h-96 border-0"
              sandbox="allow-scripts"
              title="Preview"
            />
          </div>
        </div>
      )}

      <pre className="p-4 overflow-x-auto text-sm bg-gray-900 text-gray-100">
        <code>{code}</code>
      </pre>
    </div>
  )
}
