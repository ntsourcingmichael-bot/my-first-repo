# Airtable MCP server

Pushes finished creatives to a review table; also supports polling and
status updates so `/approve` or `/reject` skills can be wired in.

## Required table fields
| Field       | Type         |
|-------------|--------------|
| Brand       | Single line  |
| Concept     | Single line  |
| Copy        | Long text    |
| Status      | Single select (Pending Review / Approved / Rejected) |
| Asset       | Attachment   |
| LocalPath   | Single line  |

## Env
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`
- `AIRTABLE_TABLE_NAME`
- `PUBLIC_ASSET_HOST` (optional — if your Drafts are served, image URLs are filled in)

## Ping
```bash
python server.py --ping
```
