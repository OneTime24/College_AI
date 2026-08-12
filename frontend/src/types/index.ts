export interface Device { id: number; name: string; device_type: string; room_id: number; status: string; is_online: boolean; metadata?: Record<string, unknown>; created_at: string; updated_at: string }
export interface Room { id: number; name: string; description?: string; building: string; floor: string; room_number: string; room_type: string; temperature?: number; humidity?: number; occupancy: number; active_mode: string; devices: Device[]; created_at: string; updated_at: string }
export interface Event { id: number; event_type: string; location: string; description: string; timestamp: string; metadata?: Record<string, unknown> }
export interface SystemStatus { backend: string; database: string; llm: string; rooms: number; devices: number; recent_events: number }
export interface AIStatus { provider: string; model?: string; runtime: string; model_available: boolean; status: string; supports_image_input?: boolean; supports_voice_input?: boolean; supports_voice_output?: boolean; voice_input_engine?: string; voice_output_engine?: string }
export interface AIChatResponse { response: string; model: string; provider: string; transcript?: string | null }
