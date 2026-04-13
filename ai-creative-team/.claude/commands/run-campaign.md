---
description: Run the end-to-end creative workflow (brief → copy → image → Airtable)
argument-hint: "<brief text> [--count N]"
---

Invoke:

```bash
python "System/Workflow tools/run_campaign.py" --brief "$ARGUMENTS"
```

Report the Airtable URL for every generated row. HALT the run if the
cost ledger exceeds `MAX_USD_PER_RUN`.
