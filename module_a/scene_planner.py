import json
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SceneInput:
    brand: str
    product: str
    style: str
    duration_seconds: int = 9


def plan_scene(inp: SceneInput) -> Dict[str, Any]:
    # In production: call Gemini here to generate structured scene plan.
    # Demo fallback: deterministic scene plan that matches your renderer.
    duration_ms = int(inp.duration_seconds * 1000)

    adjson = {
        "shots": [
            {
                "id": 1,
                "duration": duration_ms,
                "camera": {"movement": "slow-zoom-in", "angle": "slightly-top-down"},
                "elements": [
                    {"id": "product", "type": "bottle", "motion": "yaw", "presetPosition": "pos-bottle-center", "assetId": "product_main"},
                    {"id": "fruitTop", "type": "pineapple", "motion": "float", "position": {"x": 50, "y": 26}, "assetId": "fruit_yellow"},
                    {"id": "wheelRight", "type": "ferris-wheel", "motion": "rotate-wheel", "presetPosition": "pos-wheel-right", "assetId": "ring_basic"},
                    {"id": "soloCan", "type": "solo-can", "motion": "rise-spin", "presetPosition": "pos-solo-can-left", "assetId": "sphere_basic"},
                    {"id": "tree1", "type": "tree", "presetPosition": "pos-tree-1", "assetId": "crystal_basic"},
                    {"id": "person1", "type": "person", "motion": "sway", "presetPosition": "pos-person-1"}
                ]
            }
        ]
    }
    return adjson


if __name__ == "__main__":
    # quick local test
    inp = SceneInput(brand="PeachSpark", product="Sparkling Drink", style="dreamy, clean, playful")
    print(json.dumps(plan_scene(inp), indent=2))
