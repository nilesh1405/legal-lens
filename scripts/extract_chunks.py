import json
import sys
from pathlib import Path

def main(pdf_path: str, out_path: str):
    # Placeholder chunk extraction; real logic in backend services
    chunks = [{"chunk_id": 0, "text": "Sample chunk", "page_start": 1, "page_end": 1}]
    Path(out_path).write_text(json.dumps({"chunks": chunks}, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])


