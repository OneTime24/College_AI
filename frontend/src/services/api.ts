import type { AIChatResponse, AIStatus } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`)
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  return response.json() as Promise<T>
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(payload?.detail ?? `API request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  aiStatus: () => request<AIStatus>('/ai/status'),
  chat: (message: string) => post<AIChatResponse>('/ai/chat', { message }),
}
