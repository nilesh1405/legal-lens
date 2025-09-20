import os
from typing import List, Dict, Optional
import numpy as np
from dotenv import load_dotenv
load_dotenv()

try:
    from pinecone import Pinecone
except Exception:  # pragma: no cover
    Pinecone = None  # type: ignore
    print("Pinecone not available, will use in-memory fallback")

class VectorDB:
    def __init__(self):
        print("Initializing VectorDB...")
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.env = os.getenv("PINECONE_ENV")
        self.index_name = os.getenv("PINECONE_INDEX", "legal-lens-index")
        self._client = None
        self._index = None
        self._memory: List[Dict] = []  # fallback in-memory store
        print(f"Pinecone API key: {'found' if self.api_key else 'not found'}")
        if self.api_key and Pinecone:
            try:
                self._client = Pinecone(api_key=self.api_key)
                self._index = self._client.Index(self.index_name)
                print(f"Connected to Pinecone index: {self.index_name}")
            except Exception as e:
                self._client = None
                self._index = None
                print(f"Pinecone init failed: {e}")
        else:
            print("Using in-memory vector store")

    def upsert(self, vectors: List[Dict]):
        print(f"Upserting {len(vectors)} vectors...")
        try:
            if self._index:
                items = [
                    {
                        "id": str(v["id"]),
                        "values": list(v["values"]),  # ensure it's a list
                        "metadata": v.get("metadata", {}),
                    }
                    for v in vectors
                ]
                self._index.upsert(items)
                print("Upserted to Pinecone successfully")
                return
            self._memory.extend(vectors)
            print("Upserted to in-memory store")
        except Exception as e:
            print(f"VectorDB upsert failed: {e}")
            raise RuntimeError(f"VectorDB upsert failed: {e}")

    def query(self,
              vector: List[float],
              top_k: int = 5,
              filter: Optional[Dict] = None) -> List[Dict]:
        print("Querying VectorDB...")
        # print(self._index)
        # print(self._index.describe_index_stats())
        #print(vector)
        if self._index:
            res = self._index.query(vector=vector, top_k=top_k, filter=filter, include_metadata=True)
            print("helolo")
            matches = res.get("matches", [])
            print(f"Found {len(matches)} matches in Pinecone")
            return [
                {
                    "id": m.get("id"),
                    "score": m.get("score"),
                    "metadata": m.get("metadata", {}),
                }
                for m in matches
            ]
        # simple cosine in-memory
        candidates = [m for m in self._memory if _match_filter(m.get("metadata", {}), filter)]
        q = np.array(vector)
        out: List[Dict] = []
        for c in candidates:
            v = np.array(c["values"])  # type: ignore
            cs = float(q @ v / (np.linalg.norm(q) * np.linalg.norm(v) + 1e-9))
            out.append({"id": c["id"], "score": cs, "metadata": c.get("metadata", {})})
        out.sort(key=lambda x: x["score"], reverse=True)
        print(f"Found {len(out)} matches in-memory")
        return out[:top_k]

    def delete_by_doc(self, doc_id: str):
        print(f"Deleting vectors for doc_id={doc_id}...")
        if self._index:
            self._index.delete(filter={"doc_id": doc_id})
            print("Deleted from Pinecone index")
            return
        before = len(self._memory)
        self._memory = [m for m in self._memory if m.get("metadata", {}).get("doc_id") != doc_id]
        after = len(self._memory)
        print(f"Deleted {before - after} vectors from in-memory store")


def _match_filter(meta: Dict, flt: Optional[Dict]) -> bool:
    if not flt:
        return True
    for k, v in flt.items():
        if meta.get(k) != v:
            return False
    return True
