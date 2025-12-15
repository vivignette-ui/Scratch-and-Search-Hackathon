# AI-Generated Short Ad Pipeline (Gemini + Freepik + Qdrant)

This repo is a hackathon submission that generates a **6–10s vertical animated product ad** in a “mini-world” style:
- Featured product is always centered and the main character
- Surrounding elements (pipes, fruits, spheres, people, trees, ferris wheels) are mostly static
- Only subtle motions (slow rotation, floating, gentle drifting)
- Clean, dreamy, slightly playful futuristic look

## Live Demo
Deploy with GitHub Pages (recommended). Open `index.html`.

## One-sentence summary
Brand + product + style → Gemini plans a scene → Qdrant selects brand-safe assets from Freepik → Renderer outputs an animated short ad preview.

---

## Pipeline overview

### Module A: Scene Planner (Gemini + Nano Banana)
Takes user input (brand, product, style) and outputs a structured scene plan (`adJson`):
- Elements, positions, and motion presets
- Composition rules: product stays center, soft motion only

File: `module_a/scene_planner.py`

### Module B: Asset Retrieval (Freepik + Qdrant)
- Freepik provides the asset sources (this demo uses URLs + an asset log)
- Qdrant indexes assets and performs similarity search
- Returns top-k results with scores, plus the selected asset for each query (transparent scoring)

Files:
- `module_b/freepik_client.py`
- `module_b/qdrant_client.py`
- `module_b/asset_catalog.json`

### Module C: Renderer (Web)
Reads:
- `assetCatalog` (selected assets)
- `adJson` (scene plan)
And renders a playable preview with visible tradeoffs (Speed + Quality).

File: `index.html`

---

## How to run (basic)

### 1) Preview the demo
Open `index.html` in a browser.
It loads `demo_output.json` and shows:
- rendered scene
- transparent similarity scoring (top-k)

### 2) Run the pipeline locally (optional)
This creates `demo_output.json` from `demo_input.json`.

1. Start Qdrant:
```bash
docker compose up -d
