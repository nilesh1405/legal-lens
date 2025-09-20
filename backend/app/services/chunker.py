from typing import List, Dict, Tuple


def estimate_tokens(text: str) -> int:
    # Simple heuristic: ~0.75 words per token
    words = len(text.split())
    return int(words / 0.75) if words else 0


def chunk_pages(pages: List[Tuple[int, str]]) -> List[Dict]:
    chunks: List[Dict] = []
    buffer: List[str] = []
    page_start = None
    token_count = 0
    for page_num, text in pages:
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            if page_start is None:
                page_start = page_num
            t = estimate_tokens(para)
            if token_count + t <= 800:
                buffer.append(para)
                token_count += t
            else:
                if token_count < 400 and buffer:
                    buffer.append(para)
                    token_count += t
                chunk_text = "\n\n".join(buffer).strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "page_start": page_start,
                        "page_end": page_num,
                        "tokens": token_count,
                    })
                buffer = [para]
                token_count = estimate_tokens(para)
                page_start = page_num
    # finalize
    if buffer:
        if chunks and estimate_tokens("\n\n".join(buffer)) < 250:
            # merge small last chunk
            prev = chunks[-1]
            prev["text"] = (prev["text"] + "\n\n" + "\n\n".join(buffer)).strip()
            prev["page_end"] = prev["page_end"]  # unchanged
            prev["tokens"] = estimate_tokens(prev["text"])
        else:
            chunks.append({
                "text": "\n\n".join(buffer).strip(),
                "page_start": page_start or 1,
                "page_end": pages[-1][0] if pages else 1,
                "tokens": estimate_tokens("\n\n".join(buffer)),
            })
    # Cap to 1000 tokens per chunk by naive split if needed
    normalized: List[Dict] = []
    for ch in chunks:
        if ch["tokens"] <= 1000:
            normalized.append(ch)
        else:
            parts = _split_large_chunk(ch["text"], 1000)
            for p in parts:
                normalized.append({
                    "text": p,
                    "page_start": ch["page_start"],
                    "page_end": ch["page_end"],
                    "tokens": estimate_tokens(p),
                })
    return [
        {**c, "chunk_id": i}
        for i, c in enumerate(normalized)
    ]


def _split_large_chunk(text: str, max_tokens: int) -> List[str]:
    words = text.split()
    out: List[str] = []
    buf: List[str] = []
    for w in words:
        buf.append(w)
        if estimate_tokens(" ".join(buf)) >= max_tokens:
            out.append(" ".join(buf))
            buf = []
    if buf:
        out.append(" ".join(buf))
    return out


