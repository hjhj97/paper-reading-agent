'use client'

import { useState } from 'react'
import PdfUploader from '@/components/PdfUploader'
import ModelSelector from '@/components/ModelSelector'
import SummaryDisplay from '@/components/SummaryDisplay'
import ChatInterface from '@/components/ChatInterface'

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o-mini')
  const [hasSummary, setHasSummary] = useState<boolean>(false)

  const handleUploadSuccess = (newSessionId: string) => {
    setSessionId(newSessionId)
    setHasSummary(false)
  }

  const handleSummaryGenerated = () => {
    setHasSummary(true)
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📄 Paper Reading Agent</h1>
        <p>AI-powered paper summarization and Q&A system</p>
      </div>

      <ModelSelector 
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />

      <PdfUploader onUploadSuccess={handleUploadSuccess} />

      {sessionId && (
        <>
          <SummaryDisplay
            sessionId={sessionId}
            selectedModel={selectedModel}
            onSummaryGenerated={handleSummaryGenerated}
          />
          
          {hasSummary && (
            <ChatInterface
              sessionId={sessionId}
              selectedModel={selectedModel}
            />
          )}
        </>
      )}
    </div>
  )
}

