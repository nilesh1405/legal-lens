import os
from typing import Optional
from supabase import create_client
from dotenv import load_dotenv


SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "legal-lens-uploads")
load_dotenv()

def _client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase credentials missing: SUPABASE_URL or SUPABASE_KEY")
    return create_client(url, key)


def upload_pdf(user_id: str, doc_id: str, filename: str, data: bytes) -> str:
    path = f"{user_id}/{doc_id}.pdf"
    client = _client()
    
    try:

        res = client.storage.from_(SUPABASE_BUCKET).update(
        path=path,
        file=data,
            file_options={"contentType": "application/pdf"},
        )
    except Exception as e:
        raise RuntimeError(f"Supabase upload failed: {e}")

    if hasattr(res, "error") and res.error:
        raise RuntimeError(f"Supabase upload failed: {res.error}")

    return path



def delete_pdf(user_id: str, doc_id: str) -> None:
    path = f"{user_id}/{doc_id}.pdf"
    client = _client()
    client.storage.from_(SUPABASE_BUCKET).remove([path])


