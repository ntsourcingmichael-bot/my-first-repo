#!/usr/bin/env bash
# Bundle the framework for hand-off.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
name="ai-creative-team"
out="${here%/*}/${name}.zip"

cd "${here%/*}"
rm -f "$out"
zip -r "$out" "$name" \
    -x "${name}/.env" \
    -x "${name}/.cost_ledger.json" \
    -x "${name}/**/__pycache__/*" \
    -x "${name}/Working/Output/**/*.png" \
    -x "${name}/Working/Output/**/*.mp4"
echo "wrote $out"
