---
description: Reject a pending creative — Airtable → Rejected (with optional reason)
argument-hint: "<record_id> [--reason \"why\"]"
---

Run:

```bash
python "System/Workflow tools/review.py" reject $ARGUMENTS
```

If the caller did not supply `--reason`, ask them for a one-line reason
before running (reviewers need to know why).
