import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ADJSON_IN = Path("module_a/out/adJson.generated.json")
B_OUT = Path("module_a/out/shot_assets.json")
ADJSON_OUT = Path("module_a/out/adJson.with_assets.json")


# Only apply image assets to these element types (keeps visuals coherent).
ASSET_TYPES = {
    "can-on-track",
    "solo-can",
    "ferris-wheel",
    # You can add more later if you want:
    # "sign",
    # "tree",
}


def pick_asset_url(asset: Dict[str, Any]) -> Optional[str]:
    # Prefer online preview images; local_preview may not exist on your machine.
    return asset.get("preview_url") or asset.get("local_preview") or asset.get("freepik_url")


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

        matched_assets = []
        if i < len(b_results):
            matched_assets = b_results[i].get("matched_assets", []) or []

        if not matched_assets:
            continue

        asset_idx = 0
        for el in elements:
            # Never override product visuals for now
            if el.get("id") == "product" or el.get("type") == "bottle":
                continue

            # Only apply assets to chosen types
            if el.get("type") not in ASSET_TYPES:
                el["asset"] = None
                continue

            asset = matched_assets[asset_idx % len(matched_assets)]
            el["asset"] = pick_asset_url(asset)
            asset_idx += 1

    ADJSON_OUT.write_text(json.dumps(adjson, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {ADJSON_OUT}")


if __name__ == "__main__":
    main()