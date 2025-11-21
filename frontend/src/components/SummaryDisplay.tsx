'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

interface SummaryDisplayProps {
  sessionId: string
  selectedModel: string
  onSummaryGenerated: () => void
}

export default function SummaryDisplay({ 
  sessionId, 
  selectedModel,
  onSummaryGenerated 
}: SummaryDisplayProps) {
  const [summary, setSummary] = useState<string>('')
  const [customPrompt, setCustomPrompt] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string>('')
  const [rating, setRating] = useState<string>('')

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
        {isGenerating ? 'Generating Summary...' : 'Generate Summary'}
      </button>
      
      {summary && (
        <div>
          <div 
            style={{
              background: '#f9fafb',
              padding: '1.5rem',
              borderRadius: '4px',
              marginBottom: '1rem',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}
          >
            {summary}
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
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
        </div>
      )}
    </div>
  )
}

