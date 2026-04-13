# setup.md — Interactive Onboarding Wizard

> Trigger by typing `setup` (or `/setup`) in Claude Code.
> This document is both human-readable and machine-executable:
> Claude follows the script below, line by line.

---

## Step 0 — Pre-flight

Claude reads `.env.example`. If `.env` is missing, copy the template:

```bash
cp .env.example .env
```

---

## Step 1 — Ask the user (one question at a time)

Claude asks each of the following and stores the answer in
`System/Context/brand_brief.md`:

1. **Brand name?**                → `{{BRAND_NAME}}`
2. **One-liner business description?**   → `{{BUSINESS_ONE_LINER}}`
3. **Industry / vertical?**       → `{{INDUSTRY}}`
4. **Primary audience?**          → `{{AUDIENCE}}`
5. **Brand tone (3 adjectives)?** → `{{TONE}}`
6. **Hero product(s)?**           → `{{PRODUCTS}}`
7. **Visual do's and don'ts?**    → `{{VISUAL_GUARDRAILS}}`
8. **Airtable Base ID?**          → store in `.env` as `AIRTABLE_BASE_ID`
9. **Airtable Table name?**       → store in `.env` as `AIRTABLE_TABLE_NAME`

---

## Step 2 — Collect API keys

Claude prompts (and only writes them into `.env`, never echoes):

- `ANTHROPIC_API_KEY`
- `NANO_BANANA_API_KEY`
- `AIRTABLE_API_KEY`
- `GOOGLE_AI_STUDIO_KEY` (optional)

---

## Step 3 — Generate derived files

Claude writes:

* `System/Context/brand_brief.md`
* `System/Context/brand_voice.md`
* `System/Context/visual_identity.md`

Each is rendered from the templates in
`System/Context/_templates/` using the variables above.

---

## Step 4 — Verify MCP servers

Claude runs:

```bash
python mcp_servers/nano_banana/server.py --ping
python mcp_servers/airtable/server.py   --ping
```

Both must return `{"ok": true}`.

---

## Step 5 — Scaffold working folders

```bash
mkdir -p "Working/Input/{{BRAND_NAME}}"
mkdir -p "Working/Output/Draft/{{BRAND_NAME}}"
mkdir -p "Working/Output/Final/{{BRAND_NAME}}"
```

---

## Step 6 — Done

Claude prints:

```
✅ AI Creative Team is ready for {{BRAND_NAME}}.
Try:   run campaign  "spring launch, 3 concepts"
```
