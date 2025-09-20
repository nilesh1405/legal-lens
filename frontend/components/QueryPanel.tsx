import React, { useState } from 'react'
import api from '../utils/api'
import type { AskResponse } from '../utils/types'

type Props = {
  docIds?: string[]
  category?: string
  onResult?: (res: AskResponse) => void
}

export default function QueryPanel({ docIds = [], category = 'loan', onResult }: Props) {
  const [q, setQ] = useState('Is there a prepayment penalty?')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  async function ask() {
    if (!q.trim()) return
    setLoading(true)
    setErr(null)
    try {
      const { data } = await api.post('/ask', {
        user_id: 'demo-user',
        doc_ids: docIds,
        question: q,
        category,
      })
      onResult?.(data)
    } catch (e: any) {
      setErr('Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      <textarea className="input min-h-[140px]" rows={5} value={q} onChange={e=> setQ(e.target.value)} placeholder="Ask about clauses, risks, penalties..." />
      <div className="flex items-center gap-2">
        <button onClick={ask} disabled={loading} className="btn-primary">
          {loading ? 'Asking...' : 'Ask'}
        </button>
        {!!docIds.length && <span className="muted">on {docIds.length} doc{docIds.length>1 ? 's' : ''}</span>}
      </div>
      {err && <div className="text-xs text-red-400">{err}</div>}
    </div>
  )
}


