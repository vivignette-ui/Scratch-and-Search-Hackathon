import json
import os
import time
from typing import Any, Dict, List, Optional

import requests

FREEPIK_BASE_URL = "https://api.freepik.com/v1"


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def freepik_search(query: str, api_key: str, content_type: str = "3d", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search Freepik assets by text query.

    Notes:
    - content_type may vary by API account/features.
    - If your API doesn't support a filter, we still get results by query.
    """
    url = f"{FREEPIK_BASE_URL}/resources"
    headers = {"x-freepik-api-key": api_key}

    params = {
        "term": query,
        "limit": limit,
    }

    # Try to pass a type filter (some Freepik configs support it; if not, Freepik may ignore it)
    # Common values people use: "vector", "photo", "psd", "3d"
    params["type"] = content_type

    resp = requests.get(url, headers=headers, params=params, timeout=25)

    if resp.status_code == 200:
        payload = resp.json()
        return payload.get("data", []) or []
    if resp.status_code in (401, 403):
        raise RuntimeError("Freepik API key is invalid or lacks permission.")
    if resp.status_code == 429:
        return []
    return []


def build_query(asset: Dict[str, Any]) -> str:
    """
    Build a robust search query from your asset metadata.
    """
    name = (asset.get("name") or "").strip()
    tags = asset.get("tags") or []
    if isinstance(tags, list):
        tags_part = " ".join([t for t in tags if isinstance(t, str)])
    else:
        tags_part = ""

    category = (asset.get("category") or "").strip()
    style = (asset.get("style") or "").strip()

    # Keep it short to avoid overly specific queries
    parts = [name, category, style, tags_part]
    parts = [p for p in parts if p]
    q = " ".join(parts)

    # Fallback
    if not q:
        q = "3d object"
    return q


def pick_best_hit(asset: Dict[str, Any], hits: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Pick the best hit by lightweight heuristic:
    - prefer items whose title contains the asset name
    - otherwise take the first hit
    """
    if not hits:
        return None

    asset_name = (asset.get("name") or "").lower().strip()
    if asset_name:
        for h in hits:
            title = (h.get("title") or "").lower()
            if asset_name in title:
                return h

    return hits[0]


def main() -> None:
    api_key = os.environ.get("FREEPIK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing FREEPIK_API_KEY. Set it via: export FREEPIK_API_KEY='...'")

    module_dir = os.path.dirname(__file__)
    assets_path = os.path.join(module_dir, "assets.json")
    assets: List[Dict[str, Any]] = load_json(assets_path)

    enriched: List[Dict[str, Any]] = []
    unresolved_count = 0

    for a in assets:
        query = build_query(a)
        hits = freepik_search(query=query, api_key=api_key, content_type="3d", limit=6)

        # Backoff if rate limited / empty
        if not hits:
            time.sleep(0.8)
            hits = freepik_search(query=query, api_key=api_key, content_type="3d", limit=6)

        best = pick_best_hit(a, hits)

        if not best:
            a["freepik_resolved"] = False
            a["freepik_search_query"] = query
            unresolved_count += 1
            enriched.append(a)
            continue

        # Normalize fields into your asset schema
        a["freepik_resolved"] = True
        a["freepik_search_query"] = query

        a["freepik_resource_id"] = best.get("id")
        a["freepik_title"] = best.get("title")
        a["freepik_url"] = best.get("url") or a.get("freepik_url")
        a["preview_url"] = best.get("preview_url") or a.get("preview_url")
        a["licenses"] = best.get("licenses", [])

        enriched.append(a)

        # Small pause to reduce rate limit risk
        time.sleep(0.25)

    out_path = os.path.join(module_dir, "assets.enriched.json")
    save_json(enriched, out_path)

    print(f"✅ wrote: {out_path}")
    if unresolved_count:
        print(f"⚠️ assets unresolved from Freepik Search API: {unresolved_count}")


if __name__ == "__main__":
    main()