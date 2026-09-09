# H₂S Guard — frontend

React frontend for the passive colorimetric H₂S exposure dosimeter (SIH
prototype). Simulates the full flow a safety officer follows: scan a
wristband's QR code, check it hasn't expired, photograph the sensor
strip, and log the estimated cumulative exposure.

## Run it

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. No backend needed — it runs entirely
on the dummy data in `src/data/`.

## What's real vs. simulated

- **Real:** all screens, navigation, the validity check that blocks
  reading an expired badge, the history chart and table.
- **Simulated:** the camera/QR scan (tap a badge in the list instead of
  scanning), and the colour-analysis pipeline (`analyzeStrip` in
  `src/services/mockApi.js` returns a plausible number instead of
  running real image processing).

Swap the simulated parts for the real thing without touching any page:
`src/services/mockApi.js` is the only file that talks to "the backend."
Once the Go/Gin API exists, replace its `delay(...)` calls with
`fetch()` calls — same function names, same return shapes.

## Project layout

```
src/
  components/   reusable UI: sidebar, wristband illustration, readout, chart
  pages/        one file per screen (Dashboard, ScanBadge, BadgeDetails, …)
  data/         dummy workers / badges / readings
  services/     mockApi.js — the fake network layer described above
backend-dummy/  seed JSON for whoever builds the real backend
```

## Design notes

Dark instrument-panel theme: the amber accent is the sensor strip's
own colour (pale straw → amber → rust as dose rises), not a decorative
choice — it's reused consistently for the dose readout, the primary
action, and the reference-scale illustration. Numbers that matter
(dose, badge IDs, dates) are set in IBM Plex Mono, like a digital
readout; everything else is IBM Plex Sans. The one motion moment is
the analyzing screen's step-by-step reveal — nothing else animates on
its own.
