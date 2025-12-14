import json
from pathlib import Path
<<<<<<< HEAD
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
=======

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

EMBEDDINGS_PATH = Path("module_b/assets_embeddings.json")
COLLECTION_NAME = "assets"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


def main() -> None:
    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(f"Missing {EMBEDDINGS_PATH}. Run generate_embeddings.py first.")

    data = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    if not data:
        raise RuntimeError("assets_embeddings.json is empty.")

    dim = len(data[0]["embedding"])
    print(f"Embedding dimension: {dim}")

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"Recreated collection: {COLLECTION_NAME}")

    points = []
    for idx, item in enumerate(data):
        points.append(
            PointStruct(
                id=idx,
                vector=item["embedding"],
                payload={
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "category": item.get("category", ""),
                    "style": item.get("style", ""),
                    "preview_url": item.get("preview_url", ""),
                    "freepik_url": item.get("freepik_url", ""),
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Upserted {len(points)} points into Qdrant.")
>>>>>>> origin/main


if __name__ == "__main__":
    main()