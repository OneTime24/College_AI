import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Loading } from './components/Loading'
import { api, clearDashboardKey, setDashboardKey } from './services/api'
import { Assistant } from './pages/Assistant'
import type { AIStatus } from './types'

function AssistantPage() {
  const [aiStatus, setAiStatus] = useState<AIStatus>()
  const refreshStatus = useCallback(async () => {
    try {
      setAiStatus(await api.aiStatus())
    } catch {
      setAiStatus(undefined)
    }
  }, [])

  useEffect(() => {
    void refreshStatus()
  }, [refreshStatus])

  return <main className="assistant-page"><Assistant aiStatus={aiStatus} refreshStatus={refreshStatus} /></main>
}

function DashboardLogin({ onSuccess }: { onSuccess: () => void }) {
  const [key, setKey] = useState('')
  const [error, setError] = useState('')

  async function submit(event: FormEvent) {
    event.preventDefault()
    setDashboardKey(key)
    try {
      await api.dashboardAccess()
      onSuccess()
    } catch {
      clearDashboardKey()
      setError('Invalid dashboard access key.')
    }
  }

  return (
    <main className="access-page">
      <section className="panel access-panel">
        <h1>AI COLLEGE</h1>
        <p>This address is restricted to authorized users. Set <code>DASHBOARD_ACCESS_KEY</code> in <code>.env</code> on the backend side.</p>
        <form onSubmit={submit}>
          <input type="password" value={key} onChange={event => setKey(event.target.value)} placeholder="Dashboard access key" autoFocus />
          <button type="submit">Enter dashboard</button>
        </form>
        <button className="clear-button" onClick={() => { clearDashboardKey(); setKey(''); setError('') }} type="button">
          Clear saved key
        </button>
        {error && <div className="error">{error}</div>}
      </section>
    </main>
  )
}

export default function App() {
  const assistantMode = import.meta.env.VITE_APP_MODE === 'assistant'
  const [authorized, setAuthorized] = useState<boolean | undefined>(assistantMode ? true : undefined)

  useEffect(() => {
    if (assistantMode) return
    api.dashboardAccess().then(() => setAuthorized(true)).catch(() => setAuthorized(false))
  }, [assistantMode])

  if (assistantMode) return <AssistantPage />
  if (authorized === false) return <DashboardLogin onSuccess={() => setAuthorized(true)} />
  if (authorized !== true) return <Loading />
  return <AssistantPage />
}
