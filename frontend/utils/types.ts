export type SourceItem = {
  doc_id: string
  chunk_id: number
  page_range: string
  similarity: number
  source: 'user' | 'category'
  text_snippet: string
}

export type ClauseDiff = {
  user_chunk_id: number
  category_chunk_id: number
  distance: number
  unusual: boolean
  summary?: string
  risk?: { level: 'Low' | 'Medium' | 'High', rationale?: string }
  suggestion?: string
}

export type AskResponse = {
  answer: string
  sources: SourceItem[]
  clause_differences: ClauseDiff[]
  risk: { level: 'Low' | 'Medium' | 'High', score: number }
  confidence: number
}


