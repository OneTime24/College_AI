import { FormEvent, useEffect, useState } from 'react'
import { Bot, RotateCcw, Send, User } from 'lucide-react'
import { PageTitle } from './Dashboard'
import { api } from '../services/api'
import type { AIStatus } from '../types'
import { StatusPill } from '../components/StatusPill'
import './Assistant.css'

type Message = { role: 'user' | 'assistant'; content: string }

export function Assistant({ aiStatus, refreshStatus }: { aiStatus?: AIStatus; refreshStatus: () => Promise<void> }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { void refreshStatus() }, [refreshStatus])
  const available = aiStatus?.status === 'online'
  async function submit(event: FormEvent) {
    event.preventDefault()
    const text = message.trim()
    if (!text || loading) return
    setError(''); setMessages(previous => [...previous, { role: 'user', content: text }]); setMessage(''); setLoading(true)
    try { const result = await api.chat(text); setMessages(previous => [...previous, { role: 'assistant', content: result.response }]); await refreshStatus() }
    catch (err) { setError(err instanceof Error ? err.message : 'Local AI engine is currently unavailable.'); await refreshStatus() }
    finally { setLoading(false) }
  }
  return <><PageTitle title="AI COLLEGE ASSISTANT" text="Private local AI assistance powered by the configured on-device model" /><section className="assistant-panel panel"><header className="assistant-head"><div><div className="assistant-status"><Bot size={18}/><div><h2>Local AI</h2><p>{aiStatus?.model ?? 'Checking local runtime…'}</p></div></div><StatusPill value={available ? 'online' : 'offline'} /></div><button className="clear-button" onClick={() => { setMessages([]); setError('') }} disabled={!messages.length || loading}><RotateCcw size={14}/> Clear conversation</button></header>{!available && <div className="assistant-notice">Local AI engine is currently unavailable. Start Ollama and ensure the configured model is installed.</div>}<div className="conversation" aria-live="polite">{!messages.length && <div className="conversation-empty"><Bot size={25}/><strong>How can I help?</strong><span>Ask a general question. Responses are generated locally and are not sent to cloud AI services.</span></div>}{messages.map((item, index) => <article className={`chat-message ${item.role}`} key={`${item.role}-${index}`}><div className="message-icon">{item.role === 'user' ? <User size={15}/> : <Bot size={15}/>}</div><p>{item.content}</p></article>)}{loading && <article className="chat-message assistant"><div className="message-icon"><Bot size={15}/></div><p className="typing">AI College Assistant is thinking…</p></article>}</div>{error && <div className="assistant-error">{error}</div>}<form className="chat-form" onSubmit={submit}><textarea value={message} onChange={event => setMessage(event.target.value)} placeholder={available ? 'Ask the local AI assistant…' : 'Local AI is unavailable'} disabled={loading || !available} maxLength={8000} rows={2}/><button type="submit" disabled={loading || !available || !message.trim()} aria-label="Send message"><Send size={18}/></button></form></section></>
}
