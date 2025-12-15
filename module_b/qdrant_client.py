import os
import math
from typing import List, Dict, Any, Tuple

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
except Exception:
    QdrantClient = None
    rest = None


def _toy_embed(text: str, dim: int = 8) -> List[float]:
    # Deterministic toy embedding so demo is runnable without external model calls
    vals = [0.0] * dim
    for i, ch in enumerate(text.encode("utf-8")):
        vals[i % dim] += (ch % 31) / 31.0
    norm = math.sqrt(sum(v*v for v in vals)) or 1.0
    return [v / norm for v in vals]


def _cosine(a: List[float], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))


def qdrant_topk_fallback(query: str, candidates: List[Dict[str, Any]], k: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    qv = _toy_embed(query)
    scored = []
    for c in candidates:
        av = _toy_embed(c["asset_id"])
        s = _cosine(qv, av)
        scored.append({"asset_id": c["asset_id"], "score": float(s), "source": c.get("source", "unknown")})
    scored.sort(key=lambda x: x["score"], reverse=True)
    topk = scored[:k]
    selected = topk[0] if topk else {"asset_id": None, "score": 0.0}
    return topk, selected


def qdrant_client() -> Any:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY", "")
    if QdrantClient is None:
        return None
    return QdrantClient(url=url, api_key=api_key if api_key else None)


def ensure_collection(client: Any, name: str = "assets", dim: int = 8) -> None:
    if client is None or rest is None:
        return
    try:
        client.get_collection(name)
    except Exception:
        client.create_collection(
            collection_name=name,
            vectors_config=rest.VectorParams(size=dim, distance=rest.Distance.COSINE),
        )
