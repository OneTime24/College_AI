export function StatusPill({ value }: { value: string | boolean }) {
  const label = typeof value === 'boolean' ? (value ? 'ONLINE' : 'OFFLINE') : value.replaceAll('_', ' ').toUpperCase()
  const good = value === true || value === 'online' || value === 'reporting' || value === 'on' || value === 'active'
  return <span className={`status-pill ${good ? 'good' : 'neutral'}`}><i />{label}</span>
}
