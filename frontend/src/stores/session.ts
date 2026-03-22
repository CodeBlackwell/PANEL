import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, type AgentInfo, type SessionConfig, type ClarificationAnswer, type RepoContext } from '../services/api'

export type SessionPhase =
  | 'created'
  | 'idea_submitted'
  | 'configured'
  | 'clarifying'
  | 'debating'
  | 'drafting'
  | 'judging'
  | 'completed'
  | 'error'

export interface ClarificationMessage {
  type: 'question' | 'answer'
  content: string
  roundNumber: number
}

export interface DebateMessage {
  agentName: string
  agentType: string
  content: string
  messageType: 'proposal' | 'critique' | 'agreement' | 'summary'
  roundNumber: number
  timestamp: string
}

export interface JudgeScore {
  judgeName: string
  judgeType: 'business' | 'technical' | 'feasibility'
  scores: Record<string, number>
  reasoning: string
  overallScore: number
}

export const useSessionStore = defineStore('session', () => {
  // State
  const sessionId = ref<string | null>(null)
  const phase = ref<SessionPhase>('created')
  const idea = ref<string>('')
  const config = ref<SessionConfig | null>(null)
  const availableAgents = ref<AgentInfo[]>([])
  const clarificationMessages = ref<ClarificationMessage[]>([])
  const debateMessages = ref<DebateMessage[]>([])
  const judgeScores = ref<JudgeScore[]>([])
  const overallVerdict = ref<string>('')
  const clarificationRound = ref(0)
  const debateRound = ref(0)
  const error = ref<string | null>(null)
  const isLoading = ref(false)
  const repoContext = ref<RepoContext | null>(null)
  const userId = ref<string | null>(null)

  // Computed
  const isSessionActive = computed(() => sessionId.value !== null)
  const canStartClarification = computed(() => phase.value === 'configured')
  const canStartDebate = computed(() => ['clarifying', 'debating'].includes(phase.value))
  const canStartJudge = computed(() => ['debating', 'drafting', 'judging'].includes(phase.value))
  const canDownload = computed(() => phase.value === 'completed')
  const hasRepoContext = computed(() => repoContext.value !== null)

  // Actions
  async function createSession(): Promise<string> {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.createSession()
      sessionId.value = response.session_id
      phase.value = response.phase as SessionPhase
      return response.session_id
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create session'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function submitIdea(projectIdea: string): Promise<void> {
    if (!sessionId.value) throw new Error('No active session')
    isLoading.value = true
    error.value = null
    try {
      const response = await api.submitIdea(sessionId.value, projectIdea)
      idea.value = projectIdea
      phase.value = response.phase as SessionPhase
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit idea'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAgents(): Promise<void> {
    try {
      availableAgents.value = await api.getAgents()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch agents'
      throw e
    }
  }

  async function configureSession(sessionConfig: SessionConfig): Promise<void> {
    if (!sessionId.value) throw new Error('No active session')
    isLoading.value = true
    error.value = null
    try {
      const response = await api.configureSession(sessionId.value, sessionConfig)
      config.value = sessionConfig
      phase.value = response.phase as SessionPhase
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to configure session'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function submitAnswers(answers: ClarificationAnswer[]): Promise<void> {
    if (!sessionId.value) throw new Error('No active session')
    isLoading.value = true
    error.value = null
    try {
      await api.submitAnswers(sessionId.value, answers)
      answers.forEach((answer) => {
        // Display the answer in a readable format
        const displayText = answer.custom_answer
          || (answer.selected_option_text ? `[${answer.selected_option}] ${answer.selected_option_text}` : answer.selected_option || '')
        clarificationMessages.value.push({
          type: 'answer',
          content: displayText,
          roundNumber: clarificationRound.value,
        })
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit answers'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function addClarificationMessage(msg: ClarificationMessage) {
    clarificationMessages.value.push(msg)
  }

  function addDebateMessage(msg: DebateMessage) {
    // Deduplicate: skip if same agent + same content in same round already exists
    const isDupe = debateMessages.value.some(
      (existing) =>
        existing.agentName === msg.agentName &&
        existing.roundNumber === msg.roundNumber &&
        existing.content === msg.content
    )
    if (!isDupe) {
      debateMessages.value.push(msg)
    }
  }

  function addJudgeScore(score: JudgeScore) {
    judgeScores.value.push(score)
  }

  function setPhase(newPhase: SessionPhase) {
    phase.value = newPhase
  }

  function setError(errorMessage: string) {
    error.value = errorMessage
    phase.value = 'error'
  }

  function setClarificationRound(round: number) {
    clarificationRound.value = round
  }

  function setDebateRound(round: number) {
    debateRound.value = round
  }

  function setOverallVerdict(verdict: string) {
    overallVerdict.value = verdict
  }

  function reset() {
    sessionId.value = null
    phase.value = 'created'
    idea.value = ''
    config.value = null
    clarificationMessages.value = []
    debateMessages.value = []
    judgeScores.value = []
    overallVerdict.value = ''
    clarificationRound.value = 0
    debateRound.value = 0
    error.value = null
    isLoading.value = false
    repoContext.value = null
    userId.value = null
  }

  async function loadSession(id: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const session = await api.getSession(id)
      sessionId.value = session.id
      phase.value = session.phase as SessionPhase
      clarificationRound.value = session.clarification_round
      debateRound.value = session.debate_round
      config.value = session.config
      repoContext.value = session.repo_context
      userId.value = session.user_id
      if (session.error_message) {
        error.value = session.error_message
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load session'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function setRepoContext(context: RepoContext) {
    repoContext.value = context
  }

  return {
    // State
    sessionId,
    phase,
    idea,
    config,
    availableAgents,
    clarificationMessages,
    debateMessages,
    judgeScores,
    overallVerdict,
    clarificationRound,
    debateRound,
    error,
    isLoading,
    repoContext,
    userId,
    // Computed
    isSessionActive,
    canStartClarification,
    canStartDebate,
    canStartJudge,
    canDownload,
    hasRepoContext,
    // Actions
    createSession,
    submitIdea,
    fetchAgents,
    configureSession,
    submitAnswers,
    addClarificationMessage,
    addDebateMessage,
    addJudgeScore,
    setPhase,
    setError,
    setClarificationRound,
    setDebateRound,
    setOverallVerdict,
    reset,
    loadSession,
    setRepoContext,
  }
})
