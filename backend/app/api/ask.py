from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.embeddings import embed_texts
from ..services.vector_db import VectorDB
from ..services.llm_client import generate_answer

USER_SIM_THRESHOLD = 0.55
TOP_K_USER = 5
TOP_M_CATEGORY = 3

router = APIRouter(prefix="", tags=["ask"])


class AskRequest(BaseModel):
    user_id: str
    doc_ids: List[str]
    question: str
    category: str


@router.post("/ask")
async def ask(payload: AskRequest):
    vdb = VectorDB()
    qvec = embed_texts([payload.question])[0]
    # user-first retrieval restricted to doc_ids
    sources = []
    for doc_id in payload.doc_ids:
        matches = vdb.query(vector=qvec, top_k=TOP_K_USER, filter={"doc_id": doc_id})
        for m in matches:
            m["metadata"]["similarity"] = m.get("score", 0)
            m["metadata"]["source"] = "user"
            sources.append(m["metadata"])
    sources.sort(key=lambda x: x.get("similarity", 0), reverse=True)
    user_top = sources[:TOP_K_USER]

    need_category = len(user_top) < 3 or (user_top and user_top[0].get("similarity", 0) < USER_SIM_THRESHOLD)
    category_add: List[dict] = []
    if need_category:
        cat_matches = vdb.query(vector=qvec, top_k=TOP_M_CATEGORY, filter={"category": payload.category})
        for m in cat_matches:
            md = m.get("metadata", {})
            md["similarity"] = m.get("score", 0)
            md["source"] = "category"
            category_add.append(md)

    merged = user_top + category_add
    # build prompt with top 3 user + top 2 category
    top_user = [m for m in merged if m.get("source") == "user"][:3]
    top_cat = [m for m in merged if m.get("source") == "category"][:2]

    def fmt_user(m):
        return f"1) [DOC:{m['doc_id']} | CHUNK:{m['chunk_id']} | PAGES:{m['page_start']}-{m['page_end']} | SIM:{m.get('similarity', 0):.2f}]\n{m['text']}"

    def fmt_cat(m):
        return f"1) [CATEGORY:{payload.category} | SRC:{m.get('doc_id','cat')} | CHUNK:{m.get('chunk_id','-')}]\n{m['text']}"

    prompt = (
    "SYSTEM: You are LegalLens, an assistant that analyzes legal agreements. "
    "Summarize what the uploaded contract says about repayment, interest, penalties, and obligations. "
    "Highlight risks and burdens for the borrower in simple language. "
    "If the document lacks details, say that clearly. "
    "You may state whether the terms seem strict, flexible, risky, or favorable, but DO NOT directly tell the user "
    "to take or not take the loan. "
    "Use subheadings for each section in **bold** format (for example: **Repayment:**, **Interest:**, **Penalties:**, **Obligations:**, **Action steps:**). "
    f"USER QUESTION:\n{payload.question}\n\n"
    "USER DOCUMENT CHUNKS (highest relevance first):\n" +
    ("\n\n".join([fmt_user(m) for m in top_user]) if top_user else "(none)") +
    "\n\nCATEGORY CONTEXT (optional, supporting only if user chunks insufficient):\n" +
    ("\n\n".join([fmt_cat(m) for m in top_cat]) if top_cat else "(none)") +
    "\n\nTASK:\n1) Answer the user's question concisely in plain English.\n"
    "2) If the user document lacks direct info, use category context and explicitly say 'Using category precedents:'.\n"
    "3) Provide a short 'Action steps:' section (2–4 bullet points) with the heading in **bold**.\n"
    "4) Output must be plain text only — no markdown formatting except for the bold subheadings.\n\nEND."
)



    answer = generate_answer(prompt)

    # Minimal risk scoring (keyword based); can be extended per spec
    risk = {"level": "Low", "score": 0.2}
    print(answer)

    return {
        "answer": answer,   # full clean text
        "risk": risk,
        "confidence": max([m.get("similarity", 0) for m in merged], default=0),
    }


