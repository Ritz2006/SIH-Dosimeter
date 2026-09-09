import { useState } from 'react'
import { badges } from '../data/badges.js'
import { workers } from '../data/workers.js'
import { fetchBadgeByQr } from '../services/mockApi.js'

export default function ScanBadge({ onSelected, onCancel }) {
  const [loadingId, setLoadingId] = useState(null)

  function handlePick(badgeId) {
    setLoadingId(badgeId)
    fetchBadgeByQr(badgeId).then((badge) => {
      setLoadingId(null)
      onSelected(badge)
    })
  }

  return (
    <div>
      <div className="page-title">Scan badge</div>
      <div className="page-sub">Point the camera at the QR code printed on the wristband.</div>

      <div className="viewfinder panel">
        <div className="viewfinder-frame">
          <span className="corner tl" />
          <span className="corner tr" />
          <span className="corner bl" />
          <span className="corner br" />
        </div>
        <div className="viewfinder-hint text-muted">Place QR code inside the frame</div>
      </div>

      <div className="section-heading">Nearby badges (demo)</div>
      <p className="text-muted" style={{ fontSize: 13, marginTop: -4 }}>
        A live camera scan isn't wired up in this preview — tap a badge below to simulate the QR read.
      </p>

      <div className="badge-pick-list">
        {badges.map((b) => {
          const worker = workers.find((w) => w.id === b.workerId)
          return (
            <button
              key={b.badgeId}
              className="badge-pick"
              onClick={() => handlePick(b.badgeId)}
              disabled={loadingId !== null}
            >
              <div>
                <div className="badge-pick-name">{worker?.name}</div>
                <div className="badge-pick-id mono text-muted">{b.badgeId}</div>
              </div>
              <span className="text-muted">{loadingId === b.badgeId ? 'Reading…' : '↳'}</span>
            </button>
          )
        })}
      </div>

      <button className="btn btn-secondary" style={{ marginTop: 18 }} onClick={onCancel}>
        Cancel
      </button>

      <style>{`
        .viewfinder {
          margin-top: 18px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          padding: 32px;
        }
        .viewfinder-frame {
          position: relative;
          width: 180px;
          height: 180px;
          border: 1px dashed var(--border-strong);
          border-radius: var(--radius-md);
        }
        .corner {
          position: absolute;
          width: 18px;
          height: 18px;
          border: 2px solid var(--amber-400);
        }
        .corner.tl { top: -1px; left: -1px; border-right: none; border-bottom: none; }
        .corner.tr { top: -1px; right: -1px; border-left: none; border-bottom: none; }
        .corner.bl { bottom: -1px; left: -1px; border-right: none; border-top: none; }
        .corner.br { bottom: -1px; right: -1px; border-left: none; border-top: none; }
        .viewfinder-hint {
          font-size: 13px;
        }
        .section-heading {
          margin-top: 26px;
          margin-bottom: 4px;
          font-size: 13px;
          color: var(--text-secondary);
        }
        .badge-pick-list {
          margin-top: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .badge-pick {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          padding: 14px 16px;
          cursor: pointer;
          text-align: left;
          color: var(--text-primary);
        }
        .badge-pick:hover:not(:disabled) {
          border-color: var(--amber-400);
        }
        .badge-pick:disabled {
          opacity: 0.6;
          cursor: default;
        }
        .badge-pick-name {
          font-size: 14px;
          font-weight: 500;
        }
        .badge-pick-id {
          font-size: 12px;
          margin-top: 2px;
        }
      `}</style>
    </div>
  )
}
