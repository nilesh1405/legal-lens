import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from ..services.pdf_extractor import extract_text_by_page
from ..services.chunker import chunk_pages
from ..services.embeddings import embed_texts
from ..services.vector_db import VectorDB
from ..services.storage import upload_pdf
import logging

from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client()

router = APIRouter(prefix="", tags=["upload"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload(
    files: List[UploadFile] = File(...),
    category: str = Form(...),
    user_id: str = Form(...),
):
    try:
        if not files:
            return JSONResponse({"error": "no files"}, status_code=400)

        doc_id = str(uuid.uuid4())
        all_chunks = []

        # Read first file
        primary_file = files[0]
        pdf_bytes = await primary_file.read()

        # Upload original PDF to Supabase
        try:
            path = upload_pdf(
                user_id=user_id,
                doc_id=doc_id,
                filename=primary_file.filename or f"{doc_id}.pdf",
                data=pdf_bytes,
            )
        except Exception as se:
            logger.exception("Supabase upload failed")
            return JSONResponse({"error": f"storage upload failed: {se}"}, status_code=400)

        # Extract, chunk & embed
        print("Extracting text from PDF...")
        pages = extract_text_by_page(pdf_bytes)
        print(f"Extracted {len(pages)} pages")

        print("Chunking pages...")
        chunks = chunk_pages(pages)
        print(f"Created {len(chunks)} chunks")
        all_chunks.extend(chunks)
        
        print("Generating embeddings...")


        texts = [c["text"] for c in all_chunks]

        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(output_dimensionality=768)  # set vector size
        )

        embeddings = [e.values for e in result.embeddings]

        print("Embedding length example:", len(embeddings[0]))
        print(f"Generated {len(embeddings)} embeddings")

        # Prepare vectors for VectorDB
        vdb = VectorDB()
        vectors = []
        for c, vec in zip(all_chunks, embeddings):
            vectors.append({
                "id": f"{doc_id}_chunk_{c['chunk_id']}",
                "values": vec,
                "metadata": {
                    "id": f"{doc_id}_chunk_{c['chunk_id']}",
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "category": category,
                    "page_start": c["page_start"],
                    "page_end": c["page_end"],
                    "chunk_id": c["chunk_id"],
                    "text": c["text"],
                    "source": "user",
                },
            })
        print(len(vectors[0]))

        # Upsert into VectorDB
        if vectors:
            print(f"Upserting {len(vectors)} vectors to VectorDB...")
            vdb.upsert(vectors)
            print("Upsert complete.")

        return JSONResponse({
            "status": "processed",
            "doc_id": doc_id,
            "chunks_count": len(all_chunks)
        })

    except Exception as e:
        logger.exception("Upload failed")
        return JSONResponse(
            {"error": str(e), "doc_id": doc_id if "doc_id" in locals() else None},
            status_code=500,
        )
