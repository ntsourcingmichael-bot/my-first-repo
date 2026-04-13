#!/usr/bin/env python3
"""
run_campaign.py  —  top-level orchestrator for the AI Creative Team.

Flow:
  1. Load brand context from System/Context/*.md
  2. Draft copy (Anthropic) for N concepts
  3. Generate images via MCP nano-banana
  4. Save drafts to Working/Output/Draft/<brand>/<date>/
  5. Push each asset + copy to Airtable via MCP airtable

Usage:
  python "System/Workflow tools/run_campaign.py" \
      --brief "spring launch, beach vibe" \
      --count 3
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_servers.nano_banana.client import generate_image           # noqa: E402
from mcp_servers.airtable.client      import upload_asset           # noqa: E402


# --------------------------------------------------------------------------- #
#  cost guard                                                                  #
# --------------------------------------------------------------------------- #
LEDGER = ROOT / ".cost_ledger.json"
MAX_USD = float(os.getenv("MAX_USD_PER_RUN", "5.00"))


def _charge(amount_usd: float, label: str) -> None:
    data = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"total": 0.0, "items": []}
    data["total"] += amount_usd
    data["items"].append({"label": label, "usd": amount_usd, "at": dt.datetime.utcnow().isoformat()})
    if data["total"] > MAX_USD:
        raise SystemExit(f"HALT — running total ${data['total']:.2f} exceeds MAX_USD_PER_RUN=${MAX_USD}")
    LEDGER.write_text(json.dumps(data, indent=2))


# --------------------------------------------------------------------------- #
#  context loader                                                              #
# --------------------------------------------------------------------------- #
def load_context() -> dict[str, str]:
    ctx_dir = ROOT / "System" / "Context"
    ctx: dict[str, str] = {}
    for md in ctx_dir.glob("*.md"):
        ctx[md.stem] = md.read_text()
    return ctx


# --------------------------------------------------------------------------- #
#  copywriting — here we only stub the Anthropic call; the live Claude Code     #
#  session will replace this with a real API call.                              #
# --------------------------------------------------------------------------- #
def draft_copy(brief: str, concept_id: str, brand_ctx: dict[str, str]) -> str:
    """
    Returns the single strongest headline for this concept.
    In live Claude Code runs the agent writes the copy; this stub is
    the offline fallback used by CI.
    """
    return f"[{concept_id}] {brief} — {brand_ctx.get('brand_brief','brand')[:40]}..."


# --------------------------------------------------------------------------- #
#  main                                                                        #
# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--brief", required=True)
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--brand", default=os.getenv("DEFAULT_BRAND", "default"))
    args = p.parse_args()

    brand = args.brand
    today = dt.date.today().isoformat()
    out_dir = ROOT / "Working" / "Output" / "Draft" / brand / today
    out_dir.mkdir(parents=True, exist_ok=True)

    concepts = json.loads(
        (ROOT / "System" / "Skill" / "creative_batch" / "concepts.json").read_text()
    )["concepts"][: args.count]

    ctx = load_context()
    results = []

    for i, concept in enumerate(concepts, 1):
        copy_line = draft_copy(args.brief, concept["id"], ctx)
        _charge(0.01, f"copy:{concept['id']}")

        image_path = out_dir / f"{concept['id']}-{i:02d}.png"
        prompt = (
            f"{concept['hook']} Ad copy: \"{copy_line}\". "
            f"Brand voice: {ctx.get('brand_voice','')[:200]}. --ar 1:1 --style photo"
        )
        generate_image(prompt=prompt, out_path=str(image_path))
        _charge(0.04, f"image:{concept['id']}")

        record_url = upload_asset(
            image_path=str(image_path),
            copy_line=copy_line,
            concept=concept["id"],
            brand=brand,
            status="Pending Review",
        )
        results.append({"concept": concept["id"], "copy": copy_line,
                        "image": str(image_path), "airtable": record_url})
        print(f"✔ {concept['id']:20s}  →  {record_url}")

    (out_dir / "run_manifest.json").write_text(json.dumps(results, indent=2))
    print(f"\n✅ {len(results)} assets delivered. Review at your Airtable base.")


if __name__ == "__main__":
    main()
