from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.upload import router as upload_router
from .api.ask import router as ask_router
from .api.export import router as export_router
from fastapi import HTTPException
from .services.vector_db import VectorDB
from .services.storage import delete_pdf

app = FastAPI(title="LegalLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/docs-list")
async def docs_list():
    # Placeholder: not persisted yet
    return {"docs": []}

@app.delete("/docs/{doc_id}")
async def delete_doc(doc_id: str):
    try:
        VectorDB().delete_by_doc(doc_id)
        # user_id not tracked yet in memory; try best-effort delete path for demo
        # If you store user_id per doc in DB, fetch it and call delete_pdf(user_id, doc_id)
        return {"status": "deleted", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(export_router)


