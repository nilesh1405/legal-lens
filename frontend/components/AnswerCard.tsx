import React from 'react'
import type { AskResponse } from '../utils/types'
import ReactMarkdown from 'react-markdown'

type Props = { data?: AskResponse }

export default function AnswerCard({ data }: Props) {
  if (!data) return <div className="rounded-2xl border p-4 text-gray-500">No answer yet.</div>
  return (
    <div className="rounded-2xl border p-4 space-y-3">
      <div className="font-semibold">Answer</div>
      {/* use ReactMarkdown to render markdown as proper HTML */}
      <div className="prose whitespace-pre-wrap">
        <ReactMarkdown>{data.answer}</ReactMarkdown>
      </div>
      <div className="text-sm">
        Risk: <b>{data.risk.level}</b> ({Math.round(data.risk.score * 100)}%)
      </div>
    </div>
  )
}



