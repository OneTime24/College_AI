export interface AIStatus { provider: string; model?: string; runtime: string; model_available: boolean; status: string }
export interface AIChatResponse { response: string; model: string; provider: string }
