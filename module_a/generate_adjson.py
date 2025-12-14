import json
import os
from datetime import datetime
from typing import Tuple, Dict, Any, List

# This is a minimal Module A stub:
# - Generates a playable multi-shot adJson (v1-compatible)
# - Generates shot_queries for Module B retrieval
# - Does NOT call Gemini yet (you can replace the stub later)


def generate_shot_plan_stub(brief: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Produce:
      1) adJson: 3-shot version using the existing C renderer schema.
      2) shot_queries: one query_text per shot for Module B retrieval.
    """

    # --- 3-shot adJson (9 seconds total: 3s + 3s + 3s) ---
    adjson: Dict[str, Any] = {
        "shots": [
            # Shot 1: Product reveal (clean, minimal)
            {
                "id": 1,
                "duration": 3000,
                "camera": {"movement": "slow-zoom-in", "angle": "slightly-top-down"},
                "elements": [
                    {"id": "track", "type": "track-layer"},
                    {
                        "id": "product",
                        "type": "bottle",
                        "motion": "yaw",
                        "position": {"x": 50, "y": 52},
                        "presetPosition": "pos-bottle-center",
                        "asset": None,
                    },
                    {
                        "id": "platform",
                        "type": "bottle-platform",
                        "parent": "product",
                        "asset": None,
                    },
                    {
                        "id": "sign1",
                        "type": "sign",
                        "motion": "spin-slow",
                        "presetPosition": "pos-sign-1",
                        "asset": None,
                    },
                    {
                        "id": "tree1",
                        "type": "tree",
                        "motion": None,
                        "presetPosition": "pos-tree-1",
                        "asset": None,
                    },
                ],
            },
            # Shot 2: Playful world motion (more props)
            {
                "id": 2,
                "duration": 3000,
                "camera": {"movement": "slow-zoom-in", "angle": "slightly-top-down"},
                "elements": [
                    {"id": "track", "type": "track-layer"},
                    {
                        "id": "product",
                        "type": "bottle",
                        "motion": "yaw",
                        "position": {"x": 50, "y": 52},
                        "presetPosition": "pos-bottle-center",
                        "asset": None,
                    },
                    {
                        "id": "wheelRight",
                        "type": "ferris-wheel",
                        "motion": "rotate-wheel",
                        "presetPosition": "pos-wheel-right",
                        "asset": None,
                    },
                    {
                        "id": "canLoop",
                        "type": "can-on-track",
                        "motion": "loop-track",
                        "asset": None,
                    },
                    {
                        "id": "person1",
                        "type": "person",
                        "motion": "sway",
                        "presetPosition": "pos-person-1",
                        "asset": None,
                    },
                    {
                        "id": "person2",
                        "type": "person",
                        "motion": "sway",
                        "presetPosition": "pos-person-2",
                        "asset": None,
                    },
                ],
            },
            # Shot 3: Hero finish (close-up vibe, pedestal + crystal)
            {
                "id": 3,
                "duration": 3000,
                "camera": {"movement": "slow-zoom-in", "angle": "slightly-top-down"},
                "elements": [
                    {"id": "track", "type": "track-layer"},
                    {
                        "id": "product",
                        "type": "bottle",
                        "motion": "yaw",
                        "position": {"x": 50, "y": 52},
                        "presetPosition": "pos-bottle-center",
                        "asset": None,
                    },
                    {
                        "id": "platform",
                        "type": "bottle-platform",
                        "parent": "product",
                        "asset": None,
                    },
                    {
                        "id": "soloCan",
                        "type": "solo-can",
                        "motion": "rise-spin",
                        "presetPosition": "pos-solo-can-left",
                        "asset": None,
                    },
                    {
                        "id": "tree3",
                        "type": "tree",
                        "motion": None,
                        "presetPosition": "pos-tree-3",
                        "asset": None,
                    },
                    {
                        "id": "sign2",
                        "type": "sign",
                        "motion": "spin-slow",
                        "presetPosition": "pos-sign-2",
                        "asset": None,
                    },
                ],
            },
        ]
    }

    # --- Shot queries for Module B ---
    # Note: B currently accepts text queries (it encodes queries internally).
    # We keep a placeholder embedding field for future compatibility.
    shot_queries: Dict[str, Any] = {
        "shots": [
            {
                "shot_id": 1,
                "query_text": (
                    f"{brief}. Shot 1: product reveal, clean dreamy futuristic mini-world, "
                    "soft pastel, minimal 3D, gradient background, elegant shapes, gentle motion"
                ),
                "keywords": ["product reveal", "dreamy", "futuristic", "mini-world", "minimal 3D", "gradient background"],
                "embedding": [0.01] * 64,
            },
            {
                "shot_id": 2,
                "query_text": (
                    f"{brief}. Shot 2: playful motion, ferris wheel, looping can, "
                    "geometric shapes, glossy 3D props, fun mini-world, soft motion"
                ),
                "keywords": ["playful", "ferris wheel", "looping", "geometric", "glossy 3D", "mini-world"],
                "embedding": [0.01] * 64,
            },
            {
                "shot_id": 3,
                "query_text": (
                    f"{brief}. Shot 3: hero finish, pedestal, crystal, premium clean 3D, "
                    "soft glow, minimal background, product spotlight"
                ),
                "keywords": ["hero finish", "pedestal", "crystal", "premium", "clean 3D", "spotlight"],
                "embedding": [0.01] * 64,
            },
        ]
    }

    return adjson, shot_queries


def main() -> None:
    brief = os.environ.get("BRIEF", "").strip()
    if not brief:
        brief = "Promote a beverage bottle in a dreamy mini-world style 3D ad."

    adjson, shot_queries = generate_shot_plan_stub(brief)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_ad = f"module_a/out/adJson.generated.{ts}.json"
    out_q = f"module_a/out/shot_queries.{ts}.json"

    os.makedirs("module_a/out", exist_ok=True)

    with open(out_ad, "w", encoding="utf-8") as f:
        json.dump(adjson, f, ensure_ascii=False, indent=2)

    with open(out_q, "w", encoding="utf-8") as f:
        json.dump(shot_queries, f, ensure_ascii=False, indent=2)

    print("✅ wrote:", out_ad)
    print("✅ wrote:", out_q)


if __name__ == "__main__":
    main()