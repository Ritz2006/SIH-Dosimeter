import { useState } from 'react'
import ExposureReadout from '../components/ExposureReadout.jsx'
import StatusPill from '../components/StatusPill.jsx'
import { saveReading } from '../services/mockApi.js'

export default function Result({ badge, result, onSaved }) {
  const [saving, setSaving] = useState(false)

  function handleSave() {
    setSaving(true)
    saveReading({
      workerId: badge.worker?.id,
      badgeId: badge.badgeId,
      date: new Date().toISOString().slice(0, 10),
      doseEstimate: result.doseEstimate,
      confidence: result.confidence
    }).then(() => {
      setSaving(false)
      onSaved()
    })
  }

  return (
    <div>
      <div className="page-title">Exposure result</div>
      <div className="page-sub">
        {badge.worker?.name} · <span className="mono">{badge.badgeId}</span>
      </div>

      <div className="panel panel-accent result-panel">
        <ExposureReadout value={result.doseEstimate} confidence={result.confidence} />

        <hr className="hairline" />

        <div className="result-footer">
          <StatusPill status={badge.status} />
          <span className="text-muted" style={{ fontSize: 13 }}>
            Logged for occupational health records
          </span>
        </div>
      </div>

      <p className="disclaimer text-muted">
        This is an estimate. Colorimetric response doesn't scale perfectly linearly at very
        low concentrations or over long durations, and hasn't yet been validated against a
        controlled reference exposure.
      </p>

      <button className="btn btn-primary btn-block" onClick={handleSave} disabled={saving}>
        {saving ? 'Saving…' : 'Save record'}
      </button>

      <style>{`
        .result-panel {
          margin-top: 18px;
        }
        .result-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 8px;
        }
        .disclaimer {
          font-size: 12.5px;
          line-height: 1.6;
          margin: 14px 0 18px;
        }
      `}</style>
    </div>
  )
}
