<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { useSSE } from '../composables/useSSE'
import { api } from '../services/api'
import ScoreBar from '../components/ScoreBar.vue'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()
const { connect, disconnect, isConnected } = useSSE()

const judgeComplete = ref(false)
const currentJudge = ref<string | null>(null)

const sessionId = computed(() => route.params.sessionId as string)

onMounted(async () => {
  if (sessionId.value !== store.sessionId) {
    await store.loadSession(sessionId.value)
  }
  startJudging()
})

function startJudging() {
  const url = api.getJudgeStreamUrl(sessionId.value)

  connect(url, {
    judge_start: (data) => {
      currentJudge.value = data.judge_type
    },
    score: (data) => {
      store.addJudgeScore({
        judgeName: data.judge_name,
        judgeType: data.judge_type,
        scores: data.scores,
        reasoning: data.reasoning,
        overallScore: data.overall_score,
      })
      currentJudge.value = null
    },
    verdict: (data) => {
      store.setOverallVerdict(data.verdict)
    },
    complete: () => {
      judgeComplete.value = true
      store.setPhase('completed')
      disconnect()
    },
    error: (data) => {
      store.setError(data.error)
      disconnect()
    },
  })
}

function proceedToResults() {
  router.push({ name: 'results', params: { sessionId: sessionId.value } })
}

const averageScore = computed(() => {
  if (store.judgeScores.length === 0) return 0
  const sum = store.judgeScores.reduce((acc, j) => acc + j.overallScore, 0)
  return (sum / store.judgeScores.length).toFixed(1)
})

const judgeTypeLabels: Record<string, string> = {
  business: 'Business Judge',
  technical: 'Technical Judge',
  feasibility: 'Feasibility Judge',
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-dark-100 mb-2">Judicial Review</h2>
      <p class="text-dark-400">Three expert judges evaluate your project plan.</p>
    </div>

    <!-- Judge Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Business Judge -->
      <div
        class="card p-6 transition-all duration-300"
        :class="{
          'ring-2 ring-amber-500': currentJudge === 'business',
          'opacity-50': currentJudge && currentJudge !== 'business' && !store.judgeScores.find(j => j.judgeType === 'business'),
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-12 h-12 bg-amber-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold">BJ</span>
          </div>
          <div>
            <h3 class="font-semibold text-dark-100">Business Judge</h3>
            <p class="text-sm text-dark-400">Market & Value</p>
          </div>
        </div>

        <div v-if="store.judgeScores.find(j => j.judgeType === 'business')" class="space-y-3">
          <div v-for="(score, criterion) in store.judgeScores.find(j => j.judgeType === 'business')?.scores" :key="criterion">
            <ScoreBar :label="criterion" :score="score" color="amber" />
          </div>
          <div class="pt-2 border-t border-dark-700">
            <div class="flex justify-between items-center">
              <span class="text-dark-300">Overall</span>
              <span class="text-2xl font-bold text-amber-400">
                {{ store.judgeScores.find(j => j.judgeType === 'business')?.overallScore.toFixed(1) }}
              </span>
            </div>
          </div>
        </div>

        <div v-else-if="currentJudge === 'business'" class="flex items-center gap-2 text-amber-400">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <span>Evaluating...</span>
        </div>

        <div v-else class="text-dark-500 text-sm">Waiting...</div>
      </div>

      <!-- Technical Judge -->
      <div
        class="card p-6 transition-all duration-300"
        :class="{
          'ring-2 ring-blue-500': currentJudge === 'technical',
          'opacity-50': currentJudge && currentJudge !== 'technical' && !store.judgeScores.find(j => j.judgeType === 'technical'),
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold">TJ</span>
          </div>
          <div>
            <h3 class="font-semibold text-dark-100">Technical Judge</h3>
            <p class="text-sm text-dark-400">Architecture & Security</p>
          </div>
        </div>

        <div v-if="store.judgeScores.find(j => j.judgeType === 'technical')" class="space-y-3">
          <div v-for="(score, criterion) in store.judgeScores.find(j => j.judgeType === 'technical')?.scores" :key="criterion">
            <ScoreBar :label="criterion" :score="score" color="blue" />
          </div>
          <div class="pt-2 border-t border-dark-700">
            <div class="flex justify-between items-center">
              <span class="text-dark-300">Overall</span>
              <span class="text-2xl font-bold text-blue-400">
                {{ store.judgeScores.find(j => j.judgeType === 'technical')?.overallScore.toFixed(1) }}
              </span>
            </div>
          </div>
        </div>

        <div v-else-if="currentJudge === 'technical'" class="flex items-center gap-2 text-blue-400">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <span>Evaluating...</span>
        </div>

        <div v-else class="text-dark-500 text-sm">Waiting...</div>
      </div>

      <!-- Feasibility Judge -->
      <div
        class="card p-6 transition-all duration-300"
        :class="{
          'ring-2 ring-green-500': currentJudge === 'feasibility',
          'opacity-50': currentJudge && currentJudge !== 'feasibility' && !store.judgeScores.find(j => j.judgeType === 'feasibility'),
        }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold">FJ</span>
          </div>
          <div>
            <h3 class="font-semibold text-dark-100">Feasibility Judge</h3>
            <p class="text-sm text-dark-400">Resources & Risks</p>
          </div>
        </div>

        <div v-if="store.judgeScores.find(j => j.judgeType === 'feasibility')" class="space-y-3">
          <div v-for="(score, criterion) in store.judgeScores.find(j => j.judgeType === 'feasibility')?.scores" :key="criterion">
            <ScoreBar :label="criterion" :score="score" color="green" />
          </div>
          <div class="pt-2 border-t border-dark-700">
            <div class="flex justify-between items-center">
              <span class="text-dark-300">Overall</span>
              <span class="text-2xl font-bold text-green-400">
                {{ store.judgeScores.find(j => j.judgeType === 'feasibility')?.overallScore.toFixed(1) }}
              </span>
            </div>
          </div>
        </div>

        <div v-else-if="currentJudge === 'feasibility'" class="flex items-center gap-2 text-green-400">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <span>Evaluating...</span>
        </div>

        <div v-else class="text-dark-500 text-sm">Waiting...</div>
      </div>
    </div>

    <!-- Overall Verdict -->
    <div v-if="judgeComplete" class="card p-8 text-center">
      <div class="mb-6">
        <div class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-400 mb-2">
          {{ averageScore }}
        </div>
        <p class="text-dark-400">Average Score</p>
      </div>

      <div v-if="store.overallVerdict" class="mb-6 p-4 bg-dark-700/50 rounded-lg">
        <h4 class="text-sm font-medium text-dark-300 mb-2">Verdict</h4>
        <p class="text-dark-100">{{ store.overallVerdict }}</p>
      </div>

      <button @click="proceedToResults" class="btn-primary">
        View Results & Download
      </button>
    </div>
  </div>
</template>
