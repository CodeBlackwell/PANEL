<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { useSSE } from '../composables/useSSE'
import { api } from '../services/api'
import DebateTimeline from '../components/DebateTimeline.vue'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()
const { connect, disconnect, isConnected } = useSSE()

const messagesContainer = ref<HTMLElement | null>(null)
const debateComplete = ref(false)
const currentRound = ref(0)
const totalRounds = ref(5)

const sessionId = computed(() => route.params.sessionId as string)

onMounted(async () => {
  if (sessionId.value !== store.sessionId) {
    await store.loadSession(sessionId.value)
  }
  totalRounds.value = store.config?.debate_rounds || 5
  startDebate()
})

function startDebate() {
  const url = api.getDebateStreamUrl(sessionId.value)

  connect(url, {
    message: (data) => {
      store.addDebateMessage({
        agentName: data.agent_name,
        agentType: data.agent_type,
        content: data.content,
        messageType: data.message_type,
        roundNumber: data.round_number,
        timestamp: data.timestamp,
      })
      currentRound.value = data.round_number
      store.setDebateRound(data.round_number)
      scrollToBottom()
    },
    round_start: (data) => {
      currentRound.value = data.round_number
      store.setDebateRound(data.round_number)
    },
    complete: () => {
      debateComplete.value = true
      store.setPhase('debating')
      disconnect()
    },
    error: (data) => {
      store.setError(data.error)
      disconnect()
    },
  })
}

function proceedToJudge() {
  router.push({ name: 'judge', params: { sessionId: sessionId.value } })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-dark-100 mb-2">Expert Debate</h2>
      <p class="text-dark-400">
        Watch as expert agents discuss and debate your project.
      </p>
    </div>

    <!-- Progress -->
    <div class="card p-4 mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-dark-300">Round Progress</span>
        <span class="text-primary-400 font-medium">{{ currentRound }} / {{ totalRounds }}</span>
      </div>
      <div class="w-full bg-dark-700 rounded-full h-2">
        <div
          class="bg-primary-500 h-2 rounded-full transition-all duration-500"
          :style="{ width: `${(currentRound / totalRounds) * 100}%` }"
        />
      </div>
    </div>

    <!-- Debate Timeline -->
    <div
      ref="messagesContainer"
      class="card p-6 mb-6 max-h-[600px] overflow-y-auto"
    >
      <DebateTimeline :messages="store.debateMessages" />

      <!-- Loading indicator -->
      <div v-if="isConnected && !debateComplete" class="flex items-center gap-3 text-dark-400 mt-4">
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0ms"/>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 150ms"/>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 300ms"/>
        </div>
        <span>Agents discussing...</span>
      </div>
    </div>

    <!-- Complete -->
    <div v-if="debateComplete" class="card p-6 text-center">
      <div class="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-dark-100 mb-2">Debate Complete</h3>
      <p class="text-dark-400 mb-6">The experts have concluded their discussion. Ready for judicial review.</p>
      <button @click="proceedToJudge" class="btn-primary">
        Start Judicial Review
      </button>
    </div>
  </div>
</template>
