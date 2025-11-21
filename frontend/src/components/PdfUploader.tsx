'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

interface PdfUploaderProps {
  onUploadSuccess: (sessionId: string) => void
}

export default function PdfUploader({ onUploadSuccess }: PdfUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError('')
        setSuccess('')
      } else {
        setError('Please select a PDF file')
        setFile(null)
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setIsUploading(true)
    setError('')
    setSuccess('')

    try {
      const response = await api.uploadPdf(file)
      setSuccess(response.message)
      onUploadSuccess(response.session_id)
      
      // Save session ID to localStorage
      localStorage.setItem('sessionId', response.session_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload PDF')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="card">
      <h2>📤 Upload Paper PDF</h2>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      
      <div style={{ marginBottom: '1rem' }}>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={isUploading}
        />
      </div>
      
      {file && (
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
        </p>
      )}
      
      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload & Process'}
      </button>
    </div>
  )
}

