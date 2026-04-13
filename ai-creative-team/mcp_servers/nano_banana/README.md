# Nano Banana MCP server

Home-grown connector — no third-party SDK — for the Nano Banana image API.

## Tool
`generate_image(prompt, out_path, reference_url?) -> { path, bytes }`

## Env
- `NANO_BANANA_API_KEY`  (required)
- `NANO_BANANA_ENDPOINT` (default: https://api.nanobanana.ai/v1/generate)

## Health check
```bash
python server.py --ping
# → {"ok": true, "server": "nano-banana", ...}
```

## Registered in
`.mcp.json` (root) — Claude Code auto-starts it on session open.
