import React, { useState } from 'react'
import api from '../utils/api'
import type { AskResponse } from '../utils/types'

type Props = { docId?: string, analysis?: AskResponse }

export default function ExportReportButton({analysis }: Props) {
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function exportPdf() {
    if (!analysis) return
    
    setIsExporting(true)
    setError(null)
    
    try {
      const docId = crypto.randomUUID()  // generate new docId
      console.log('Exporting report with docId:', docId)
      
      const { data } = await api.post(
        '/export',
        { doc_id: docId, analysis },
        { 
          responseType: 'blob',
          timeout: 30000 // 30 second timeout
        }
      )
      
      console.log('Export response received:', data)
      
      const blob = new Blob([data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `legal-lens-report-${docId}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      console.log('PDF download initiated successfully')
    } catch (err: any) {
      console.error('Export failed:', err)
      setError(err.response?.data?.detail || err.message || 'Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }
  
  return (
    <div className="space-y-2">
      <button 
        onClick={exportPdf} 
        className="btn-primary" 
        disabled={!analysis || isExporting}
      >
        {isExporting ? 'Exporting...' : 'Export Report'}
      </button>
      {error && (
        <div className="text-red-500 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}


