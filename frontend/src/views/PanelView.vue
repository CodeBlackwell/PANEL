<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useSessionStore } from '../stores/session'
import { useAuthStore } from '../stores/auth'
import { useSSE } from '../composables/useSSE'
import { api, type ClarificationAnswer } from '../services/api'
import AgentMessage from '../components/AgentMessage.vue'
import DebateTimeline from '../components/DebateTimeline.vue'
import ScoreBar from '../components/ScoreBar.vue'

// ---------- stores ----------
const store = useSessionStore()
const authStore = useAuthStore()

// ---------- sidebar state ----------
const ideaText = ref('')
const selectedAgents = ref<string[]>([])
const debateRounds = ref(5)
const sidebarCollapsed = ref(false)

// ---------- clarification state ----------
interface ClarificationOption { id: string; text: string }
interface ClarificationQuestion { question: string; context?: string; options: ClarificationOption[] }
interface AnswerSelection { selectedOption: string | null; customAnswer: string }

const currentQuestions = ref<ClarificationQuestion[]>([])
const currentAnswers = ref<AnswerSelection[]>([])
const isWaitingForAnswer = ref(false)
const isSubmitting = ref(false)
const clarificationComplete = ref(false)

// ---------- debate state ----------
const debateComplete = ref(false)
const currentDebateRound = ref(0)
const totalDebateRounds = ref(5)

// ---------- judge state ----------
const judgeComplete = ref(false)
const currentJudge = ref<string | null>(null)

// ---------- UI state ----------
const boardRef = ref<HTMLElement | null>(null)
const isStarting = ref(false)

// ---------- SSE instances ----------
const clarifySSE = useSSE()
const debateSSE = useSSE()
const judgeSSE = useSSE()

// ---------- computed ----------
const isIdle = computed(() => !store.sessionId)
const canStart = computed(() =>
  ideaText.value.trim().length >= 10 &&
  selectedAgents.value.length >= 2 &&
  selectedAgents.value.length <= 6
)

const showClarification = computed(() =>
  ['configured', 'clarifying'].includes(store.phase) || store.clarificationMessages.length > 0
)
const showDebate = computed(() =>
  ['debating', 'drafting', 'judging', 'completed'].includes(store.phase) || store.debateMessages.length > 0
)
const showJudge = computed(() =>
  ['judging', 'completed'].includes(store.phase) || store.judgeScores.length > 0
)
const showResults = computed(() => store.phase === 'completed')

const allQuestionsAnswered = computed(() =>
  currentAnswers.value.every(a => {
    if (!a.selectedOption) return false
    if (a.selectedOption === 'custom') return a.customAnswer.trim().length > 0
    return true
  })
)

const averageScore = computed(() => {
  if (store.judgeScores.length === 0) return '0.0'
  const sum = store.judgeScores.reduce((acc, j) => acc + j.overallScore, 0)
  return (sum / store.judgeScores.length).toFixed(1)
})

// progress bar
const phaseIndex = computed(() => {
  const map: Record<string, number> = {
    created: -1, idea_submitted: -1, configured: 0,
    clarifying: 0, debating: 1, drafting: 2, judging: 2,
    completed: 3, error: -1,
  }
  return map[store.phase] ?? -1
})

// ---------- agent helpers ----------
function toggleAgent(id: string) {
  const idx = selectedAgents.value.indexOf(id)
  if (idx >= 0) {
    selectedAgents.value.splice(idx, 1)
  } else if (selectedAgents.value.length < 6) {
    selectedAgents.value.push(id)
  }
}

// judge color mapping
function judgeColor(type: string): 'yellow' | 'dusty' | 'green' {
  if (type === 'business') return 'yellow'
  if (type === 'technical') return 'dusty'
  return 'green'
}

function judgeLabel(type: string): string {
  const labels: Record<string, string> = {
    business: 'Business', technical: 'Technical', feasibility: 'Feasibility'
  }
  return labels[type] || type
}

// ---------- core orchestration ----------
async function handleStart() {
  isStarting.value = true
  try {
    await store.createSession()
    await store.submitIdea(ideaText.value)
    await store.configureSession({
      selected_agents: selectedAgents.value,
      debate_rounds: debateRounds.value,
    })
    totalDebateRounds.value = debateRounds.value
    sidebarCollapsed.value = true
    startClarification()
  } catch (e) {
    console.error('Failed to start:', e)
  } finally {
    isStarting.value = false
  }
}

function startClarification() {
  const url = api.getClarifyStreamUrl(store.sessionId!)
  clarifySSE.connect(url, {
    questions: (data: any) => {
      currentQuestions.value = (data.questions || []).map((q: any) => ({
        question: q.question || '',
        context: q.context || undefined,
        options: (q.options || []).map((opt: any) => ({ id: opt.id || '', text: opt.text || '' })),
      }))
      currentAnswers.value = currentQuestions.value.map(() => ({ selectedOption: null, customAnswer: '' }))
      isWaitingForAnswer.value = true
      store.setClarificationRound(data.round_number)

      currentQuestions.value.forEach((q: ClarificationQuestion) => {
        let content = q.question
        if (q.context) content += `\n_${q.context}_`
        if (q.options.length > 0) content += '\n' + q.options.map(opt => `${opt.id}) ${opt.text}`).join('\n')
        store.addClarificationMessage({ type: 'question', content, roundNumber: data.round_number })
      })
      scrollBoard()
      clarifySSE.disconnect()
    },
    complete: () => {
      clarificationComplete.value = true
      clarifySSE.disconnect()
      startDebate()
    },
    error: (data: any) => {
      store.setError(data.error)
      clarifySSE.disconnect()
    },
  })
}

async function submitAnswers() {
  if (!allQuestionsAnswered.value) return
  isSubmitting.value = true
  isWaitingForAnswer.value = false

  try {
    const structuredAnswers: ClarificationAnswer[] = currentQuestions.value.map((q, i) => {
      const answer = currentAnswers.value[i]
      const isCustom = answer.selectedOption === 'custom'
      let selectedOptionText: string | null = null
      if (!isCustom && answer.selectedOption) {
        const opt = q.options.find(o => o.id === answer.selectedOption)
        selectedOptionText = opt?.text || null
      }
      return {
        question: q.question,
        selected_option: isCustom ? null : answer.selectedOption,
        selected_option_text: selectedOptionText,
        custom_answer: isCustom ? answer.customAnswer : null,
      }
    })

    await store.submitAnswers(structuredAnswers)
    currentQuestions.value = []
    currentAnswers.value = []
    scrollBoard()

    if (!clarificationComplete.value) {
      startClarification()
    }
  } catch (e) {
    console.error('Failed to submit answers:', e)
    isWaitingForAnswer.value = true
  } finally {
    isSubmitting.value = false
  }
}

function skipToDebate() {
  clarifySSE.disconnect()
  clarificationComplete.value = true
  startDebate()
}

function startDebate() {
  const url = api.getDebateStreamUrl(store.sessionId!)
  debateSSE.connect(url, {
    message: (data: any) => {
      store.addDebateMessage({
        agentName: data.agent_name,
        agentType: data.agent_type,
        content: data.content,
        messageType: data.message_type,
        roundNumber: data.round_number,
        timestamp: data.timestamp,
      })
      currentDebateRound.value = data.round_number
      store.setDebateRound(data.round_number)
      scrollBoard()
    },
    round_start: (data: any) => {
      currentDebateRound.value = data.round_number
      store.setDebateRound(data.round_number)
    },
    drafting_start: () => {
      store.setPhase('drafting')
      scrollBoard()
    },
    complete: () => {
      debateComplete.value = true
      debateSSE.disconnect()
      startJudging()
    },
    error: (data: any) => {
      store.setError(data.error)
      debateSSE.disconnect()
    },
  })
}

function startJudging() {
  const url = api.getJudgeStreamUrl(store.sessionId!)
  judgeSSE.connect(url, {
    judge_start: (data: any) => {
      currentJudge.value = data.judge_type
      scrollBoard()
    },
    score: (data: any) => {
      store.addJudgeScore({
        judgeName: data.judge_name,
        judgeType: data.judge_type,
        scores: data.scores || {},
        reasoning: data.reasoning || '',
        overallScore: data.overall_score || 0,
      })
      currentJudge.value = null
      scrollBoard()
    },
    verdict: (data: any) => {
      store.setOverallVerdict(data.verdict)
      scrollBoard()
    },
    complete: () => {
      judgeComplete.value = true
      store.setPhase('completed')
      judgeSSE.disconnect()
      scrollBoard()
    },
    error: (data: any) => {
      store.setError(data.error)
      judgeSSE.disconnect()
    },
  })
}

function downloadZip() {
  window.location.href = api.getDownloadUrl(store.sessionId!)
}

function resetSession() {
  store.reset()
  sidebarCollapsed.value = false
  ideaText.value = ''
  selectedAgents.value = store.availableAgents.filter(a => a.default_selected).map(a => a.id)
  debateRounds.value = 5
  clarificationComplete.value = false
  debateComplete.value = false
  judgeComplete.value = false
  currentQuestions.value = []
  currentAnswers.value = []
  isWaitingForAnswer.value = false
  currentJudge.value = null
  currentDebateRound.value = 0
}

function scrollBoard() {
  nextTick(() => {
    if (boardRef.value) {
      boardRef.value.scrollTo({ top: boardRef.value.scrollHeight, behavior: 'smooth' })
    }
  })
}

// ---------- init ----------
onMounted(async () => {
  await store.fetchAgents()
  selectedAgents.value = store.availableAgents.filter(a => a.default_selected).map(a => a.id)
})
</script>

<template>
  <div class="flex h-full">

    <!-- ================================== -->
    <!-- LEFT SIDEBAR: "The Brief"          -->
    <!-- ================================== -->
    <aside
      class="flex-shrink-0 border-r border-slate-border bg-slate-light flex flex-col transition-all duration-300 overflow-hidden"
      :class="sidebarCollapsed ? 'w-14' : 'w-80'"
    >
      <!-- Collapsed state -->
      <div v-if="sidebarCollapsed" class="flex flex-col items-center py-4 h-full gap-4">
        <button @click="sidebarCollapsed = false" class="text-chalk-faint hover:text-chalk transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        <span class="text-chalk-faint font-heading text-xs tracking-[0.2em] select-none" style="writing-mode: vertical-lr">
          PANEL
        </span>
      </div>

      <!-- Expanded state -->
      <div v-else class="flex flex-col h-full">
        <!-- Header -->
        <div class="px-5 py-4 border-b border-slate-border flex items-center justify-between flex-shrink-0">
          <span class="font-heading text-lg font-bold text-chalk tracking-wide">PANEL</span>
          <button
            v-if="store.sessionId"
            @click="sidebarCollapsed = true"
            class="text-chalk-faint hover:text-chalk transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        <!-- Scrollable content -->
        <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">
          <!-- Running: show summary -->
          <div v-if="store.sessionId" class="space-y-3">
            <div class="text-[10px] uppercase tracking-[0.15em] text-chalk-faint font-medium">Your Brief</div>
            <p class="text-sm text-chalk-dim leading-relaxed line-clamp-6">{{ ideaText }}</p>
            <div class="text-xs text-chalk-faint">
              {{ selectedAgents.length }} agents &middot; {{ debateRounds }} rounds
            </div>
            <button @click="resetSession" class="btn-ghost text-xs w-full mt-2">
              New Session
            </button>
          </div>

          <!-- Idle: show form -->
          <div v-else class="space-y-5">
            <div>
              <label for="idea" class="label">Describe your project</label>
              <textarea
                id="idea"
                v-model="ideaText"
                class="textarea h-40 text-sm"
                placeholder="What are you building? What problem does it solve? Who are the target users?"
              />
              <p class="text-[10px] text-chalk-faint mt-1">Minimum 10 characters</p>
            </div>

            <!-- Agent checkboxes -->
            <div>
              <label class="label">Expert Agents ({{ selectedAgents.length }}/6)</label>
              <div class="space-y-0.5 max-h-52 overflow-y-auto pr-1">
                <label
                  v-for="agent in store.availableAgents"
                  :key="agent.id"
                  class="flex items-center gap-2.5 px-2 py-1.5 rounded cursor-pointer hover:bg-slate/50 transition-colors text-sm group"
                  :class="{
                    'opacity-30 cursor-not-allowed': !selectedAgents.includes(agent.id) && selectedAgents.length >= 6
                  }"
                >
                  <input
                    type="checkbox"
                    :checked="selectedAgents.includes(agent.id)"
                    @change="toggleAgent(agent.id)"
                    :disabled="!selectedAgents.includes(agent.id) && selectedAgents.length >= 6"
                    class="w-3.5 h-3.5 rounded"
                  />
                  <span class="text-chalk group-hover:text-chalk">{{ agent.name }}</span>
                  <span v-if="agent.default_selected" class="text-[9px] text-dusty ml-auto">default</span>
                </label>
              </div>
            </div>

            <!-- Rounds slider -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="label mb-0">Debate Rounds</label>
                <span class="text-sm font-heading font-bold text-yellow">{{ debateRounds }}</span>
              </div>
              <input type="range" v-model.number="debateRounds" min="3" max="10" class="w-full mt-1" />
              <div class="flex justify-between text-[9px] text-chalk-faint mt-0.5">
                <span>3 Quick</span>
                <span>10 Deep</span>
              </div>
            </div>

            <!-- Start button -->
            <button
              @click="handleStart"
              class="btn-primary w-full py-3 text-base font-heading font-semibold tracking-wide"
              :disabled="!canStart || isStarting"
              :class="{ 'opacity-50 cursor-not-allowed': !canStart || isStarting }"
            >
              {{ isStarting ? 'Starting...' : 'Begin' }}
            </button>
          </div>
        </div>

        <!-- GitHub sign-in footer -->
        <div class="px-5 py-3 border-t border-slate-border flex-shrink-0">
          <button
            v-if="!authStore.isAuthenticated"
            @click="authStore.loginWithGitHub()"
            class="flex items-center gap-2 text-xs text-chalk-faint hover:text-chalk transition-colors"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
            </svg>
            Sign in with GitHub
          </button>
          <div v-else class="flex items-center gap-2 text-xs text-chalk-faint">
            <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" class="w-5 h-5 rounded-full" />
            <span class="truncate">{{ authStore.user?.username }}</span>
            <button @click="authStore.logout()" class="ml-auto text-chalk-faint hover:text-chalk text-[10px]">
              Sign out
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- ================================== -->
    <!-- MAIN: Board + Bottom bar           -->
    <!-- ================================== -->
    <div class="flex-1 flex flex-col min-w-0">

      <!-- The Board -->
      <main ref="boardRef" class="flex-1 overflow-y-auto px-8 py-6">

        <!-- Empty state -->
        <div v-if="isIdle" class="flex items-center justify-center h-full">
          <div class="text-center max-w-md">
            <h1 class="font-heading text-4xl font-bold text-chalk mb-4 tracking-tight">
              The Board
            </h1>
            <p class="text-chalk-dim text-base leading-relaxed">
              Describe your project in the sidebar, select your expert agents, and let the debate begin.
            </p>
            <p class="text-chalk-faint text-sm mt-6 italic font-heading">
              PRD from Agent Negotiation &amp; Expert Logic
            </p>
          </div>
        </div>

        <!-- Active session feed -->
        <div v-else class="max-w-3xl mx-auto space-y-10 pb-8">

          <!-- ── CLARIFICATION ── -->
          <section v-if="showClarification" class="animate-chalk-fade">
            <div class="board-section-header">
              <div class="divider" />
              <h2>Clarification</h2>
              <div class="divider" />
            </div>

            <div class="space-y-3">
              <AgentMessage
                v-for="(msg, i) in store.clarificationMessages"
                :key="'c-' + i"
                :agent-name="msg.type === 'question' ? 'Clarifier' : 'You'"
                :agent-type="msg.type === 'question' ? 'clarifier' : 'user'"
                :content="msg.content"
                :message-type="msg.type"
              />
            </div>

            <!-- Inline answer forms -->
            <div v-if="isWaitingForAnswer && currentQuestions.length > 0" class="mt-6 space-y-4">
              <div v-for="(q, qIdx) in currentQuestions" :key="'q-' + qIdx" class="card p-4 space-y-3">
                <h3 class="font-heading text-base font-semibold text-chalk">{{ q.question }}</h3>
                <p v-if="q.context" class="text-xs text-chalk-faint italic">{{ q.context }}</p>

                <label
                  v-for="opt in q.options"
                  :key="opt.id"
                  class="flex items-center gap-2.5 p-2.5 rounded border cursor-pointer transition-colors text-sm"
                  :class="{
                    'border-dusty bg-dusty/10 text-chalk': currentAnswers[qIdx]?.selectedOption === opt.id,
                    'border-slate-border text-chalk-dim hover:border-dusty-dim': currentAnswers[qIdx]?.selectedOption !== opt.id,
                  }"
                >
                  <input
                    type="radio"
                    :name="'q-' + qIdx"
                    :value="opt.id"
                    v-model="currentAnswers[qIdx].selectedOption"
                    class="w-3.5 h-3.5 text-dusty bg-slate border-slate-border focus:ring-dusty"
                  />
                  <span><span class="font-medium text-dusty">{{ opt.id }}.</span> {{ opt.text }}</span>
                </label>

                <!-- Custom answer -->
                <label
                  class="flex items-center gap-2.5 p-2.5 rounded border cursor-pointer transition-colors text-sm"
                  :class="{
                    'border-dusty bg-dusty/10': currentAnswers[qIdx]?.selectedOption === 'custom',
                    'border-slate-border hover:border-dusty-dim': currentAnswers[qIdx]?.selectedOption !== 'custom',
                  }"
                >
                  <input type="radio" :name="'q-' + qIdx" value="custom" v-model="currentAnswers[qIdx].selectedOption" class="w-3.5 h-3.5 text-dusty bg-slate border-slate-border" />
                  <span class="text-chalk-dim">Write your own</span>
                </label>
                <textarea
                  v-if="currentAnswers[qIdx]?.selectedOption === 'custom'"
                  v-model="currentAnswers[qIdx].customAnswer"
                  class="textarea text-sm ml-6"
                  rows="2"
                  placeholder="Your answer..."
                />
              </div>

              <div class="flex items-center gap-3">
                <button
                  @click="submitAnswers"
                  class="btn-primary"
                  :disabled="!allQuestionsAnswered || isSubmitting"
                  :class="{ 'opacity-50 cursor-not-allowed': !allQuestionsAnswered || isSubmitting }"
                >
                  {{ isSubmitting ? 'Submitting...' : 'Submit Answers' }}
                </button>
                <button
                  v-if="store.clarificationRound >= 1"
                  @click="skipToDebate"
                  class="text-xs text-chalk-faint hover:text-dusty underline underline-offset-4 transition-colors"
                >
                  Skip to debate
                </button>
              </div>
            </div>

            <!-- Loading -->
            <div v-if="clarifySSE.isConnected.value && !isWaitingForAnswer && !clarificationComplete" class="flex items-center gap-2 mt-4 text-chalk-faint text-sm">
              <span class="inline-flex space-x-1">
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:0ms" />
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:150ms" />
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:300ms" />
              </span>
              Generating questions...
            </div>
          </section>

          <!-- ── DEBATE ── -->
          <section v-if="showDebate" class="animate-chalk-fade">
            <div class="board-section-header">
              <div class="divider" />
              <h2>Debate</h2>
              <div class="divider" />
            </div>

            <DebateTimeline :messages="store.debateMessages" />

            <div v-if="debateSSE.isConnected.value && !debateComplete" class="flex items-center gap-2 mt-4 text-chalk-faint text-sm">
              <span class="inline-flex space-x-1">
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:0ms" />
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:150ms" />
                <span class="w-1.5 h-1.5 bg-dusty rounded-full animate-bounce" style="animation-delay:300ms" />
              </span>
              Agents discussing... (Round {{ currentDebateRound }}/{{ totalDebateRounds }})
            </div>
          </section>

          <!-- ── DRAFTING ── -->
          <div v-if="store.phase === 'drafting'" class="text-center py-8 animate-chalk-fade">
            <p class="font-heading text-lg text-yellow italic">Synthesizing PRD...</p>
          </div>

          <!-- ── JUDGE ── -->
          <section v-if="showJudge" class="animate-chalk-fade">
            <div class="board-section-header">
              <div class="divider" />
              <h2>Judicial Review</h2>
              <div class="divider" />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                v-for="judge in store.judgeScores"
                :key="judge.judgeType"
                class="card p-4 space-y-3"
              >
                <div class="flex items-center gap-2 mb-2">
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center text-slate font-bold text-xs"
                    :class="{
                      'bg-yellow': judge.judgeType === 'business',
                      'bg-dusty': judge.judgeType === 'technical',
                      'bg-agent-devops': judge.judgeType === 'feasibility',
                    }"
                  >
                    {{ judgeLabel(judge.judgeType).slice(0, 2).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-sm font-heading font-semibold text-chalk">{{ judgeLabel(judge.judgeType) }}</div>
                  </div>
                </div>

                <div class="space-y-2">
                  <ScoreBar
                    v-for="(score, key) in judge.scores"
                    :key="String(key)"
                    :label="String(key)"
                    :score="Number(score)"
                    :color="judgeColor(judge.judgeType)"
                  />
                </div>

                <div class="pt-2 border-t border-slate-border flex justify-between items-center">
                  <span class="text-xs text-chalk-faint">Overall</span>
                  <span class="text-xl font-heading font-bold" :class="{
                    'text-yellow': judge.judgeType === 'business',
                    'text-dusty': judge.judgeType === 'technical',
                    'text-agent-devops': judge.judgeType === 'feasibility',
                  }">{{ judge.overallScore.toFixed(1) }}</span>
                </div>
              </div>
            </div>

            <!-- Judge loading -->
            <div v-if="judgeSSE.isConnected.value && !judgeComplete" class="flex items-center justify-center gap-2 mt-4 text-chalk-faint text-sm">
              <span class="inline-flex space-x-1">
                <span class="w-1.5 h-1.5 bg-yellow rounded-full animate-bounce" style="animation-delay:0ms" />
                <span class="w-1.5 h-1.5 bg-yellow rounded-full animate-bounce" style="animation-delay:150ms" />
                <span class="w-1.5 h-1.5 bg-yellow rounded-full animate-bounce" style="animation-delay:300ms" />
              </span>
              {{ currentJudge ? `${judgeLabel(currentJudge)} judge evaluating...` : 'Evaluating...' }}
            </div>
          </section>

          <!-- ── VERDICT + DOWNLOAD ── -->
          <section v-if="showResults" class="animate-chalk-fade">
            <div class="board-section-header">
              <div class="divider" />
              <h2>Verdict</h2>
              <div class="divider" />
            </div>

            <div class="card p-8 text-center">
              <div class="font-heading text-5xl font-bold text-yellow mb-2">{{ averageScore }}</div>
              <p class="text-chalk-faint text-sm mb-4">Average Score</p>
              <p v-if="store.overallVerdict" class="text-chalk-dim text-sm mb-8 max-w-lg mx-auto leading-relaxed">
                {{ store.overallVerdict }}
              </p>
              <div class="flex items-center justify-center gap-3">
                <button @click="downloadZip" class="btn-primary px-8 py-3 font-heading font-semibold">
                  Download PRD
                </button>
                <button @click="resetSession" class="btn-secondary px-6 py-3">
                  New Session
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>

      <!-- Bottom progress bar -->
      <div v-if="!isIdle" class="h-9 border-t border-slate-border bg-slate-light flex items-center px-6 flex-shrink-0">
        <div class="flex items-center gap-2 w-full">
          <template v-for="(label, idx) in ['Clarify', 'Debate', 'Judge', 'Done']" :key="label">
            <div
              class="w-2 h-2 rounded-full transition-all duration-500"
              :class="{
                'bg-dusty scale-125': idx === phaseIndex,
                'bg-yellow': idx < phaseIndex,
                'bg-slate-border': idx > phaseIndex,
              }"
            />
            <span
              v-if="idx === phaseIndex"
              class="text-[10px] text-chalk-dim font-medium tracking-wide"
            >
              {{ label }}
            </span>
            <div
              v-if="idx < 3"
              class="flex-1 h-px transition-colors duration-500"
              :class="idx < phaseIndex ? 'bg-yellow-dim' : 'bg-slate-border'"
            />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
