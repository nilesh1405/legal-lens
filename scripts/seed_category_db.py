import argparse
import json
from pathlib import Path

def main(category: str, directory: str):
    files = list(Path(directory).glob('*.txt'))
    print(f"Seeding category {category} with {len(files)} files (placeholder)")
    meta = [{"doc_id": f.stem, "category": category, "filename": f.name, "source": "seed"} for f in files]
    Path('seed_metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', required=True)
    parser.add_argument('--dir', required=True)
    args = parser.parse_args()
    main(args.category, args.dir)


