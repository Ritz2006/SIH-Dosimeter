export default function ExposureChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-muted">No readings yet.</div>
  }

  const width = 640
  const height = 180
  const padX = 36
  const padY = 20

  const values = data.map((d) => d.doseEstimate)
  const maxV = Math.max(...values) * 1.15
  const minV = 0

  const stepX = (width - padX * 2) / Math.max(1, data.length - 1)

  const points = data.map((d, i) => {
    const x = padX + i * stepX
    const y = height - padY - ((d.doseEstimate - minV) / (maxV - minV)) * (height - padY * 2)
    return { x, y, ...d }
  })

  const path = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')

  const gridLines = [0.25, 0.5, 0.75, 1].map((f) => height - padY - f * (height - padY * 2))

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label="Exposure trend over time">
      {gridLines.map((y, i) => (
        <line key={i} x1={padX} x2={width - padX} y1={y} y2={y} stroke="var(--border)" strokeWidth="1" />
      ))}

      <path d={path} fill="none" stroke="var(--amber-400)" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />

      {points.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="3.5" fill="var(--bg)" stroke="var(--amber-400)" strokeWidth="2" />
          <text x={p.x} y={height - 4} textAnchor="middle" fontSize="9.5" fontFamily="IBM Plex Mono, monospace" fill="var(--text-muted)">
            {p.date.slice(5)}
          </text>
        </g>
      ))}
    </svg>
  )
}
