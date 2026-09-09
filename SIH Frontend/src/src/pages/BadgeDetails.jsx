import StatusPill from '../components/StatusPill.jsx'

export default function BadgeDetails({ badge, onReadSensor, onBack }) {
  const isValid = badge.status === 'valid'

  return (
    <div>
      <div className="page-title">Badge details</div>
      <div className="page-sub">Confirm the badge is still valid before taking a reading.</div>

      <div className="panel details-panel">
        {!isValid && <div className="hazard-stripe danger" />}

        <div className="details-row">
          <div className="details-label text-muted">Worker</div>
          <div className="details-value">{badge.worker?.name}</div>
        </div>
        <hr className="hairline" />
        <div className="details-row">
          <div className="details-label text-muted">Badge ID</div>
          <div className="details-value mono">{badge.badgeId}</div>
        </div>
        <hr className="hairline" />
        <div className="details-row">
          <div className="details-label text-muted">Site</div>
          <div className="details-value">{badge.worker?.site}</div>
        </div>
        <hr className="hairline" />
        <div className="details-row">
          <div className="details-label text-muted">Activated</div>
          <div className="details-value mono">{badge.activatedOn}</div>
        </div>
        <hr className="hairline" />
        <div className="details-row">
          <div className="details-label text-muted">Valid until</div>
          <div className="details-value mono">{badge.expiresOn}</div>
        </div>
        <hr className="hairline" />
        <div className="details-row">
          <div className="details-label text-muted">Status</div>
          <StatusPill status={badge.status} />
        </div>

        {!isValid && (
          <p className="expired-note">
            This badge is past its {badge.shelfLifeDays}-day shelf life. Readings from an
            expired strip aren't reliable — issue the worker a new badge before reading.
          </p>
        )}
      </div>

      <div className="details-actions">
        <button className="btn btn-secondary" onClick={onBack}>
          Back
        </button>
        <button className="btn btn-primary" onClick={onReadSensor} disabled={!isValid}>
          Read sensor
        </button>
      </div>

      <style>{`
        .details-panel {
          margin-top: 18px;
          position: relative;
          overflow: hidden;
        }
        .details-panel .hazard-stripe {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          border-radius: 0;
        }
        .details-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 4px 0;
        }
        .details-label {
          font-size: 13px;
        }
        .details-value {
          font-size: 14.5px;
        }
        .expired-note {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border);
          color: var(--rust-500);
          font-size: 13.5px;
          line-height: 1.6;
        }
        .details-actions {
          display: flex;
          gap: 10px;
          margin-top: 18px;
        }
      `}</style>
    </div>
  )
}
