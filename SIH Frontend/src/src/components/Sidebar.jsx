const NAV_ITEMS = [
  { key: 'dashboard', label: 'Dashboard', icon: IconGauge },
  { key: 'scan', label: 'Scan badge', icon: IconScan },
  { key: 'workers', label: 'Workers', icon: IconWorkers },
  { key: 'history', label: 'History', icon: IconHistory }
]

export default function Sidebar({ active, onNavigate }) {
  return (
    <nav className="sidebar" aria-label="Primary">
      <div className="sidebar-mark" aria-hidden="true">
        <MarkIcon />
      </div>
      <ul className="sidebar-list">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = active === item.key
          return (
            <li key={item.key}>
              <button
                className={`sidebar-btn${isActive ? ' active' : ''}`}
                onClick={() => onNavigate(item.key)}
                aria-current={isActive ? 'page' : undefined}
                title={item.label}
              >
                <Icon />
                <span className="sidebar-label">{item.label}</span>
              </button>
            </li>
          )
        })}
      </ul>

      <style>{`
        .sidebar {
          background: var(--bg-raised);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 18px 0;
        }
        .sidebar-mark {
          margin-bottom: 24px;
          color: var(--amber-400);
        }
        .sidebar-list {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 4px;
          width: 100%;
        }
        .sidebar-btn {
          width: 100%;
          background: none;
          border: none;
          border-left: 2px solid transparent;
          color: var(--text-muted);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          padding: 10px 4px;
          cursor: pointer;
          font-family: var(--font-ui);
          font-size: 10px;
        }
        .sidebar-btn:hover {
          color: var(--text-primary);
        }
        .sidebar-btn.active {
          color: var(--amber-400);
          border-left-color: var(--amber-400);
          background: rgba(227, 167, 59, 0.06);
        }
        .sidebar-label {
          font-size: 10px;
          letter-spacing: 0.01em;
        }

        @media (max-width: 720px) {
          .sidebar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            top: auto;
            flex-direction: row;
            justify-content: space-around;
            border-right: none;
            border-top: 1px solid var(--border);
            padding: 8px 0;
            z-index: 20;
          }
          .sidebar-mark {
            display: none;
          }
          .sidebar-list {
            flex-direction: row;
            justify-content: space-around;
          }
          .sidebar-btn {
            border-left: none;
            border-top: 2px solid transparent;
          }
          .sidebar-btn.active {
            border-top-color: var(--amber-400);
            border-left-color: transparent;
          }
        }
      `}</style>
    </nav>
  )
}

function MarkIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
      <circle cx="13" cy="13" r="11" stroke="currentColor" strokeWidth="1.6" />
      <path d="M13 6.5v6.5l4.2 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

function IconGauge() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M3 15a7 7 0 0 1 14 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M10 15 13 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="10" cy="15" r="1.1" fill="currentColor" />
    </svg>
  )
}

function IconScan() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M3 7V4.5A1.5 1.5 0 0 1 4.5 3H7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M13 3h2.5A1.5 1.5 0 0 1 17 4.5V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M17 13v2.5a1.5 1.5 0 0 1-1.5 1.5H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M7 17H4.5A1.5 1.5 0 0 1 3 15.5V13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M6.5 10h7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function IconWorkers() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="7.2" cy="7" r="2.4" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="14" cy="8" r="1.9" stroke="currentColor" strokeWidth="1.5" />
      <path d="M2.8 16c.5-2.8 2.2-4.3 4.4-4.3s3.9 1.5 4.4 4.3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M12.6 12.4c1.7.2 2.9 1.5 3.3 3.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function IconHistory() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M3 10a7 7 0 1 1 2.2 5.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M3 6v4h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 7v3.3l2.4 1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}
