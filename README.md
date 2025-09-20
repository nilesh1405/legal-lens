# LegalLens

Hackathon-ready RAG + Clause-Diff + Risk Scorer.

## Monorepo Structure

```
legal-lens/
├─ frontend/
├─ backend/
├─ infra/
├─ scripts/
├─ seed_data/
└─ README.md
```

## Quick Start (Local Dev)

1) Prereqs: Python 3.11, Node 18+, Docker, Git.

2) Copy env example and fill values:

```
cp .env.example .env
```

3) Backend (FastAPI):

```
cd backend
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

4) Frontend (Next.js):

```
cd frontend
npm install
npm run dev
```

Local dev uses safe fallbacks if API keys are missing (mock embeddings/vector store, local file storage).

## Deploy (High Level)

- Backend → Cloud Run (Docker). See `infra/cloudrun-deploy.sh`.
- Frontend → Vercel (connect GitHub, set env vars).

## Datasets (seed)

Place curated samples under `seed_data/{loan,rental,tos}`. See citations at bottom.

## Scripts

- `scripts/extract_chunks.py` — PDF → chunks (JSON)
- `scripts/upsert_embeddings.py` — chunks → Gemini embeddings → Pinecone
- `scripts/seed_category_db.py` — seed category corpora

Seed sample categories (place your .txt excerpts inside):

```
python scripts/seed_category_db.py --category loan --dir seed_data/loan
```

## Env Vars

See `.env.example` for all required variables.

Required for full functionality: `GEMINI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENV`, `GCS_BUCKET`.
Without keys, app runs with local mock embedding/vector store and no GCS.

## Security & Privacy

- Do not commit secrets. `.env`, key files are gitignored.
- GCS bucket private with signed URLs.
- DELETE endpoint wipes GCS + Pinecone + DB rows.

## Citations

- CUAD (Hugging Face / GitHub) — theatticusproject/cuad
- ACORD (Atticus Clause Retrieval Dataset) — atticus-project
- ContractNLI — stanfordnlp.github.io
- MAUD — atticus-project
- MCC — mcc.law.stanford.edu

## Demo Script

1) Upload `seed_data/loan/unusual_prepayment.pdf` (provided by team at demo time).
2) Ask: "Is there a prepayment penalty?"
3) Inspect sources, clause diffs, risk badge.
4) Export PDF report.
5) Delete data.

### Testing Checklist

- POST /upload with small pdf → returns chunks_count > 0
- POST /ask with doc_ids → returns sources including user doc
- Risk logic: clause containing "penalty" yields High (to be enabled)
- DELETE /docs/{doc_id} wipes vectors
- POST /export returns a PDF


"# legal-lens" 
