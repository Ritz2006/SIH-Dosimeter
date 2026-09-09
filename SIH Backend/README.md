# backend-dummy

This is **not** the real backend — it's seed data so the frontend has
something realistic to point at before the real API exists.

- `data/workers.json`, `data/badges.json`, `data/readings.json` mirror
  the shape of `src/data/*.js` on the frontend side.
- The frontend currently reads its copies directly (`src/services/mockApi.js`)
  so it runs standalone with `npm install && npm run dev`, no backend needed.

Suggested real endpoints, once the Go/Gin service exists:

```
GET  /api/badges/:badgeId          -> badge + linked worker
GET  /api/workers                  -> worker list
GET  /api/workers/:id/readings     -> exposure history for a worker
POST /api/readings                 -> save a new dose estimate
POST /api/analyze                  -> photo in, {doseEstimate, confidence} out
```

When that's ready, only `src/services/mockApi.js` needs to change —
swap the `delay(...)` calls for `fetch('/api/...')`. Nothing in
`src/pages/` should need to change.
