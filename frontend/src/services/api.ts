import type { AIChatResponse, AIStatus, Device, Event, Room, SystemStatus } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
const DASHBOARD_KEY_STORAGE = 'ai-college-dashboard-key'

export function setDashboardKey(key: string) { localStorage.setItem(DASHBOARD_KEY_STORAGE, key) }
export function clearDashboardKey() { localStorage.removeItem(DASHBOARD_KEY_STORAGE) }

async function request<T>(path: string): Promise<T> {
  const key = localStorage.getItem(DASHBOARD_KEY_STORAGE)
  const response = await fetch(`${API_URL}${path}`, { headers: key ? { 'X-Dashboard-Key': key } : undefined })
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  return response.json() as Promise<T>
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const key = localStorage.getItem(DASHBOARD_KEY_STORAGE)
  const response = await fetch(`${API_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(key ? { 'X-Dashboard-Key': key } : {}) }, body: JSON.stringify(body) })
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(payload?.detail ?? `API request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

async function postBlob(path: string, body: unknown): Promise<Blob> {
  const key = localStorage.getItem(DASHBOARD_KEY_STORAGE)
  const response = await fetch(`${API_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(key ? { 'X-Dashboard-Key': key } : {}) }, body: JSON.stringify(body) })
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(payload?.detail ?? `API request failed (${response.status})`)
  }
  return response.blob()
}

export const api = {
  dashboardAccess: () => request<{ allowed: boolean }>('/access/dashboard'),
  status: () => request<SystemStatus>('/system/status'),
  aiStatus: () => request<AIStatus>('/ai/status'),
  chat: (message: string, images: string[] = [], audio: string[] = []) => post<AIChatResponse>('/ai/chat', { message, images, audio }),
  speak: (text: string) => postBlob('/speech/tts', { text }),
  rooms: () => request<Room[]>('/rooms'),
  devices: () => request<Device[]>('/devices'),
  events: (filters: { location?: string; event_type?: string } = {}) => request<Event[]>(`/events?limit=50&${new URLSearchParams(Object.entries(filters).filter(([, v]) => v) as [string, string][]).toString()}`),
}
