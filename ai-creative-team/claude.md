# CLAUDE.md — AI Creative Team (System Heart)

> This file is the long-lived orchestration manifest for Claude Code.
> It MUST be loaded at the start of every session. Treat it as the
> single source of truth for project layout, vendors, skills and
> cost-control rules.

---

## 1. Mission

Turn a short brand brief into finished advertising creatives with
zero human glue-work. The pipeline is:

```
Brand brief  ──▶  Ad Copy  ──▶  Nano Banana (image)  ──▶  Airtable (review)
```

---

## 2. Project Structure

```
ai-creative-team/
├── claude.md               # this file — system heart
├── setup.md                # interactive onboarding wizard
├── .env                    # API key placeholders (never commit real keys)
├── .env.example            # template committed to git
├── .mcp.json               # MCP server registration for Claude Code
│
├── System/                 # configure once, use forever
│   ├── Context/            # brand brief, tone, visual identity
│   ├── Skill/              # executable capabilities
│   │   ├── create_image/
│   │   ├── create_video/
│   │   ├── create_UGC/
│   │   └── creative_batch/ # 40 built-in concept templates
│   └── Workflow tools/     # orchestration scripts
│
├── Working/                # day-to-day output, auto-partitioned by brand
│   ├── Input/              # client product shots, reference images
│   └── Output/
│       ├── Draft/          # local review, waiting for team approval
│       └── Final/          # approved & locked
│
└── mcp_servers/            # home-grown MCP connectors
    ├── nano_banana/        # image generation
    └── airtable/           # review board sync
```

---

## 3. Connected Vendors

| Vendor           | Purpose                         | Env var                  | MCP name       |
|------------------|---------------------------------|--------------------------|----------------|
| Nano Banana      | Text-to-image generation        | `NANO_BANANA_API_KEY`    | `nano-banana`  |
| Airtable         | Creative review board           | `AIRTABLE_API_KEY`       | `airtable`     |
| Google AI Studio | Copywriting / Gemini fallback   | `GOOGLE_AI_STUDIO_KEY`   | (native HTTP)  |
| Anthropic        | Primary LLM (Claude)            | `ANTHROPIC_API_KEY`      | (native)       |

All keys live in `.env`. `claude.md` NEVER embeds a real key.

---

## 4. Available Skills

| Skill            | Input                        | Output                          |
|------------------|------------------------------|---------------------------------|
| `create_image`   | prompt + ref image (opt.)    | 1 PNG in `Working/Output/Draft` |
| `create_video`   | storyboard JSON              | 1 MP4 in `Working/Output/Draft` |
| `create_UGC`     | persona + product            | UGC-style image + caption       |
| `creative_batch` | brand brief + concept count  | N assets from 40-concept library|

Each skill has its own `SKILL.md` with the exact prompt template,
the model it calls, and its cost envelope.

---

## 5. Workflow SOP — `brand → copy → image → airtable`

1. Read `System/Context/brand_brief.md`.
2. Invoke **Skill/creative_batch** (or `create_image`) to write the ad copy
   and craft an image-prompt.
3. Call **MCP `nano-banana.generate_image`** with the prompt.
4. Save the returned binary to `Working/Output/Draft/<brand>/<yyyy-mm-dd>/`.
5. Call **MCP `airtable.upload_asset`** to push the asset + copy to the
   review table; status = `Pending Review`.
6. Report the Airtable record URL back to the user.

The full script lives at `System/Workflow tools/run_campaign.py`.

---

## 6. Cost Awareness (MANDATORY)

Claude Code MUST refuse to run any step that blows the per-run budget.

| Limit              | Default | Override env var           |
|--------------------|---------|----------------------------|
| Max images / run   | 10      | `MAX_IMAGES_PER_RUN`       |
| Max USD / run      | $5.00   | `MAX_USD_PER_RUN`          |
| Max tokens / call  | 8000    | `MAX_TOKENS_PER_CALL`      |

Before any paid API call:
1. Estimate the cost (tokens × rate  OR  images × unit price).
2. Accumulate into `.cost_ledger.json` in the project root.
3. If the running total for this session exceeds `MAX_USD_PER_RUN`,
   **HALT** and ask the user for explicit go-ahead.

---

## 7. Folder-naming Convention (Working/)

```
Working/Input/<brand>/<product>/...
Working/Output/Draft/<brand>/<yyyy-mm-dd>/<concept>-<nn>.png
Working/Output/Final/<brand>/<yyyy-mm-dd>/<concept>-<nn>.png
```

Claude Code creates missing folders on demand — never overwrites.

---

## 8. First-time setup

Run `/setup` (or read `setup.md`) — the wizard will:
  * ask for brand / product / industry / tone,
  * write `System/Context/brand_brief.md`,
  * populate `.env` from `.env.example`,
  * verify every MCP server with a ping.
