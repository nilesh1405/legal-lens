import React, { useState } from 'react'
import axios from 'axios'

type Props = {
  onUploaded?: (docId: string) => void
}

export default function UploadPanel({ onUploaded }: Props) {
  const [files, setFiles] = useState<FileList | null>(null)
  const [category, setCategory] = useState('loan')
  const [userId, setUserId] = useState('demo-user')
  const [status, setStatus] = useState<string | null>(null)

  async function handleUpload() {
    if (!files || files.length === 0) return

    const form = new FormData()
    Array.from(files).forEach(f => form.append('files', f))
    form.append('category', category)
    form.append('user_id', userId)

    setStatus('Uploading...')
    try {
      const { data } = await axios.post('/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      })

      // Supabase se aa raha response
      if (data?.doc_id) {
        setStatus(`✅ Uploaded & processed (${data.chunks_count} chunks)`)
        onUploaded?.(data.doc_id)
      } else {
        setStatus('⚠️ Upload succeeded but no doc_id returned')
      }
    } catch (e: any) {
      console.error(e)
      setStatus('❌ Upload failed')
    }
  }

  return (
    <div className="space-y-3">
      <div className="muted">Upload PDF and select category</div>

      <div className="grid grid-cols-2 gap-3">
        <select
          className="input"
          value={category}
          onChange={e => setCategory(e.target.value)}
        >
          <option value="loan">Loan</option>
          <option value="rental">Rental</option>
          <option value="tos">ToS</option>
        </select>
        <input
          type="text"
          className="input"
          value={userId}
          onChange={e => setUserId(e.target.value)}
          placeholder="User ID"
        />
      </div>

      <label className="block">
        <span className="sr-only">Choose files</span>
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={e => setFiles(e.target.files)}
          className="block w-full text-sm text-white/80 file:mr-4 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-white/10 file:text-white hover:file:bg-white/20 transition"
        />
      </label>

      <button
        onClick={handleUpload}
        className="btn-primary relative overflow-hidden"
        disabled={!files || files.length === 0}
      >
        <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
        Upload
      </button>

      {status && <div className="muted">{status}</div>}
    </div>
  )
}
