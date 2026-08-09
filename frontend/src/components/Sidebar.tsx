import { Activity, Bot, Building2, Cable, LayoutDashboard, Settings } from 'lucide-react'

export type Page = 'dashboard' | 'rooms' | 'devices' | 'activity' | 'assistant' | 'settings'
const items: [Page, string, typeof LayoutDashboard][] = [['dashboard', 'Dashboard', LayoutDashboard], ['rooms', 'Rooms', Building2], ['devices', 'Devices', Cable], ['activity', 'Activity', Activity], ['assistant', 'AI Assistant', Bot], ['settings', 'Settings', Settings]]
export function Sidebar({ page, setPage, aiStatus }: { page: Page; setPage: (p: Page) => void; aiStatus?: string }) {
  return <aside className="sidebar"><div className="brand"><div className="brand-mark">AI</div><div><strong>AI COLLEGE</strong><small>Infrastructure</small></div></div><nav>{items.map(([id, label, Icon]) => <button key={id} className={page === id ? 'active' : ''} onClick={() => setPage(id)}><Icon size={18}/><span>{label}</span></button>)}</nav><div className="sidebar-footer"><small>LOCAL AI</small><StatusPill value={aiStatus === 'online' ? 'online' : 'offline'}/><span>Local runtime status</span></div></aside>
}
function StatusPill({ value }: { value: string }) { return <span className="status-pill good"><i />{value.toUpperCase()}</span> }
