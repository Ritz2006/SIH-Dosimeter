import { useEffect, useState } from 'react'
import WristbandIcon from '../components/WristbandIcon.jsx'
import { fetchTodayCount, fetchWorkers } from '../services/mockApi.js'

export default function Dashboard({ onScan, onOpenWorker }) {
  const [todayCount, setTodayCount] = useState(null)
  const [workers, setWorkers] = useState([])

  useEffect(() => {
    fetchTodayCount().then(setTodayCount)
    fetchWorkers().then(setWorkers)
  }, [])

  return (
    <div>
      <div className="page-title">Dashboard</div>
      <div className="page-sub">Passive H₂S exposure monitoring for Field Site B-12.</div>

      <div className="hero panel panel-accent">
        <div className="hero-copy">
          <h2 className="hero-heading">Read a badge</h2>
          <p className="hero-text text-secondary">
            Scan the QR code on a worker's wristband, then photograph the sensor strip
            to log today's estimated exposure.
          </p>
          <button className="btn btn-primary" onClick={onScan}>
            Scan badge
          </button>
        </div>
        <div className="hero-art" aria-hidden="true">
          <WristbandIcon size={200} />
        </div>
      </div>

      <div className="stat-row">
        <div className="panel stat-card">
          <div className="stat-value mono">{todayCount ?? '—'}</div>
          <div className="stat-label text-muted">Readings logged today</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value mono">{workers.length || '—'}</div>
          <div className="stat-label text-muted">Workers on badge programme</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value mono">30</div>
          <div className="stat-label text-muted">Days badge shelf life</div>
        </div>
      </div>

      <div className="section-heading">Workers</div>
      <div className="panel">
        <ul className="worker-quick-list">
          {workers.map((w) => (
            <li key={w.id}>
              <button className="worker-quick-item" onClick={() => onOpenWorker(w.id)}>
                <span>{w.name}</span>
                <span className="text-muted mono">{w.badgeId}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <style>{`
        .hero {
          margin-top: 22px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
          flex-wrap: wrap;
        }
        .hero-copy {
          max-width: 340px;
        }
        .hero-heading {
          font-size: 20px;
          margin-bottom: 8px;
        }
        .hero-text {
          font-size: 14px;
          margin: 0 0 18px;
          line-height: 1.6;
        }
        .stat-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-top: 20px;
        }
        @media (max-width: 560px) {
          .stat-row { grid-template-columns: 1fr; }
        }
        .stat-card {
          padding: 16px 18px;
        }
        .stat-value {
          font-size: 28px;
          color: var(--amber-400);
          font-weight: 500;
        }
        .stat-label {
          font-size: 12.5px;
          margin-top: 4px;
        }
        .section-heading {
          margin-top: 28px;
          margin-bottom: 10px;
          font-size: 13px;
          color: var(--text-secondary);
        }
        .worker-quick-list {
          list-style: none;
          margin: 0;
          padding: 0;
        }
        .worker-quick-item {
          width: 100%;
          background: none;
          border: none;
          border-bottom: 1px solid var(--border);
          padding: 12px 4px;
          display: flex;
          justify-content: space-between;
          color: var(--text-primary);
          cursor: pointer;
          font-size: 14px;
          text-align: left;
        }
        .worker-quick-list li:last-child .worker-quick-item {
          border-bottom: none;
        }
        .worker-quick-item:hover {
          color: var(--amber-400);
        }
      `}</style>
    </div>
  )
}
