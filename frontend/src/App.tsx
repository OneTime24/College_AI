import { useCallback, useEffect, useState } from 'react'
import { Sidebar, type Page } from './components/Sidebar'
import { Loading } from './components/Loading'
import { api } from './services/api'
import type { AIStatus, Device, Event, Room, SystemStatus } from './types'
import { Dashboard } from './pages/Dashboard'
import { Rooms } from './pages/Rooms'
import { Devices } from './pages/Devices'
import { ActivityPage } from './pages/Activity'
import { Placeholder } from './pages/Placeholder'
import { Assistant } from './pages/Assistant'

export default function App() { const [page,setPage]=useState<Page>('dashboard'); const [status,setStatus]=useState<SystemStatus>(); const [aiStatus,setAiStatus]=useState<AIStatus>(); const [rooms,setRooms]=useState<Room[]>([]); const [devices,setDevices]=useState<Device[]>([]); const [events,setEvents]=useState<Event[]>([]); const [error,setError]=useState(''); const refreshAIStatus=useCallback(async()=>{try{setAiStatus(await api.aiStatus())}catch{setAiStatus(undefined)}},[]); useEffect(()=>{Promise.all([api.status(),api.rooms(),api.devices(),api.events(),api.aiStatus()]).then(([s,r,d,e,ai])=>{setStatus(s);setRooms(r);setDevices(d);setEvents(e);setAiStatus(ai)}).catch(()=>setError('Unable to reach the AI College backend. Start it on port 8000 and refresh.'))},[]); let content=status ? page==='dashboard'?<Dashboard status={status} rooms={rooms} events={events}/>:page==='rooms'?<Rooms rooms={rooms}/>:page==='devices'?<Devices devices={devices} rooms={rooms}/>:page==='activity'?<ActivityPage events={events} rooms={rooms}/>:page==='assistant'?<Assistant aiStatus={aiStatus} refreshStatus={refreshAIStatus}/>:<Placeholder type="settings"/> : <Loading/>; return <div className="app-shell"><Sidebar page={page} setPage={setPage} aiStatus={aiStatus?.status}/><main>{error?<div className="error">{error}</div>:content}</main></div> }
