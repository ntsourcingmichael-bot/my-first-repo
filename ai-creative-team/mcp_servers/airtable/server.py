#!/usr/bin/env python3
"""
Airtable MCP server — minimal JSON-RPC 2.0 stdio server.

Tools
-----
- upload_asset(image_path, copy_line, concept, brand, status) -> record_url
- list_pending() -> [records]
- set_status(record_id, status) -> ok

Env
---
AIRTABLE_API_KEY     pat...
AIRTABLE_BASE_ID     appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME  e.g. "Creative Review"
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
import urllib.error

SERVER_NAME = "airtable"
SERVER_VERSION = "0.1.0"

API_KEY = os.getenv("AIRTABLE_API_KEY", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
TABLE   = os.getenv("AIRTABLE_TABLE_NAME", "Creative Review")


def _api(method: str, path: str, body: dict | None = None) -> dict:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{urllib.parse.quote(TABLE)}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"airtable HTTP {e.code}: {e.read().decode(errors='ignore')}")


def upload_asset_impl(image_path: str, copy_line: str, concept: str,
                      brand: str, status: str = "Pending Review") -> str:
    """
    Creates a new row. The Attachment field is set by URL — because Airtable
    can't accept file bytes directly. We stash the file in a public-ish
    location OR fall back to storing the local path only.
    """
    p = pathlib.Path(image_path).resolve()
    fields = {
        "Brand":   brand,
        "Concept": concept,
        "Copy":    copy_line,
        "Status":  status,
        "LocalPath": str(p),
    }
    # If the caller exposed a public URL env var, use it; else skip attachment.
    host = os.getenv("PUBLIC_ASSET_HOST")
    if host:
        fields["Asset"] = [{"url": f"{host.rstrip('/')}/{p.name}"}]

    res = _api("POST", "", {"records": [{"fields": fields}]})
    rec_id = res["records"][0]["id"]
    return f"https://airtable.com/{BASE_ID}/{TABLE}/{rec_id}"


def list_pending_impl() -> list:
    res = _api("GET", "?filterByFormula=" + urllib.parse.quote("{Status}='Pending Review'"))
    return [{"id": r["id"], **r["fields"]} for r in res.get("records", [])]


def set_status_impl(record_id: str, status: str) -> dict:
    return _api("PATCH", "", {"records": [{"id": record_id, "fields": {"Status": status}}]})


# --------------------------------------------------------------------------- #
#  MCP stdio plumbing                                                         #
# --------------------------------------------------------------------------- #
TOOLS = [
    {
        "name": "upload_asset",
        "description": "Push one creative asset (image + copy) to the review table.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string"},
                "copy_line":  {"type": "string"},
                "concept":    {"type": "string"},
                "brand":      {"type": "string"},
                "status":     {"type": "string", "default": "Pending Review"},
            },
            "required": ["image_path", "copy_line", "concept", "brand"],
        },
    },
    {
        "name": "list_pending",
        "description": "List rows awaiting review.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_status",
        "description": "Update a row's Status field (Approved / Rejected / ...).",
        "inputSchema": {
            "type": "object",
            "properties": {"record_id": {"type": "string"}, "status": {"type": "string"}},
            "required": ["record_id", "status"],
        },
    },
]

_DISPATCH = {
    "upload_asset": upload_asset_impl,
    "list_pending": lambda: list_pending_impl(),
    "set_status":   set_status_impl,
}


def _send(obj): sys.stdout.write(json.dumps(obj) + "\n"); sys.stdout.flush()


def _reply(i, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": i}
    (m.__setitem__("error", error) if error else m.__setitem__("result", result))
    _send(m)


def _handle(req):
    m, i, p = req.get("method"), req.get("id"), req.get("params", {}) or {}
    if m == "initialize":
        _reply(i, {"protocolVersion": "2024-11-05",
                   "capabilities": {"tools": {}},
                   "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}})
    elif m == "tools/list":
        _reply(i, {"tools": TOOLS})
    elif m == "tools/call":
        name = p.get("name"); args = p.get("arguments", {}) or {}
        fn = _DISPATCH.get(name)
        if not fn:
            _reply(i, error={"code": -32601, "message": f"unknown tool: {name}"}); return
        try:
            res = fn(**args) if args else fn()
            _reply(i, {"content": [{"type": "text", "text": json.dumps(res)}]})
        except Exception as e:
            _reply(i, error={"code": -32000, "message": str(e)})
    elif m == "notifications/initialized":
        pass
    elif i is not None:
        _reply(i, error={"code": -32601, "message": f"method not found: {m}"})


def run_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: _handle(json.loads(line))
        except json.JSONDecodeError: continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true")
    args = ap.parse_args()
    if args.ping:
        print(json.dumps({"ok": bool(API_KEY and BASE_ID), "server": SERVER_NAME,
                          "base": BASE_ID, "table": TABLE}))
        return
    run_stdio()


if __name__ == "__main__":
    main()
