import { useEffect, useState } from 'react'
import { analyzeStrip } from '../services/mockApi.js'

const ALL_STEPS = [
  'Badge detected',
  'Reference patch detected',
  'Sensor patch detected',
  'Lighting corrected',
  'Colour extracted',
  'Estimating dose'
]

export default function Analyzing({ badge, onComplete }) {
  const [visibleCount, setVisibleCount] = useState(0)

  useEffect(() => {
    let cancelled = false
    const stepTimer = setInterval(() => {
      setVisibleCount((n) => Math.min(n + 1, ALL_STEPS.length))
    }, 220)

    analyzeStrip(badge.badgeId).then((result) => {
      if (cancelled) return
      clearInterval(stepTimer)
      setVisibleCount(ALL_STEPS.length)
      setTimeout(() => !cancelled && onComplete(result), 260)
    })

    return () => {
      cancelled = true
      clearInterval(stepTimer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [badge.badgeId])

  const progress = (visibleCount / ALL_STEPS.length) * 100

  return (
    <div>
      <div className="page-title">Analyzing</div>
      <div className="page-sub">Correcting for lighting and estimating cumulative exposure.</div>

      <div className="panel analyzing-panel">
        <ul className="step-list">
          {ALL_STEPS.map((step, i) => (
            <li key={step} className={i < visibleCount ? 'done' : ''}>
              <span className="step-dot" />
              {step}
            </li>
          ))}
        </ul>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <style>{`
        .analyzing-panel {
          margin-top: 18px;
          padding: 26px;
        }
        .step-list {
          list-style: none;
          margin: 0 0 20px;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .step-list li {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          color: var(--text-muted);
          transition: color 0.2s ease;
        }
        .step-list li.done {
          color: var(--text-primary);
        }
        .step-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--border-strong);
          transition: background 0.2s ease;
        }
        .step-list li.done .step-dot {
          background: var(--amber-400);
        }
        .progress-track {
          height: 4px;
          background: var(--surface-2);
          border-radius: 2px;
          overflow: hidden;
        }
        .progress-fill {
          height: 100%;
          background: var(--amber-400);
          transition: width 0.22s ease;
        }
      `}</style>
    </div>
  )
}
