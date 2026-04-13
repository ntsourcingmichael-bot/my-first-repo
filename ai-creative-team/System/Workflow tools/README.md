# Workflow tools

Scripts that glue Skills together into end-to-end runs.

| Script              | What it does                                           |
|---------------------|--------------------------------------------------------|
| `run_campaign.py`   | brief → copy → image → Airtable (the SOP)              |
| `stitch_video.sh`   | ffmpeg wrapper used by `create_video`                  |

Claude Code shells these out via its Bash tool; the scripts never
call an LLM directly — they defer to the registered MCP servers.
