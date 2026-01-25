const API_BASE = '/api/v1'

export interface Session {
  id: string
  phase: string
  clarification_round: number
  debate_round: number
  config: SessionConfig | null
  created_at: string
  updated_at: string
  error_message: string | null
}

export interface SessionConfig {
  selected_agents: string[]
  debate_rounds: number
}

export interface AgentInfo {
  id: string
  name: string
  focus_area: string
  default_selected: boolean
}

export interface ClarificationOption {
  id: string  // "A", "B", "C", "D"
  text: string
}

export interface ClarificationQuestionData {
  question: string
  context?: string
  options: ClarificationOption[]
}

export interface ClarificationAnswer {
  question: string
  selected_option: string | null  // Option ID or null
  selected_option_text: string | null
  custom_answer: string | null
}

export interface CreateSessionResponse {
  session_id: string
  phase: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  async createSession(): Promise<CreateSessionResponse> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    return handleResponse(response)
  },

  async getSession(sessionId: string): Promise<Session> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
    return handleResponse(response)
  },

  async submitIdea(sessionId: string, idea: string): Promise<Session> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/idea`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea }),
    })
    return handleResponse(response)
  },

  async getAgents(): Promise<AgentInfo[]> {
    const response = await fetch(`${API_BASE}/sessions`)
    return handleResponse(response)
  },

  async configureSession(sessionId: string, config: SessionConfig): Promise<Session> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    })
    return handleResponse(response)
  },

  async submitAnswers(sessionId: string, answers: ClarificationAnswer[]): Promise<Session> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    })
    return handleResponse(response)
  },

  getClarifyStreamUrl(sessionId: string): string {
    return `${API_BASE}/sessions/${sessionId}/clarify/stream`
  },

  getDebateStreamUrl(sessionId: string): string {
    return `${API_BASE}/sessions/${sessionId}/debate/stream`
  },

  getJudgeStreamUrl(sessionId: string): string {
    return `${API_BASE}/sessions/${sessionId}/judge/stream`
  },

  getDownloadUrl(sessionId: string): string {
    return `${API_BASE}/sessions/${sessionId}/download`
  },
}
