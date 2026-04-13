# Skill: create_video

## Purpose
Turn a storyboard (3-6 beats) into an MP4 under 15 seconds.

## Invocation contract
```json
{
  "skill": "create_video",
  "inputs": {
    "storyboard": [
      {"beat": 1, "shot": "...", "copy": "..."},
      {"beat": 2, "shot": "...", "copy": "..."}
    ],
    "duration_sec": 12
  },
  "outputs": {
    "video_path": "Working/Output/Draft/<brand>/<date>/<concept>.mp4"
  }
}
```

## Pipeline
1. Render each beat as a still via `create_image`.
2. Stitch with ffmpeg (`System/Workflow tools/stitch_video.sh`).
3. Overlay copy with the brand typography.

## Cost envelope
- ≈ $0.04 × beats + ffmpeg (free)
