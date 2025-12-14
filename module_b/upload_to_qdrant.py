import json
from pathlib import Path
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    module_dir = Path(__file__).parent

    # Prefer enriched metadata if it exists.
    assets_path = module_dir / "assets.enriched.json"
    if not assets_path.exists():
        assets_path = module_dir / "assets.json"

    embeddings_path = module_dir / "assets_embeddings.json"
    if not embeddings_path.exists():
        raise FileNotFoundError("assets_embeddings.json not found. Run generate_embeddings.py first.")

    assets: List[Dict[str, Any]] = load_json(assets_path)
    embeddings: List[Dict[str, Any]] = load_json(embeddings_path)

    # Map embeddings by id for quick lookup
    emb_map = {e["id"]: e["embedding"] for e in embeddings}

    client = QdrantClient(url="http://localhost:6333")

    collection_name = "assets"

    # Create collection if missing
    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    points: List[PointStruct] = []

    for idx, a in enumerate(assets):
        asset_id = a.get("id")
        if not asset_id or asset_id not in emb_map:
            continue

        vector = emb_map[asset_id]

        # Store rich metadata in payload for demo + guardrails
        payload = {
            "id": a.get("id"),
            "name": a.get("name"),
            "category": a.get("category"),
            "style": a.get("style"),
            "tags": a.get("tags", []),
            "description": a.get("description", ""),

            # Freepik fields (now real + resolved)
            "freepik_resolved": a.get("freepik_resolved", False),
            "freepik_resource_id": a.get("freepik_resource_id"),
            "freepik_title": a.get("freepik_title"),
            "freepik_url": a.get("freepik_url"),
            "preview_url": a.get("preview_url"),
            "licenses": a.get("licenses", []),
        }

        points.append(PointStruct(id=idx + 1, vector=vector, payload=payload))

    client.upsert(collection_name=collection_name, points=points)

    print(f"✅ Uploaded {len(points)} points to Qdrant collection '{collection_name}'")


if __name__ == "__main__":
    main()