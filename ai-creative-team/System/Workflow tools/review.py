#!/usr/bin/env python3
"""
review.py — promote a Draft to Final (approve) or mark rejected.

Usage:
    python "System/Workflow tools/review.py" approve <record_id>
    python "System/Workflow tools/review.py" reject  <record_id> [--reason "..."]
    python "System/Workflow tools/review.py" list

Approve:
  * Airtable Status → "Approved"
  * The file at LocalPath is MOVED from Working/Output/Draft/... to
    Working/Output/Final/... (same relative sub-path under the brand/date).

Reject:
  * Airtable Status → "Rejected" (Notes field appended with --reason)
  * Draft file is left in place (delete manually if desired).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_servers.airtable.client import list_pending, set_status        # noqa: E402
from mcp_servers.airtable.server import _api                            # noqa: E402


DRAFT = ROOT / "Working" / "Output" / "Draft"
FINAL = ROOT / "Working" / "Output" / "Final"


def _fetch_record(record_id: str) -> dict:
    res = _api("GET", f"/{record_id}")
    return {"id": res["id"], **res.get("fields", {})}


def _promote_file(local_path: str) -> pathlib.Path | None:
    src = pathlib.Path(local_path)
    if not src.exists():
        return None
    try:
        rel = src.relative_to(DRAFT)
    except ValueError:
        # Not under Draft — nothing to move.
        return None
    dst = FINAL / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return dst


def cmd_approve(record_id: str) -> None:
    rec = _fetch_record(record_id)
    set_status(record_id, "Approved")
    moved = _promote_file(rec.get("LocalPath", ""))
    print(json.dumps({
        "record_id": record_id,
        "status":    "Approved",
        "moved_to":  str(moved) if moved else None,
    }, indent=2))


def cmd_reject(record_id: str, reason: str | None) -> None:
    set_status(record_id, "Rejected")
    if reason:
        _api("PATCH", "", {"records": [{"id": record_id,
                                        "fields": {"Notes": reason}}]})
    print(json.dumps({"record_id": record_id, "status": "Rejected",
                      "reason": reason}, indent=2))


def cmd_list() -> None:
    rows = list_pending()
    print(json.dumps(rows, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("approve")
    a.add_argument("record_id")

    r = sub.add_parser("reject")
    r.add_argument("record_id")
    r.add_argument("--reason", default=None)

    sub.add_parser("list")

    args = ap.parse_args()
    if args.cmd == "approve":
        cmd_approve(args.record_id)
    elif args.cmd == "reject":
        cmd_reject(args.record_id, args.reason)
    elif args.cmd == "list":
        cmd_list()


if __name__ == "__main__":
    main()
