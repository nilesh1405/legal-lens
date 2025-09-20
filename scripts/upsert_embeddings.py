import json
import sys

def main(chunks_json: str):
    data = json.loads(open(chunks_json, 'r', encoding='utf-8').read())
    print(f"Upserting {len(data.get('chunks', []))} chunks (mock)")

if __name__ == "__main__":
    main(sys.argv[1])


