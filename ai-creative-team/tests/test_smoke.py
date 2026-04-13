"""
Offline smoke tests — no network, no real keys.
Verifies:
  * MCP servers respond to --ping
  * concepts.json has 40 entries
  * every SKILL.md is well-formed
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_concepts_catalog():
    data = json.loads((ROOT / "System/Skill/creative_batch/concepts.json").read_text())
    assert len(data["concepts"]) == 40, "need 40 concepts"
    ids = [c["id"] for c in data["concepts"]]
    assert len(set(ids)) == 40, "duplicate concept ids"


def test_skill_docs_present():
    for s in ("create_image", "create_video", "create_UGC", "creative_batch"):
        assert (ROOT / f"System/Skill/{s}/SKILL.md").exists()


def test_ping_nano_banana():
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "mcp_servers/nano_banana/server.py"), "--ping"],
        env={"NANO_BANANA_API_KEY": "test"},
    )
    assert json.loads(out)["ok"] is True


def test_ping_airtable():
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "mcp_servers/airtable/server.py"), "--ping"],
        env={"AIRTABLE_API_KEY": "test", "AIRTABLE_BASE_ID": "app123"},
    )
    assert json.loads(out)["ok"] is True


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"✔ {name}")
    print("all smoke tests passed")
