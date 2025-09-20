from typing import List, Tuple
import fitz  # PyMuPDF


def extract_text_by_page(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Returns list of (page_number starting at 1, text)
    """
    texts: List[Tuple[int, str]] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            texts.append((i + 1, _clean_text(text)))
    return texts


def _clean_text(text: str) -> str:
    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])


