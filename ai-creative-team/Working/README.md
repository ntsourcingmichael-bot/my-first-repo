# Working folder — the "place where work happens"

Auto-partitioned by brand/product so nothing ever gets mixed up.

```
Working/
├── Input/
│   └── <brand>/<product>/           # client product shots, reference moodboards
└── Output/
    ├── Draft/                       # local review queue — pushed to Airtable
    │   └── <brand>/<yyyy-mm-dd>/<concept>-<nn>.png
    └── Final/                       # approved + locked
        └── <brand>/<yyyy-mm-dd>/<concept>-<nn>.png
```

## Rules
- Claude NEVER overwrites an existing file — it bumps the `<nn>` suffix.
- Anything in `Draft/` is considered ephemeral; CI-safe to delete.
- Promoting Draft → Final is manual (or via a future `/approve` skill).
