const VARIANTS = {
  valid: { className: 'pill-valid', label: 'Valid' },
  expired: { className: 'pill-expired', label: 'Expired' },
  pending: { className: 'pill-pending', label: 'Pending' }
}

export default function StatusPill({ status, label }) {
  const variant = VARIANTS[status] || VARIANTS.pending
  return (
    <span className={`pill ${variant.className}`}>
      <span className="pill-dot" />
      {label || variant.label}
    </span>
  )
}
