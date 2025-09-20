import os
from typing import List
import numpy as np
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover
    genai = None
    types = None

# Set to match Pinecone index
EMBED_DIM = 768  

# Keep global client
client = None

def init_gemini() -> bool:
    global client
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and genai:
        client = genai.Client(api_key=api_key)
        return True
    return False


def embed_texts(texts: List[str]) -> List[List[float]]:
    global client
    if client and genai:
        try:
            result = client.models.embed_content(
                model="models/embedding-001",   # ✅ correct model name
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM),
            )
            return [e.values for e in result.embeddings]
        except Exception as e:
            print(f"Error embedding via Gemini: {e}")
            return [_mock_embed(t) for t in texts]
    # fallback
    return [_mock_embed(t) for t in texts]


def _mock_embed(text: str) -> List[float]:
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    v = rng.normal(size=EMBED_DIM).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-9)
    return v.tolist()
