import { useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import TopBar from './components/TopBar.jsx'

import Dashboard from './pages/Dashboard.jsx'
import ScanBadge from './pages/ScanBadge.jsx'
import BadgeDetails from './pages/BadgeDetails.jsx'
import ReadSensor from './pages/ReadSensor.jsx'
import Analyzing from './pages/Analyzing.jsx'
import Result from './pages/Result.jsx'
import History from './pages/History.jsx'
import Workers from './pages/Workers.jsx'

// Top-level nav sections the sidebar can jump straight to.
const NAV_VIEWS = new Set(['dashboard', 'scan', 'workers', 'history'])

export default function App() {
  const [view, setView] = useState('dashboard')
  const [activeBadge, setActiveBadge] = useState(null) // { badgeId, worker, status, ... }
  const [analysisResult, setAnalysisResult] = useState(null)
  const [historyWorkerId, setHistoryWorkerId] = useState(null)

  function goTo(nextView) {
    setView(nextView)
  }

  function handleSidebarNavigate(key) {
    if (key === 'history' && !historyWorkerId) {
      // land on the worker picker inside history if none chosen yet
      setView('history')
      return
    }
    setView(key)
  }

  function handleBadgeSelected(badge) {
    setActiveBadge(badge)
    setView('badge')
  }

  function handleReadSensor() {
    setView('sensor')
  }

  function handleCaptured() {
    setView('analyzing')
  }

  function handleAnalysisComplete(result) {
    setAnalysisResult(result)
    setView('result')
  }

  function handleSaved() {
    setHistoryWorkerId(activeBadge?.worker?.id || null)
    setView('history')
  }

  function handleOpenWorkerHistory(workerId) {
    setHistoryWorkerId(workerId)
    setView('history')
  }

  return (
    <div className="app-shell">
      <Sidebar active={NAV_VIEWS.has(view) ? view : 'dashboard'} onNavigate={handleSidebarNavigate} />

      <div className="main-column">
        <TopBar />

        <main className="view">
          {view === 'dashboard' && (
            <Dashboard onScan={() => goTo('scan')} onOpenWorker={handleOpenWorkerHistory} />
          )}

          {view === 'scan' && <ScanBadge onSelected={handleBadgeSelected} onCancel={() => goTo('dashboard')} />}

          {view === 'badge' && activeBadge && (
            <BadgeDetails
              badge={activeBadge}
              onReadSensor={handleReadSensor}
              onBack={() => goTo('scan')}
            />
          )}

          {view === 'sensor' && activeBadge && (
            <ReadSensor badge={activeBadge} onCaptured={handleCaptured} onBack={() => goTo('badge')} />
          )}

          {view === 'analyzing' && activeBadge && (
            <Analyzing badge={activeBadge} onComplete={handleAnalysisComplete} />
          )}

          {view === 'result' && activeBadge && analysisResult && (
            <Result badge={activeBadge} result={analysisResult} onSaved={handleSaved} />
          )}

          {view === 'workers' && <Workers onOpenWorker={handleOpenWorkerHistory} />}

          {view === 'history' && (
            <History workerId={historyWorkerId} onSelectWorker={setHistoryWorkerId} />
          )}
        </main>
      </div>
    </div>
  )
}
