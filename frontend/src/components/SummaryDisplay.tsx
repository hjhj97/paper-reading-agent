'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface SummaryDisplayProps {
  sessionId: string
  selectedModel: string
  onSummaryGenerated: () => void
  autoSummarize?: boolean
  initialSummary?: string | null
}

export default function SummaryDisplay({ 
  sessionId, 
  selectedModel,
  onSummaryGenerated,
  autoSummarize = false,
  initialSummary = null
}: SummaryDisplayProps) {
  const [summary, setSummary] = useState<string>(initialSummary || '')
  const [customPrompt, setCustomPrompt] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string>('')
  const [rating, setRating] = useState<string>('')

  // Auto-summarize on mount if enabled and no existing summary
  useEffect(() => {
    if (autoSummarize && !initialSummary && !summary && !isGenerating) {
      handleGenerateSummary()
    }
  }, [autoSummarize, initialSummary])

  // Update summary if initialSummary changes
  useEffect(() => {
    if (initialSummary) {
      setSummary(initialSummary)
      onSummaryGenerated()
    }
  }, [initialSummary])

  const handleGenerateSummary = async () => {
    setIsGenerating(true)
    setError('')
    setSummary('')
    setRating('')

    try {
      const response = await api.summarize(
        sessionId,
        customPrompt || undefined,
        selectedModel
      )
      setSummary(response.summary)
      onSummaryGenerated()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate summary')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRate = async (ratingType: 'thumbs_up' | 'thumbs_down') => {
    try {
      await api.rate(sessionId, ratingType)
      setRating(ratingType)
    } catch (err: any) {
      console.error('Failed to rate:', err)
    }
  }

  return (
    <div className="card">
      <h2>📝 Paper Summary</h2>
      
      {error && <div className="error">{error}</div>}
      
      {isGenerating && (
        <div style={{ 
          textAlign: 'center', 
          padding: '2rem',
          background: '#f0f9ff',
          borderRadius: '4px',
          marginBottom: '1rem'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🤖</div>
          <p style={{ color: '#0369a1', fontWeight: 'bold' }}>Generating summary...</p>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>This may take a moment depending on the paper length.</p>
        </div>
      )}
      
      {!isGenerating && !summary && (
        <>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Custom Prompt (Optional):
            </label>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="Enter a custom prompt to guide the summarization (e.g., 'Focus on the methodology and results')..."
              disabled={isGenerating}
            />
          </div>
          
          <button
            onClick={handleGenerateSummary}
            disabled={isGenerating}
            style={{ marginBottom: '1.5rem' }}
          >
            Generate Summary
          </button>
        </>
      )}
      
      {summary && (
        <div>
          <div 
            className="markdown-content"
            style={{
              background: '#f9fafb',
              padding: '1.5rem',
              borderRadius: '4px',
              marginBottom: '1rem',
              lineHeight: '1.8'
            }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {summary}
            </ReactMarkdown>
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 'bold' }}>Rate this summary:</span>
            <button
              onClick={() => handleRate('thumbs_up')}
              style={{
                background: rating === 'thumbs_up' ? '#10b981' : '#6b7280',
                padding: '0.5rem 1rem'
              }}
            >
              👍 Good
            </button>
            <button
              onClick={() => handleRate('thumbs_down')}
              style={{
                background: rating === 'thumbs_down' ? '#ef4444' : '#6b7280',
                padding: '0.5rem 1rem'
              }}
            >
              👎 Not Good
            </button>
            {rating && (
              <span style={{ color: '#666', fontSize: '0.9rem' }}>
                Thank you for your feedback!
              </span>
            )}
          </div>
          
          <div style={{ marginTop: '1.5rem', borderTop: '1px solid #e5e7eb', paddingTop: '1rem' }}>
            <details>
              <summary style={{ cursor: 'pointer', color: '#2563eb', fontWeight: 'bold' }}>
                Regenerate with custom prompt
              </summary>
              <div style={{ marginTop: '1rem' }}>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Enter a custom prompt..."
                  disabled={isGenerating}
                />
                <button
                  onClick={handleGenerateSummary}
                  disabled={isGenerating}
                  style={{ marginTop: '0.5rem' }}
                >
                  Regenerate Summary
                </button>
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  )
}
