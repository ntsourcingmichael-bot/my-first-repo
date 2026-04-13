#!/usr/bin/env python3
"""
Nano Banana MCP server — hand-rolled, zero-dependency implementation of the
Model Context Protocol (stdio transport, JSON-RPC 2.0).

Exposes ONE tool:
    generate_image(prompt: str, reference_url?: str, out_path: str) -> { path, bytes }

Spec reference: https://modelcontextprotocol.io

Run standalone:
    python server.py --ping        # health-check, prints {"ok": true}
    python server.py               # speak MCP over stdio
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error

SERVER_NAME = "nano-banana"
SERVER_VERSION = "0.1.0"

API_KEY  = os.getenv("NANO_BANANA_API_KEY", "")
ENDPOINT = os.getenv("NANO_BANANA_ENDPOINT", "https://api.nanobanana.ai/v1/generate")


# --------------------------------------------------------------------------- #
#  underlying HTTP call                                                       #
# --------------------------------------------------------------------------- #
def _call_nano_banana(prompt: str, reference_url: str | None) -> bytes:
    """Return raw PNG bytes."""
    body = json.dumps({
        "prompt": prompt,
        "reference_url": reference_url,
        "size": "1024x1024",
        "format": "png",
    }).encode()

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"nano-banana HTTP {e.code}: {e.read().decode(errors='ignore')}")

    if "image_b64" in payload:
        return base64.b64decode(payload["image_b64"])
    if "url" in payload:
        with urllib.request.urlopen(payload["url"], timeout=60) as img:
            return img.read()
    raise RuntimeError(f"unexpected nano-banana response: {payload!r}")


def generate_image_impl(prompt: str, out_path: str, reference_url: str | None = None) -> dict:
    png = _call_nano_banana(prompt, reference_url)
    p = pathlib.Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(png)
    return {"path": str(p), "bytes": len(png)}


# --------------------------------------------------------------------------- #
#  MCP stdio loop — minimal JSON-RPC 2.0                                      #
# --------------------------------------------------------------------------- #
TOOLS = [
    {
        "name": "generate_image",
        "description": "Generate a single image from a text prompt via Nano Banana.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt":        {"type": "string"},
                "out_path":      {"type": "string"},
                "reference_url": {"type": "string"},
            },
            "required": ["prompt", "out_path"],
        },
    }
]


def _send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _reply(req_id, result=None, error=None) -> None:
    msg = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    _send(msg)


def _handle(req: dict) -> None:
    m = req.get("method")
    i = req.get("id")
    p = req.get("params", {}) or {}

    if m == "initialize":
        _reply(i, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    elif m == "tools/list":
        _reply(i, {"tools": TOOLS})
    elif m == "tools/call":
        name = p.get("name")
        args = p.get("arguments", {}) or {}
        if name != "generate_image":
            _reply(i, error={"code": -32601, "message": f"unknown tool: {name}"})
            return
        try:
            res = generate_image_impl(**args)
            _reply(i, {"content": [{"type": "text", "text": json.dumps(res)}]})
        except Exception as e:
            _reply(i, error={"code": -32000, "message": str(e)})
    elif m in ("notifications/initialized",):
        pass  # no response to notifications
    else:
        if i is not None:
            _reply(i, error={"code": -32601, "message": f"method not found: {m}"})


def run_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        _handle(req)


# --------------------------------------------------------------------------- #
#  CLI entry                                                                  #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true", help="health check")
    args = ap.parse_args()

    if args.ping:
        ok = bool(API_KEY)
        print(json.dumps({"ok": ok, "server": SERVER_NAME,
                          "endpoint": ENDPOINT, "has_key": ok}))
        return
    run_stdio()


if __name__ == "__main__":
    main()
