import { ChangeEvent, FormEvent, useEffect, useRef, useState } from 'react'
import { Bot, ImagePlus, Mic, MicOff, RotateCcw, Send, User, Volume2, VolumeX, X } from 'lucide-react'
import { PageTitle } from './Dashboard'
import { api } from '../services/api'
import type { AIStatus } from '../types'
import { StatusPill } from '../components/StatusPill'
import './Assistant.css'

type Message = { role: 'user' | 'assistant'; content: string; images?: string[] }
type Attachment = { name: string; dataUrl: string }

function readAsDataURL(file: File): Promise<Attachment> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error(`Could not read ${file.name}`))
    reader.onload = () => resolve({ name: file.name, dataUrl: String(reader.result ?? '') })
    reader.readAsDataURL(file)
  })
}

function dataUrlFromBlob(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Could not read recorded audio.'))
    reader.onload = () => resolve(String(reader.result ?? ''))
    reader.readAsDataURL(blob)
  })
}

export function Assistant({ aiStatus, refreshStatus }: { aiStatus?: AIStatus; refreshStatus: () => Promise<void> }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [recording, setRecording] = useState(false)
  const [recordedAudio, setRecordedAudio] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [voiceError, setVoiceError] = useState('')
  const [speakReplies, setSpeakReplies] = useState(false)
  const [voiceReplyError, setVoiceReplyError] = useState('')
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioStreamRef = useRef<MediaStream | null>(null)

  useEffect(() => { void refreshStatus() }, [refreshStatus])
  useEffect(() => () => {
    mediaRecorderRef.current?.stop()
    audioStreamRef.current?.getTracks().forEach(track => track.stop())
  }, [])

  const available = aiStatus?.status === 'online'
  const imageSupported = aiStatus?.supports_image_input ?? false
  const voiceSupported = aiStatus?.supports_voice_input ?? false
  const voiceOutputSupported = aiStatus?.supports_voice_output ?? false
  const voiceInputEngine = aiStatus?.voice_input_engine ?? 'unavailable'
  const voiceOutputEngine = aiStatus?.voice_output_engine ?? 'unavailable'
  const canSubmit = available && !loading && !recording && (message.trim().length > 0 || attachments.length > 0 || recordedAudio.length > 0) && (attachments.length === 0 || imageSupported)

  async function sendChat(text: string, imagePayloads: string[], audioPayloads: string[]) {
    if (imagePayloads.length > 0 && !imageSupported) {
      setError('This model does not currently accept image input.')
      return
    }

    setError('')
    setLoading(true)

    try {
      const result = await api.chat(text, imagePayloads, audioPayloads)
      const userContent = result.transcript?.trim() || text || 'Voice input'
      setMessages(previous => [
        ...previous,
        { role: 'user', content: userContent, images: imagePayloads },
        { role: 'assistant', content: result.response },
      ])
      setMessage('')
      setAttachments([])
      setRecordedAudio('')
      if (speakReplies && voiceOutputSupported) {
        try {
          const audio = await api.speak(result.response)
          const url = URL.createObjectURL(audio)
          const playback = new Audio(url)
          playback.onended = () => URL.revokeObjectURL(url)
          playback.onerror = () => URL.revokeObjectURL(url)
          void playback.play()
        } catch (speechErr) {
          setVoiceReplyError(speechErr instanceof Error ? speechErr.message : 'Voice reply could not be generated locally.')
        }
      }
      await refreshStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Local AI engine is currently unavailable.')
      await refreshStatus()
    } finally {
      setLoading(false)
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    const text = message.trim()
    if (!text && !attachments.length && !recordedAudio) return
    await sendChat(text, attachments.map(item => item.dataUrl), recordedAudio ? [recordedAudio] : [])
  }

  async function handleFiles(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? [])
    if (!files.length) return
    const loaded = await Promise.all(files.slice(0, 3).map(readAsDataURL))
    setAttachments(previous => [...previous, ...loaded])
    event.target.value = ''
  }

  function removeAttachment(index: number) {
    setAttachments(previous => previous.filter((_, itemIndex) => itemIndex !== index))
  }

  async function toggleRecording() {
    setVoiceError('')
    if (recording) {
      mediaRecorderRef.current?.stop()
      audioStreamRef.current?.getTracks().forEach(track => track.stop())
      setRecording(false)
      return
    }
    if (!voiceSupported) {
      setVoiceError('This browser cannot access the microphone.')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioStreamRef.current = stream
      audioChunksRef.current = []
      setRecordedAudio('')
      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder
      recorder.ondataavailable = event => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data)
      }
      recorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        const dataUrl = await dataUrlFromBlob(blob)
        audioChunksRef.current = []
        mediaRecorderRef.current = null
        setRecording(false)
        if (!message.trim() && !attachments.length) {
          await sendChat('', [], [dataUrl])
          return
        }
        setRecordedAudio(dataUrl)
      }
      recorder.start()
      setRecording(true)
    } catch {
      setVoiceError('Microphone permission was denied or unavailable.')
    }
  }

  return (
    <>
      <PageTitle title="AI COLLEGE ASSISTANT" text="Private local AI assistance powered by the configured on-device model" />
      <section className="assistant-panel panel">
        <header className="assistant-head">
          <div>
            <div className="assistant-status">
              <Bot size={18} />
              <div>
                <h2>Local AI</h2>
                <p>{aiStatus?.model ?? 'Checking local runtime…'}</p>
              </div>
            </div>
            <StatusPill value={available ? 'online' : 'offline'} />
          </div>
          <div className="assistant-head-actions">
            <button className="tool-button" type="button" onClick={() => setSpeakReplies(previous => !previous)} disabled={!voiceOutputSupported}>
              {speakReplies ? <Volume2 size={15} /> : <VolumeX size={15} />}
              {speakReplies ? 'Voice reply on' : 'Voice reply off'}
            </button>
            <button className="clear-button" onClick={() => { setMessages([]); setError(''); setRecordedAudio('') }} disabled={!messages.length || loading}>
              <RotateCcw size={14} /> Clear conversation
            </button>
          </div>
        </header>

        {!available && <div className="assistant-notice">Local AI engine is currently unavailable. Start Ollama and ensure the configured model is installed.</div>}
        {attachments.length > 0 && !imageSupported && <div className="assistant-notice">Image attachments are ready, but the current model is not vision-capable yet.</div>}
        {!voiceSupported && <div className="assistant-notice">Voice input is not available until whisper.cpp is configured locally.</div>}
        {voiceSupported && <div className="assistant-notice">Voice input engine: {voiceInputEngine}</div>}
        {voiceOutputSupported && speakReplies && <div className="assistant-notice">Replies will be spoken locally with {voiceOutputEngine}.</div>}
        {voiceError && <div className="assistant-error">{voiceError}</div>}
        {voiceReplyError && <div className="assistant-error">{voiceReplyError}</div>}

        <div className="conversation" aria-live="polite">
          {!messages.length && (
            <div className="conversation-empty">
              <Bot size={25} />
              <strong>How can I help?</strong>
              <span>Type a prompt, record your voice, or attach an image when the selected model supports it.</span>
            </div>
          )}
          {messages.map((item, index) => (
            <article className={`chat-message ${item.role}`} key={`${item.role}-${index}`}>
              <div className="message-icon">{item.role === 'user' ? <User size={15} /> : <Bot size={15} />}</div>
              <div className="message-body">
                {item.images?.length ? (
                  <div className="message-images">
                    {item.images.map((src, imageIndex) => <img alt={`Attachment ${imageIndex + 1}`} src={src} key={`${index}-${imageIndex}`} />)}
                  </div>
                ) : null}
                <p>{item.content}</p>
              </div>
            </article>
          ))}
          {loading && (
            <article className="chat-message assistant">
              <div className="message-icon"><Bot size={15} /></div>
              <p className="typing">AI College Assistant is thinking…</p>
            </article>
          )}
        </div>

        {error && <div className="assistant-error">{error}</div>}

        <form className="chat-form" onSubmit={submit}>
          <div className="chat-compose">
            <textarea
              value={message}
              onChange={event => setMessage(event.target.value)}
              placeholder={available ? 'Ask the local AI assistant…' : 'Local AI is unavailable'}
              disabled={loading || !available}
              maxLength={8000}
              rows={3}
            />
            {recordedAudio && <div className="assistant-notice">Recorded voice ready to send.</div>}
            {attachments.length > 0 && (
              <div className="attachment-strip">
                {attachments.map((item, index) => (
                  <div className="attachment-chip" key={`${item.name}-${index}`}>
                    <img alt={item.name} src={item.dataUrl} />
                    <span>{item.name}</span>
                    <button type="button" onClick={() => removeAttachment(index)} aria-label={`Remove ${item.name}`}>
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            <div className="chat-tools">
              <button type="button" className="tool-button" onClick={() => fileInputRef.current?.click()} disabled={loading || !available}>
                <ImagePlus size={15} /> Image
              </button>
              <button type="button" className={`tool-button ${recording ? 'active' : ''}`} onClick={() => void toggleRecording()} disabled={loading || !available || !voiceSupported}>
                {recording ? <MicOff size={15} /> : <Mic size={15} />}
                {recording ? 'Stop' : 'Voice'}
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" multiple onChange={handleFiles} hidden />
              <div className="tool-hint">{voiceSupported ? `Voice input is powered by ${voiceInputEngine}.` : 'Configure whisper.cpp locally to enable voice input.'}</div>
            </div>
          </div>
          <button type="submit" disabled={!canSubmit} aria-label="Send message">
            <Send size={18} />
          </button>
        </form>
      </section>
    </>
  )
}
