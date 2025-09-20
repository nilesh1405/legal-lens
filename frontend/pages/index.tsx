import React, { useState } from 'react'
import UploadPanel from '../components/UploadPanel'
import QueryPanel from '../components/QueryPanel'
import AnswerCard from '../components/AnswerCard'
import ClauseDiffViewer from '../components/ClauseDiffViewer'
import ExportReportButton from '../components/ExportReportButton'
import type { AskResponse } from '../utils/types'

export default function Home() {
  const [docIds, setDocIds] = useState<string[]>([])
  const [answer, setAnswer] = useState<AskResponse | undefined>()
  const [activeDocId, setActiveDocId] = useState<string | undefined>()
  return (
    <main className="min-h-screen p-6 md:p-10">
      <header className="max-w-7xl mx-auto mb-6 md:mb-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-indigo-600/90 shadow-lg shadow-indigo-500/20 animate-float" />
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">LegalLens</h1>
          </div>
          <div className="hidden md:flex items-center gap-2 text-white/70">
            <span className="hidden sm:inline">AI-powered legal document insights</span>
          </div>
        </div>
      </header>

      <section className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <div className="space-y-4">
          <div className="glass-card p-4 md:p-5">
            <div className="card-title mb-2">Upload</div>
            <UploadPanel onUploaded={(id)=> { setDocIds((prev)=> [...prev, id]); setActiveDocId(id); }} />
          </div>
        </div>

        <div className="md:col-span-1">
          <div className="glass-card p-4 md:p-5 h-full">
            <div className="card-title mb-2">Ask</div>
            <QueryPanel docIds={docIds} category='loan' onResult={setAnswer} />
          </div>
        </div>

        <div className="md:col-span-1">
          <div className="space-y-4">
            <AnswerCard data={answer} />
            <ClauseDiffViewer diffs={answer?.clause_differences} />
            <div className="glass-card p-4 md:p-5 flex justify-end">
              <ExportReportButton docId={activeDocId} analysis={answer} />
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}


