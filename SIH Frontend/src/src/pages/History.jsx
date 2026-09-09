import { useEffect, useState } from 'react'
import ExposureChart from '../components/ExposureChart.jsx'
import { fetchWorkers, fetchWorkerHistory } from '../services/mockApi.js'

export default function History({ workerId, onSelectWorker }) {
  const [workers, setWorkers] = useState([])
  const [readings, setReadings] = useState(null)

  useEffect(() => {
    fetchWorkers().then(setWorkers)
  }, [])

  useEffect(() => {
    if (!workerId) return
    setReadings(null)
    fetchWorkerHistory(workerId).then(setReadings)
  }, [workerId])

  if (!workerId) {
    return (
      <div>
        <div className="page-title">Exposure history</div>
        <div className="page-sub">Choose a worker to view their reading history.</div>

        <div className="worker-pick-list">
          {workers.map((w) => (
            <button key={w.id} className="worker-pick" onClick={() => onSelectWorker(w.id)}>
              <span>{w.name}</span>
              <span className="text-muted mono">{w.badgeId}</span>
            </button>
          ))}
        </div>

        <style>{`
          .worker-pick-list {
            margin-top: 18px;
            display: flex;
            flex-direction: column;
            gap: 8px;
          }
          .worker-pick {
            display: flex;
            justify-content: space-between;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 14px 16px;
            cursor: pointer;
            color: var(--text-primary);
            text-align: left;
          }
          .worker-pick:hover {
            border-color: var(--amber-400);
          }
        `}</style>
      </div>
    )
  }

  const worker = workers.find((w) => w.id === workerId)

  return (
    <div>
      <div className="page-title">Exposure history</div>
      <div className="page-sub">{worker?.name || 'Worker'}</div>

      <button className="btn btn-secondary" style={{ marginTop: 12 }} onClick={() => onSelectWorker(null)}>
        Choose a different worker
      </button>

      <div className="panel chart-panel">
        {readings ? <ExposureChart data={readings} /> : <div className="text-muted">Loading…</div>}
      </div>

      <div className="panel table-panel">
        {readings && readings.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th className="num">Dose (ppm·min)</th>
                <th className="num">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {[...readings].reverse().map((r) => (
                <tr key={r.id}>
                  <td className="mono">{r.date}</td>
                  <td className="num mono">{r.doseEstimate.toFixed(1)}</td>
                  <td className="num mono">{Math.round(r.confidence * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-muted">No readings logged yet for this worker.</div>
        )}
      </div>

      <style>{`
        .chart-panel, .table-panel {
          margin-top: 16px;
        }
      `}</style>
    </div>
  )
}
