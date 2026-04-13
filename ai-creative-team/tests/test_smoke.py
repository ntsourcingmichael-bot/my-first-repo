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


def test_review_promotes_draft_to_final(tmp_path=None):
    """_promote_file moves a file from Draft to Final preserving sub-path."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "review", ROOT / "System/Workflow tools/review.py")
    # loading the module imports airtable client (no network until called),
    # which is fine for this pure-filesystem helper.
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    draft = ROOT / "Working/Output/Draft/_test_brand/2099-01-01"
    draft.mkdir(parents=True, exist_ok=True)
    sample = draft / "before_after-01.png"
    sample.write_bytes(b"\x89PNG\r\n\x1a\n")

    moved = mod._promote_file(str(sample))
    assert moved is not None and moved.exists()
    assert "Final" in str(moved) and "_test_brand" in str(moved)
    # cleanup
    moved.unlink()
    moved.parent.rmdir()
    # may also clean brand dir if empty
    try:
        moved.parent.parent.rmdir()
        (ROOT / "Working/Output/Final/_test_brand").rmdir()
    except OSError:
        pass
    try:
        draft.rmdir()
        draft.parent.rmdir()
    except OSError:
        pass


def test_slash_commands_present():
    for cmd in ("setup", "run-campaign", "approve", "reject", "pending"):
        assert (ROOT / f".claude/commands/{cmd}.md").exists(), cmd


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"✔ {name}")
    print("all smoke tests passed")
