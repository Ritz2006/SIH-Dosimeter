export default function TopBar() {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <span className="mono topbar-code">H2S</span>
        <span>Guard</span>
      </div>
      <div className="topbar-site text-muted mono">Field Site B-12</div>

      <style>{`
        .topbar {
          height: 56px;
          border-bottom: 1px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 24px;
          background: var(--bg);
        }
        .topbar-title {
          display: flex;
          align-items: baseline;
          gap: 8px;
          font-size: 15px;
          font-weight: 600;
        }
        .topbar-code {
          color: var(--amber-400);
          font-size: 13px;
          letter-spacing: 0.04em;
        }
        .topbar-site {
          font-size: 12.5px;
        }
        @media (max-width: 480px) {
          .topbar-site { display: none; }
        }
      `}</style>
    </header>
  )
}
