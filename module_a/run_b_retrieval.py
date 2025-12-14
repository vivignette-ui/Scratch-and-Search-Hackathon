import json
from pathlib import Path

from module_b.retriever import AssetRetriever

INPUT_PATH = Path("module_a/out/shot_queries.json")
OUTPUT_PATH = Path("module_a/out/shot_assets.json")


def main() -> None:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    shots = payload.get("shots", [])
    shot_texts = [s.get("query_text", "") for s in shots if s.get("query_text")]

    retriever = AssetRetriever(collection_name="assets")
    results = retriever.search_multiple_shots(shot_texts, top_k=3)

    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()