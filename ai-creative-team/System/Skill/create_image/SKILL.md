# Skill: create_image

## Purpose
Produce a single advertising image from a copy line + brand context.

## Invocation contract
```json
{
  "skill": "create_image",
  "inputs": {
    "copy_line": "string — the ad headline this image must support",
    "concept":   "string — one of the 40 concepts from creative_batch",
    "reference": "path  — optional reference image in Working/Input/"
  },
  "outputs": {
    "image_path": "Working/Output/Draft/<brand>/<date>/<concept>-<nn>.png",
    "prompt_used": "string"
  }
}
```

## Prompt template
```
You are art-directing a single still frame for {{BRAND_NAME}}.
Brand voice: {{TONE}}.
Visual rules: {{VISUAL_GUARDRAILS}}.
Concept: {{concept}}.
Ad copy: "{{copy_line}}".

Write ONE detailed image prompt (max 120 words) that a text-to-image
model can execute. Describe subject, lighting, composition, palette,
lens, mood. End with: "--ar 1:1 --style photo".
```

## Model call
MCP tool: `nano-banana.generate_image`
Params: `{ "prompt": <rendered prompt>, "reference_url": <optional> }`

## Cost envelope
- 1 image ≈ $0.04 (Nano Banana standard tier)
- Hard-cap: `MAX_IMAGES_PER_RUN`
