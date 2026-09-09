export default function ExposureReadout({ value, confidence, maxForScale = 35 }) {
  const ratio = Math.min(1, value / maxForScale)
  const segments = 12
  const filled = Math.round(ratio * segments)

  return (
    <div className="readout">
      <div className="readout-label">Estimated cumulative exposure</div>
      <div className="readout-value">
        <span className="mono readout-number">{value.toFixed(1)}</span>
        <span className="readout-unit mono">ppm·min</span>
      </div>

      <div className="readout-bar" aria-hidden="true">
        {Array.from({ length: segments }).map((_, i) => (
          <span key={i} className={`readout-seg${i < filled ? ' filled' : ''}`} />
        ))}
      </div>
      <div className="readout-scale-label text-muted mono">Relative exposure level — not a calibrated threshold</div>

      <div className="readout-confidence text-muted">
        Confidence <span className="mono">{Math.round(confidence * 100)}%</span>
      </div>

      <style>{`
        .readout-label {
          font-size: 12.5px;
          text-transform: none;
          color: var(--text-secondary);
          margin-bottom: 6px;
        }
        .readout-value {
          display: flex;
          align-items: baseline;
          gap: 8px;
        }
        .readout-number {
          font-size: 48px;
          font-weight: 500;
          color: var(--amber-400);
          line-height: 1;
        }
        .readout-unit {
          font-size: 14px;
          color: var(--text-muted);
        }
        .readout-bar {
          display: flex;
          gap: 3px;
          margin-top: 16px;
        }
        .readout-seg {
          height: 8px;
          flex: 1;
          background: var(--surface-2);
          border-radius: 1px;
        }
        .readout-seg.filled {
          background: var(--amber-400);
        }
        .readout-scale-label {
          font-size: 11px;
          margin-top: 6px;
        }
        .readout-confidence {
          margin-top: 14px;
          font-size: 13px;
        }
      `}</style>
    </div>
  )
}
