---
description: List every creative currently pending review
---

Run:

```bash
python "System/Workflow tools/review.py" list
```

Render the response as a short table: concept · brand · copy (truncated)
· record_id. Then remind the user they can `/approve <id>` or
`/reject <id>`.
