# Skill: creative_batch

## Purpose
Fan out a single brand brief into **N** finished ad concepts drawn from
a built-in library of 40 concept templates.

## Invocation contract
```json
{
  "skill": "creative_batch",
  "inputs": {
    "brief": "string — free-form brief, e.g. 'spring launch, beach vibe'",
    "count": 3,
    "concepts": ["auto"]
  },
  "outputs": {
    "records": [
      { "concept": "before_after", "copy": "...", "image_path": "..." }
    ]
  }
}
```

## 40 Concept Library
See `concepts.json` for the full catalog. Categories:

| Category            | Example concept IDs                                    |
|---------------------|--------------------------------------------------------|
| Problem / Solution  | before_after, pain_relief, day_in_life                 |
| Social Proof        | testimonial_quote, star_rating, as_seen_on             |
| Comparison          | us_vs_them, feature_matrix, price_drop                 |
| Demonstration       | how_it_works, speed_demo, durability_test              |
| Aspirational        | lifestyle_hero, transformation, dream_outcome          |
| UGC / Authentic     | unboxing, reaction, in_the_wild                        |
| Urgency / Offer     | flash_sale, limited_stock, bundle_deal                 |
| Storytelling        | founder_story, origin_myth, day_one                    |

(See the JSON file for all 40.)

## Pipeline
1. Pick `count` concepts (or honour explicit `concepts` list).
2. For each concept:
   - draft ad copy (3 headline variants) using Claude,
   - pick the strongest variant,
   - call `create_image` with `{ copy_line, concept }`.
3. Return the batch as a JSON array. The orchestrator pushes each row
   to Airtable.

## Cost envelope
- copy ≈ $0.01 × 3 headlines × count
- image ≈ $0.04 × count
- HALT if cumulative > `MAX_USD_PER_RUN`.
