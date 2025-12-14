import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
from sentence_transformers import SentenceTransformer


# -----------------------------
# Configuration
# -----------------------------

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-flash-latest")
DEFAULT_SHOT_COUNT = int(os.environ.get("SHOT_COUNT", "4"))  # 3-5 recommended
DEFAULT_DURATION_MS = 2200  # per shot, keep short for demo
OUT_DIR = "module_a/out"


# -----------------------------
# Prompt (IMPORTANT: no .format braces conflicts)
# -----------------------------

SHOT_PLANNER_PROMPT = """
You are an ad shot planner. Convert the brief into a multi-shot short-form ad plan.

Rules:
- Output MUST be valid JSON (no markdown, no code fences, no commentary).
- Provide exactly {shot_count} shots.
- Keep a consistent visual style across all shots.
- Use only these element types in elements[].type:
  - bottle
  - can-on-track
  - solo-can
  - ferris-wheel
  - sign
  - tree
  - person
  - track-layer
  - bottle-platform
  - pineapple
- Motions allowed:
  - yaw
  - float
  - loop-track
  - rotate-wheel
  - spin-slow
  - rise-spin
  - sway
  - null

Schema:
{
  "visual_style": ["..."],
  "shots": [
    {
      "id": 1,
      "duration": 2200,
      "shot_description": "one sentence describing the shot",
      "camera": { "movement": "slow-zoom-in|pan-left|pan-right|push-in|pull-out", "angle": "slightly-top-down|eye-level|low-angle" },
      "elements": [
        {
          "id": "product",
          "type": "bottle",
          "motion": "yaw",
          "position": { "x": 50, "y": 52 },
          "presetPosition": "pos-bottle-center"
        }
      ],
      "keywords": ["..."]
    }
  ]
}

Brief:
{brief}
""".strip()


# -----------------------------
# Utilities
# -----------------------------

def ensure_out_dir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_extract_json(text: str) -> Dict[str, Any]:
    """
    Best-effort JSON extraction:
    1) Try direct json.loads
    2) If model returns extra text, extract the first {...} block
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    # Extract first JSON object block
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("Model output did not contain a JSON object.")
    return json.loads(m.group(0))


def clamp_shot_count(n: int) -> int:
    if n < 1:
        return 1
    if n > 6:
        return 6
    return n


# -----------------------------
# Gemini call
# -----------------------------

def call_gemini_for_shot_plan(brief: str, shot_count: int) -> Dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment.")

    genai.configure(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    model = genai.GenerativeModel(model_name)

    prompt = SHOT_PLANNER_PROMPT.replace("{brief}", brief).replace("{shot_count}", str(shot_count))

    resp = model.generate_content(
        prompt,
        generation_config={
            # This is the key: force JSON output
            "response_mime_type": "application/json",
            "temperature": 0.3,
        },
    )

    if not getattr(resp, "text", None):
        raise ValueError("Empty response from Gemini.")

    return safe_extract_json(resp.text)


# -----------------------------
# Stub fallback
# -----------------------------

def generate_shot_plan_stub(brief: str, shot_count: int) -> Dict[str, Any]:
    """
    Minimal plan that always works (used if Gemini fails).
    """
    shots = []
    for i in range(1, shot_count + 1):
        shots.append(
            {
                "id": i,
                "duration": DEFAULT_DURATION_MS,
                "shot_description": f"Shot {i}: dreamy futuristic mini-world reveal of the product with playful motion.",
                "camera": {"movement": "slow-zoom-in", "angle": "slightly-top-down"},
                "elements": [
                    {"id": "track", "type": "track-layer", "motion": None},
                    {"id": "product", "type": "bottle", "motion": "yaw", "position": {"x": 50, "y": 52}, "presetPosition": "pos-bottle-center"},
                    {"id": "wheelRight", "type": "ferris-wheel", "motion": "rotate-wheel", "presetPosition": "pos-wheel-right"},
                    {"id": "tree1", "type": "tree", "motion": None, "presetPosition": "pos-tree-1"},
                    {"id": "person1", "type": "person", "motion": "sway", "presetPosition": "pos-person-1"},
                ],
                "keywords": ["dreamy", "futuristic", "mini-world", "3D", "soft motion"],
            }
        )

    return {"visual_style": ["dreamy", "futuristic", "mini-world", "clean 3D"], "shots": shots}


# -----------------------------
# Build outputs for the pipeline
# -----------------------------

def shot_plan_to_adjson(shot_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Gemini shot_plan into the frontend-friendly adJson format.
    """
    shots_out = []
    for s in shot_plan.get("shots", []):
        shots_out.append(
            {
                "id": s.get("id"),
                "duration": s.get("duration", DEFAULT_DURATION_MS),
                "camera": s.get("camera", {"movement": "slow-zoom-in", "angle": "slightly-top-down"}),
                "elements": s.get("elements", []),
            }
        )
    return {"shots": shots_out}


def build_shot_queries(shot_plan: Dict[str, Any], brief: str) -> Dict[str, Any]:
    """
    Build Module-B query payload.
    Note: Module B currently searches using query_text (and re-embeds internally),
    but we also include embeddings for transparency / future use.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")

    queries = []
    for s in shot_plan.get("shots", []):
        shot_id = s.get("id")
        desc = s.get("shot_description", "")
        keywords = s.get("keywords", [])
        style = " ".join(shot_plan.get("visual_style", []))

        query_text = f"{brief}. {desc}. Style: {style}. Keywords: {', '.join(keywords)}".strip()
        emb = model.encode(query_text).tolist()

        queries.append(
            {
                "shot_id": shot_id,
                "query_text": query_text,
                "keywords": keywords,
                "embedding": emb,
            }
        )

    return {"shots": queries}


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    ensure_out_dir()

    brief = os.environ.get("BRIEF", "").strip()
    if not brief:
        brief = "Brand: XXX; Product: drink bottle; Style: dreamy futuristic mini-world; Elements: transparent pipes, fruit, balls, ferris wheel, trees, little people"

    shot_count = clamp_shot_count(int(os.environ.get("SHOT_COUNT", str(DEFAULT_SHOT_COUNT))))

    # Try Gemini first; fallback to stub if anything goes wrong
    try:
        shot_plan = call_gemini_for_shot_plan(brief, shot_count)
        # Basic validation
        if "shots" not in shot_plan or not isinstance(shot_plan["shots"], list) or len(shot_plan["shots"]) == 0:
            raise ValueError("Gemini returned JSON but missing 'shots'.")
    except Exception as e:
        print(f"⚠️ Gemini failed, falling back to stub. Reason: {e}")
        shot_plan = generate_shot_plan_stub(brief, shot_count)

    adjson = shot_plan_to_adjson(shot_plan)
    shot_queries = build_shot_queries(shot_plan, brief)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_ad = f"{OUT_DIR}/adJson.generated.{ts}.json"
    out_q = f"{OUT_DIR}/shot_queries.{ts}.json"

    write_json(out_ad, adjson)
    write_json(out_q, shot_queries)

    # Also update the "latest" stable filenames used by the rest of the pipeline
    write_json(f"{OUT_DIR}/adJson.generated.json", adjson)
    write_json(f"{OUT_DIR}/shot_queries.json", shot_queries)

    print("✅ wrote:", out_ad)
    print("✅ wrote:", out_q)
    print("✅ updated:", f"{OUT_DIR}/adJson.generated.json")
    print("✅ updated:", f"{OUT_DIR}/shot_queries.json")


if __name__ == "__main__":
    main()