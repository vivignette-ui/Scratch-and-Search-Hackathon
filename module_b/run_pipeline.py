import json
from pathlib import Path

from module_a.scene_planner import SceneInput, plan_scene
from module_b.freepik_client import freepik_search_stub
from module_b.qdrant_client import qdrant_topk_fallback

ROOT = Path(__file__).resolve().parent


def main() -> None:
    inp_path = ROOT / "demo_input.json"
    out_path = ROOT / "demo_output.json"
    catalog_path = ROOT / "module_b" / "asset_catalog.json"

    inp_raw = json.loads(inp_path.read_text(encoding="utf-8"))
    scene_inp = SceneInput(
        brand=inp_raw["brand"],
        product=inp_raw["product"],
        style=inp_raw["style"],
        duration_seconds=int(inp_raw.get("duration_seconds", 9))
    )

    # Module A: scene plan (Gemini-ready)
    adjson = plan_scene(scene_inp)

    # Module B: Freepik candidates + Qdrant-style top-k scoring
    # We score two queries for transparency in the demo.
    queries = [
        "ring / ferris wheel structure, clean dreamy style",
        "floating fruit accent, warm yellow"
    ]

    scoring_queries = []
    for q in queries:
        candidates = freepik_search_stub(q)
        topk, selected = qdrant_topk_fallback(q, candidates, k=5)
        scoring_queries.append({
            "query": q,
            "top_k": topk,
            "selected": selected
        })

    asset_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    output = {
        "input": {
          "brand": scene_inp.brand,
          "product": scene_inp.product,
          "style": scene_inp.style,
          "speed": "normal",
          "quality": "balanced"
        },
        "assetCatalog": asset_catalog,
        "adJson": adjson,
        "scoring": {
            "method": "qdrant_style_topk_demo",
            "queries": scoring_queries
        }
    }

    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
