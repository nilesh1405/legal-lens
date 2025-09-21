from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.embeddings import embed_texts
from ..services.vector_db import VectorDB
from ..services.llm_client import generate_answer
import asyncio

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

    # --- Retrieve user document chunks ---
    sources = []
    for doc_id in payload.doc_ids:
        matches = vdb.query(vector=qvec, top_k=TOP_K_USER, filter={"doc_id": doc_id})
        for m in matches:
            md = m.get("metadata", {})
            md["similarity"] = m.get("score", 0)
            md["source"] = "user"
            # Ensure text is present
            if "text" in md and md["text"].strip():
                sources.append(md)

    # Always include top user chunks (no similarity filtering)
    top_user = sources[:TOP_K_USER]

    # --- Retrieve category context only if user chunks < 3 ---
    category_add = []
    if len(top_user) < 3:
        cat_matches = vdb.query(vector=qvec, top_k=TOP_M_CATEGORY, filter={"category": payload.category})
        for m in cat_matches:
            md = m.get("metadata", {})
            md["similarity"] = m.get("score", 0)
            md["source"] = "category"
            if "text" in md and md["text"].strip():
                category_add.append(md)
    top_cat = category_add[:2]

    # --- Formatting functions ---
    def fmt_user(m):
        return f"1) [DOC:{m['doc_id']} | CHUNK:{m['chunk_id']} | PAGES:{m.get('page_start','-')}-{m.get('page_end','-')} | SIM:{m.get('similarity',0):.2f}]\n{m['text']}"

    def fmt_cat(m):
        return f"1) [CATEGORY:{payload.category} | SRC:{m.get('doc_id','cat')} | CHUNK:{m.get('chunk_id','-')}]\n{m['text']}"

    # --- Build prompt ---
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
        "3) Provide a short 'Action steps:' section (2-4 bullet points) with the heading in **bold**.\n"
        "4) Output must be plain text only — no markdown formatting except for the bold subheadings.\n\nEND."
    )

    # --- Async-safe LLM call ---
    answer = await asyncio.to_thread(generate_answer, prompt)

    # --- Risk scoring placeholder ---
    risk = {"level": "Low", "score": 0.2}

    return {
        "answer": answer,
        "risk": risk,
        "confidence": max([m.get("similarity", 0) for m in top_user + top_cat], default=0),
    }
