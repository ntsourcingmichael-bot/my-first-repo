# Skill: create_UGC

## Purpose
Generate UGC-style (user-generated-content) assets — selfie framing,
imperfect lighting, handwritten caption — to blend with organic feeds.

## Invocation contract
```json
{
  "skill": "create_UGC",
  "inputs": {
    "persona": "e.g. '28-year-old Brooklyn barista'",
    "product": "hero product name from brand_brief",
    "platform": "tiktok | reels | shorts"
  },
  "outputs": {
    "image_path": "Working/Output/Draft/<brand>/<date>/ugc-<nn>.png",
    "caption":    "string (≤ 120 chars, platform-appropriate)"
  }
}
```

## Prompt scaffold
```
Vertical 9:16 phone selfie. {{persona}} holding {{product}}.
Soft window light, slight motion blur, authentic, un-retouched skin,
cluttered realistic background. No studio lighting. No brand logo.
```
