"""
In-process client for the nano_banana MCP server.
Used by run_campaign.py so the orchestrator can stay single-process
in local/CI mode. In production Claude Code will call the server via
its own MCP transport (see .mcp.json).
"""
from __future__ import annotations

from .server import generate_image_impl


def generate_image(prompt: str, out_path: str, reference_url: str | None = None) -> dict:
    return generate_image_impl(prompt=prompt, out_path=out_path, reference_url=reference_url)
