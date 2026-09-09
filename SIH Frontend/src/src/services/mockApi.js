// Thin fake network layer. Every function returns a Promise so
// swapping these for real fetch() calls to the Go/Gin backend
// later is a one-file change — nothing in pages/ should need to
// know the difference.

import { workers } from '../data/workers.js'
import { badges } from '../data/badges.js'
import { readings, readingsForWorker } from '../data/readings.js'

const LATENCY = 350

function delay(value, ms = LATENCY) {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

export function fetchBadgeByQr(qrValue) {
  const badge = badges.find((b) => b.badgeId === qrValue)
  if (!badge) return delay(null)
  const worker = workers.find((w) => w.id === badge.workerId)
  return delay({ ...badge, worker })
}

export function fetchWorkers() {
  return delay(workers)
}

export function fetchWorkerHistory(workerId) {
  return delay(readingsForWorker(workerId))
}

export function fetchTodayCount() {
  const today = readings.filter((r) => r.date === '2026-09-01').length
  return delay(today || readings.length)
}

// Simulates the camera -> lighting correction -> colour extraction
// -> ML calibration -> dose estimation pipeline. Returns a plausible
// estimate in the same numeric neighbourhood as nearby readings so
// the demo stays internally consistent.
export function analyzeStrip(badgeId) {
  const priorReadings = readings.filter((r) => r.badgeId === badgeId)
  const base = priorReadings.length
    ? priorReadings[priorReadings.length - 1].doseEstimate
    : 12

  const doseEstimate = Math.max(1, +(base + (Math.random() * 6 - 3)).toFixed(1))
  const confidence = +(0.82 + Math.random() * 0.12).toFixed(2)

  return delay(
    {
      doseEstimate,
      confidence,
      steps: [
        'Badge detected',
        'Reference patch detected',
        'Sensor patch detected',
        'Lighting corrected',
        'Colour extracted'
      ]
    },
    1400
  )
}

export function saveReading(reading) {
  // In production: POST /readings. Here we just resolve — the
  // dummy data file isn't mutated so refreshing resets the demo.
  return delay({ ok: true, saved: reading })
}
