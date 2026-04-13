---
description: Approve a pending creative — Airtable → Approved, move Draft → Final
argument-hint: "<record_id>"
---

Run:

```bash
python "System/Workflow tools/review.py" approve $ARGUMENTS
```

Report back the new Final path and the Airtable record URL. If the
record was already Approved, say so and stop.
