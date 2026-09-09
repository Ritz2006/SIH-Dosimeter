import WristbandIcon from '../components/WristbandIcon.jsx'

const CHECKS = ['Good lighting', 'Reference scale visible', 'Sensor patch visible']

export default function ReadSensor({ badge, onCaptured, onBack }) {
  return (
    <div>
      <div className="page-title">Read sensor</div>
      <div className="page-sub">Place the badge inside the frame, reference scale facing the camera.</div>

      <div className="panel camera-panel">
        <div className="camera-frame">
          <WristbandIcon size={230} tone="amber" />
        </div>
        <ul className="camera-checks">
          {CHECKS.map((c) => (
            <li key={c}>
              <CheckIcon /> {c}
            </li>
          ))}
        </ul>
      </div>

      <div className="details-actions">
        <button className="btn btn-secondary" onClick={onBack}>
          Back
        </button>
        <button className="btn btn-primary" onClick={onCaptured}>
          Capture
        </button>
      </div>

      <style>{`
        .camera-panel {
          margin-top: 18px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          padding: 30px;
        }
        .camera-frame {
          border: 1px dashed var(--border-strong);
          border-radius: var(--radius-md);
          padding: 20px 28px;
          background: var(--bg-raised);
        }
        .camera-checks {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 8px;
          width: 100%;
          max-width: 260px;
        }
        .camera-checks li {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13.5px;
          color: var(--text-secondary);
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

function CheckIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
      <circle cx="7.5" cy="7.5" r="7" stroke="#5fa776" strokeWidth="1.3" />
      <path d="M4.5 7.7l2 2 4-4.4" stroke="#5fa776" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
