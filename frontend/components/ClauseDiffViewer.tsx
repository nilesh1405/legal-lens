import React from 'react'
import type { ClauseDiff } from '../utils/types'

type Props = { diffs?: ClauseDiff[] }

export default function ClauseDiffViewer({ diffs = [] }: Props) {
  if (!diffs.length) return <div className="rounded-2xl border p-4 text-gray-500">No clause differences.</div>
  return (
    <div className="rounded-2xl border p-4 space-y-3">
      <div className="font-semibold">Clause Differences</div>
      {diffs.map((d,i)=> (
        <div key={i} className="border rounded p-3">
          <div className="text-sm">Unusual: <b>{d.unusual ? 'Yes' : 'No'}</b> (dist {d.distance.toFixed(2)})</div>
          {d.summary && <div className="text-sm mt-1">{d.summary}</div>}
          {d.suggestion && <div className="text-sm mt-1 italic">Suggested: {d.suggestion}</div>}
          {d.risk && <div className="text-xs mt-1">Risk: {d.risk.level} {d.risk.rationale ? `- ${d.risk.rationale}` : ''}</div>}
        </div>
      ))}
    </div>
  )
}


