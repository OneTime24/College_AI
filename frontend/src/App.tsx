import { FormEvent, useEffect, useState } from 'react'
import { api } from './services/api'
import type { AIStatus } from './types'

type Message = { role: 'user' | 'assistant'; content: string }

export default function App() {
  const [status, setStatus] = useState<AIStatus>()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function refreshStatus() {
    try { setStatus(await api.aiStatus()) } catch { setStatus(undefined) }
  }

  useEffect(() => { void refreshStatus() }, [])

  async function submit(event: FormEvent) {
    event.preventDefault()
    const message = input.trim()
    if (!message || loading) return
    setError('')
    setMessages(previous => [...previous, { role: 'user', content: message }])
    setInput('')
    setLoading(true)
    try {
      const result = await api.chat(message)
      setMessages(previous => [...previous, { role: 'assistant', content: result.response }])
      await refreshStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The local LLM is unavailable.')
    } finally { setLoading(false) }
  }

  const online = status?.status === 'online'
  return <main>
    <header>
      <div><p className="eyebrow">LOCAL LLM</p><h1>AI Assistant</h1></div>
      <span className={online ? 'status online' : 'status'}>{online ? 'online' : 'offline'}{status?.model ? ` · ${status.model}` : ''}</span>
    </header>
    <section className="chat" aria-live="polite">
      {!messages.length && <p className="empty">Ask your local model anything.</p>}
      {messages.map((item, index) => <article className={item.role} key={`${item.role}-${index}`}><strong>{item.role === 'user' ? 'You' : 'AI'}</strong><p>{item.content}</p></article>)}
      {loading && <article className="assistant"><strong>AI</strong><p>Thinking…</p></article>}
    </section>
    {error && <p className="error">{error}</p>}
    {!online && <p className="hint">Start Ollama and make sure the configured model is installed.</p>}
    <form onSubmit={submit}><textarea value={input} onChange={event => setInput(event.target.value)} placeholder="Message the local LLM…" disabled={!online || loading} rows={3} /><button disabled={!online || loading || !input.trim()}>{loading ? 'Thinking…' : 'Send'}</button></form>
  </main>
}
