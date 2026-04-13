"""In-process client shim for Airtable MCP server."""
from __future__ import annotations

from .server import upload_asset_impl, list_pending_impl, set_status_impl


def upload_asset(**kw) -> str:
    return upload_asset_impl(**kw)


def list_pending():
    return list_pending_impl()


def set_status(record_id: str, status: str):
    return set_status_impl(record_id=record_id, status=status)
