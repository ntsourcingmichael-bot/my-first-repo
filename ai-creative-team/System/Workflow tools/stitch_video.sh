#!/usr/bin/env bash
# Stitch N stills into a single MP4. Used by Skill/create_video.
# Usage: stitch_video.sh <frames_dir> <output.mp4> <fps>
set -euo pipefail
frames="${1:?frames dir required}"
out="${2:?output mp4 required}"
fps="${3:-1}"
ffmpeg -y -framerate "$fps" -pattern_type glob -i "${frames}/*.png" \
       -c:v libx264 -pix_fmt yuv420p "$out"
echo "wrote $out"
