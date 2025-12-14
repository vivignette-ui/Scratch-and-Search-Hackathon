import json
from pathlib import Path

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


if __name__ == "__main__":
    main()