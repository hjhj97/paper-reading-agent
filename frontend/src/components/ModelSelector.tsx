'use client'

import { useState, useEffect } from 'react'
import { api, ModelInfo } from '@/lib/api'

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export default function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const modelList = await api.getModels()
        setModels(modelList)
      } catch (err) {
        console.error('Failed to fetch models:', err)
        // Set default models as fallback
        setModels([
          { id: 'gpt-4o-mini', name: 'GPT-4o Mini', is_default: true },
          { id: 'gpt-5-mini', name: 'GPT-5 Mini', is_default: false },
        ])
      } finally {
        setIsLoading(false)
      }
    }

    fetchModels()
  }, [])

  return (
    <div className="card">
      <h2>🤖 Select AI Model</h2>
      
      {isLoading ? (
        <p className="loading">Loading models...</p>
      ) : (
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} {model.is_default ? '(Default)' : ''}
            </option>
          ))}
        </select>
      )}
    </div>
  )
}

