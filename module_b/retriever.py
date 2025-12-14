"""
Asset Retriever for Sketch & Search Hackathon

This module wraps Qdrant vector search and returns enriched asset metadata.

Returned fields include:
- preview_url: Online preview image URL (from Freepik if available)
- local_preview: Local preview image path (if present)
- freepik_url / freepik_title / licenses: Provenance fields for guardrails scoring
"""

from pathlib import Path
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class AssetRetriever:
    """
    3D Asset Retriever

    Usage:
        from module_b.retriever import AssetRetriever

        retriever = AssetRetriever()
        results = retriever.search("metallic sphere on dark background")

        for asset in results:
            print(asset["preview_url"])
            print(asset["freepik_url"])
            print(asset["licenses"])
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "assets",
        previews_dir: str = None,
    ):
        """
        Initialize retriever.

        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Qdrant collection name
            previews_dir: Optional local previews directory
        """
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = collection_name

        # Local preview directory (default: module_b/data/assets/previews)
        if previews_dir:
            self.previews_dir = Path(previews_dir)
        else:
            self.previews_dir = Path(__file__).parent / "data" / "assets" / "previews"

    def _get_local_preview(self, asset_id: str, asset_name: str) -> str:
        """
        Return local preview path if it exists.

        Expected filename format:
            asset_001_sphere.png
        """
        filename = f"{asset_id}_{asset_name.lower().replace(' ', '_')}.png"
        filepath = self.previews_dir / filename
        return str(filepath) if filepath.exists() else ""

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search matching assets.

        Args:
            query: Text description such as "metallic sphere on dark background"
            top_k: Number of results to return

        Returns:
            List of matched asset dicts including score and preview URLs.
        """
        # Encode query into a vector
        query_vector = self.model.encode(query).tolist()

        # Search in Qdrant
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
        )

        matched_assets: List[Dict[str, Any]] = []

        for result in results.points:
            payload = result.payload or {}

            asset_id = payload.get("id", "")
            asset_name = payload.get("name", "")

            # Prefer local preview if available, otherwise fall back to online preview URL
            local_preview = self._get_local_preview(asset_id, asset_name)
            preview_url = payload.get("preview_url", "")

            asset: Dict[str, Any] = {
                "id": asset_id,
                "name": asset_name,
                "description": payload.get("description", ""),
                "category": payload.get("category", ""),
                "style": payload.get("style", ""),
                "tags": payload.get("tags", []),

                # Old field may exist in some payloads; keep it for backward compatibility
                "freepik_id": payload.get("freepik_id"),

                # Enriched Freepik provenance fields (from assets.enriched.json / upload script)
                "freepik_resolved": payload.get("freepik_resolved", False),
                "freepik_resource_id": payload.get("freepik_resource_id"),
                "freepik_title": payload.get("freepik_title", ""),
                "freepik_url": payload.get("freepik_url", ""),
                "licenses": payload.get("licenses", []),

                # Previews
                "preview_url": preview_url,
                "local_preview": local_preview,

                # Similarity score (cosine)
                "score": round(float(result.score), 4),
            }

            matched_assets.append(asset)

        return matched_assets

    def search_shot(self, shot_description: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Search assets for a single shot (for Module A).

        Returns:
            {
              "shot_description": "...",
              "matched_assets": [...]
            }
        """
        assets = self.search(shot_description, top_k)
        return {
            "shot_description": shot_description,
            "matched_assets": assets,
        }

    def search_multiple_shots(self, shots: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search assets for multiple shots.
        """
        return [self.search_shot(shot, top_k) for shot in shots]


# ========== Quick test ==========
if __name__ == "__main__":
    print("=" * 60)
    print("Asset Retriever Test")
    print("=" * 60)

    retriever = AssetRetriever()

    test_queries = [
        "shiny metallic sphere",
        "colorful gradient background",
        "glass transparent crystal",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        results = retriever.search(query, top_k=3)

        for i, asset in enumerate(results, 1):
            print(f"  {i}. {asset['name']} (score: {asset['score']})")

            if asset.get("local_preview"):
                print(f"     local_preview: {asset['local_preview']}")
            else:
                preview = asset.get("preview_url", "")
                print(f"     preview_url: {preview[:80]}..." if preview else "     preview_url: (empty)")

            freepik_url = asset.get("freepik_url", "")
            if freepik_url:
                print(f"     freepik_url: {freepik_url}")

            licenses = asset.get("licenses", [])
            if licenses:
                print(f"     licenses: {licenses}")
            else:
                print("     licenses: []")

    print("\n" + "=" * 60)
    print("✅ Retriever ready!")