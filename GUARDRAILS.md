# Guardrails: Copyright + Brand Safety

This project is designed to be brand-safe by default.

## Content policy
- No brand logos by default
- No copyrighted characters, celebrities, or trademarked mascots
- No unsafe or restricted product categories in the demo outputs

## Asset policy
- Use licensed sources (Freepik) or placeholders
- Maintain an asset log (see ASSET_SOURCES.md)
- If licensing is unclear, fallback to placeholders

## Prompt and output controls
- Scene planner only uses allowlisted element categories (abstract shapes, fruits, generic objects)
- Renderer supports “Draft/Balanced/High” quality presets, but does not introduce risky content
