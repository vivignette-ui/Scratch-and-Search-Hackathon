import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ADJSON_IN = Path("module_a/out/adJson.generated.json")
B_OUT = Path("module_a/out/shot_assets.json")
ADJSON_OUT = Path("module_a/out/adJson.with_assets.json")

<<<<<<< HEAD
=======

>>>>>>> origin/main
# Only apply image assets to these element types (keeps visuals coherent).
ASSET_TYPES = {
    "can-on-track",
    "solo-can",
    "ferris-wheel",
<<<<<<< HEAD
    # Add more later if needed:
=======
    # You can add more later if you want:
>>>>>>> origin/main
    # "sign",
    # "tree",
}

<<<<<<< HEAD
# When true, clears any asset fields for element types not in ASSET_TYPES.
# This prevents random visuals from showing up on elements that are not meant to be "asset-driven".
CLEAR_NON_ASSET_TYPES = True


def pick_asset_url(asset: Dict[str, Any]) -> Optional[str]:
    """
    Prefer online preview images for browser-based demos.
    local_preview is usually a local filesystem path and may not load in the browser.
    """
    return asset.get("preview_url") or asset.get("local_preview") or asset.get("freepik_url")


def build_asset_meta(asset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Keep a minimal, judge-friendly provenance payload to support:
    - Guardrails (license/source)
    - Search & Similarity transparency (score)
    """
    return {
        "id": asset.get("id"),
        "name": asset.get("name"),
        "score": asset.get("score"),
        "preview_url": asset.get("preview_url"),
        "local_preview": asset.get("local_preview"),
        "freepik_url": asset.get("freepik_url"),
        "freepik_title": asset.get("freepik_title"),
        "licenses": asset.get("licenses", []),
        "category": asset.get("category"),
        "style": asset.get("style"),
        "tags": asset.get("tags", []),
    }


=======

def pick_asset_url(asset: Dict[str, Any]) -> Optional[str]:
    # Prefer online preview images; local_preview may not exist on your machine.
    return asset.get("preview_url") or asset.get("local_preview") or asset.get("freepik_url")


>>>>>>> origin/main
def main() -> None:
    if not ADJSON_IN.exists():
        raise FileNotFoundError(f"Missing: {ADJSON_IN}")
    if not B_OUT.exists():
        raise FileNotFoundError(f"Missing: {B_OUT}")

    adjson = json.loads(ADJSON_IN.read_text(encoding="utf-8"))
    b_results: List[Dict[str, Any]] = json.loads(B_OUT.read_text(encoding="utf-8"))

    shots: List[Dict[str, Any]] = adjson.get("shots", [])
    if not shots:
        raise ValueError("adJson has no shots")

    # b_results should align with shots (one retrieval result per shot query)
    for i, shot in enumerate(shots):
        elements: List[Dict[str, Any]] = shot.get("elements", [])
        if not elements:
            continue

<<<<<<< HEAD
        matched_assets: List[Dict[str, Any]] = []
=======
        matched_assets = []
>>>>>>> origin/main
        if i < len(b_results):
            matched_assets = b_results[i].get("matched_assets", []) or []

        if not matched_assets:
<<<<<<< HEAD
            # Still clear non-asset types if configured (keeps output deterministic)
            if CLEAR_NON_ASSET_TYPES:
                for el in elements:
                    el["asset"] = el.get("asset") if el.get("type") in ASSET_TYPES else None
                    if el.get("type") not in ASSET_TYPES:
                        el.pop("asset_meta", None)
                        el.pop("asset_source", None)
=======
>>>>>>> origin/main
            continue

        asset_idx = 0
        for el in elements:
            # Never override product visuals for now
            if el.get("id") == "product" or el.get("type") == "bottle":
<<<<<<< HEAD
                el.pop("asset_meta", None)
                el.pop("asset_source", None)
                continue

            el_type = el.get("type")

            # Only apply assets to chosen types
            if el_type not in ASSET_TYPES:
                if CLEAR_NON_ASSET_TYPES:
                    el["asset"] = None
                el.pop("asset_meta", None)
                el.pop("asset_source", None)
                continue

            asset = matched_assets[asset_idx % len(matched_assets)]
            chosen_url = pick_asset_url(asset)

            el["asset"] = chosen_url
            el["asset_meta"] = build_asset_meta(asset)

            # Simple provenance label for the frontend/demo
            el["asset_source"] = "freepik" if asset.get("freepik_url") else ("local" if asset.get("local_preview") else "unknown")

=======
                continue

            # Only apply assets to chosen types
            if el.get("type") not in ASSET_TYPES:
                el["asset"] = None
                continue

            asset = matched_assets[asset_idx % len(matched_assets)]
            el["asset"] = pick_asset_url(asset)
>>>>>>> origin/main
            asset_idx += 1

    ADJSON_OUT.write_text(json.dumps(adjson, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {ADJSON_OUT}")


if __name__ == "__main__":
    main()