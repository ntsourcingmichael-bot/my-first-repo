# AI Creative Team — a Claude Code plugin framework

A from-scratch, zero-dependency plugin that turns a brand brief into
finished ads and drops them into your team's Airtable review board.

```
brand brief  ─▶  ad copy  ─▶  Nano Banana image  ─▶  Airtable row
```

## Quick start

```bash
# 1. in Claude Code:
/setup

# 2. then anytime:
/run-campaign  "spring launch, beach vibe"  --count 3
```

## Architecture at a glance

| Layer                 | Location                         | What lives here                     |
|-----------------------|----------------------------------|-------------------------------------|
| System heart          | `claude.md`                      | Project map, vendors, cost rules    |
| Onboarding            | `setup.md`, `.claude/commands/`  | Interactive wizard                  |
| Secrets               | `.env` (git-ignored)             | API key placeholders                |
| Brand knowledge       | `System/Context/`                | Brief, voice, visual identity       |
| Skills                | `System/Skill/`                  | create_image / video / UGC / batch  |
| Orchestration         | `System/Workflow tools/`         | `run_campaign.py`, ffmpeg glue      |
| MCP connectors        | `mcp_servers/`                   | Hand-rolled Nano Banana + Airtable  |
| Work in progress      | `Working/Input/`, `Output/Draft/`| Per-brand, per-date                 |
| Approved              | `Working/Output/Final/`          | Locked creatives                    |

Every piece is home-grown Python — no third-party SDKs, no `pip install`
beyond the Python standard library. The MCP servers speak JSON-RPC 2.0
over stdio, exactly as Claude Code expects.

## Tests

```bash
python tests/test_smoke.py
```

## Packaging

```bash
./package.sh           # produces ai-creative-team.zip
```
