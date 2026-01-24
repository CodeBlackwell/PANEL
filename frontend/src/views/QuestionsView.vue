<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { useSSE } from '../composables/useSSE'
import { api } from '../services/api'
import AgentMessage from '../components/AgentMessage.vue'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()
const { connect, disconnect, isConnected } = useSSE()

const messagesContainer = ref<HTMLElement | null>(null)
const currentAnswers = ref<string[]>([])
const currentQuestions = ref<string[]>([])
const isWaitingForAnswer = ref(false)
const isSubmitting = ref(false)
const clarificationComplete = ref(false)

const sessionId = computed(() => route.params.sessionId as string)

onMounted(async () => {
  if (sessionId.value !== store.sessionId) {
    await store.loadSession(sessionId.value)
  }
  startClarification()
})

function startClarification() {
  const url = api.getClarifyStreamUrl(sessionId.value)

  connect(url, {
    questions: (data) => {
      currentQuestions.value = data.questions || []
      currentAnswers.value = new Array(currentQuestions.value.length).fill('')
      isWaitingForAnswer.value = true
      store.setClarificationRound(data.round_number)

      currentQuestions.value.forEach((q: string) => {
        store.addClarificationMessage({
          type: 'question',
          content: q,
          roundNumber: data.round_number,
        })
      })
      scrollToBottom()
    },
    complete: () => {
      clarificationComplete.value = true
      store.setPhase('clarifying')
      disconnect()
    },
    error: (data) => {
      store.setError(data.error)
      disconnect()
    },
  })
}

async function submitAnswers() {
  if (currentAnswers.value.some(a => !a.trim())) return

  isSubmitting.value = true
  isWaitingForAnswer.value = false

  try {
    await store.submitAnswers(currentAnswers.value)
    currentQuestions.value = []
    currentAnswers.value = []
    scrollToBottom()

    // Continue listening for more questions or completion
    if (!clarificationComplete.value && !isConnected.value) {
      startClarification()
    }
  } catch (e) {
    console.error('Failed to submit answers:', e)
    isWaitingForAnswer.value = true
  } finally {
    isSubmitting.value = false
  }
}

function proceedToDebate() {
  router.push({ name: 'debate', params: { sessionId: sessionId.value } })
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
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-dark-100 mb-2">Clarification Phase</h2>
      <p class="text-dark-400">
        Answer the questions to help us understand your project better.
        <span class="text-primary-400">Round {{ store.clarificationRound }}</span>
      </p>
    </div>

    <!-- Messages -->
    <div
      ref="messagesContainer"
      class="card p-6 mb-6 max-h-[500px] overflow-y-auto space-y-4"
    >
      <AgentMessage
        v-for="(msg, index) in store.clarificationMessages"
        :key="index"
        :agent-name="msg.type === 'question' ? 'Clarifier' : 'You'"
        :agent-type="msg.type === 'question' ? 'clarifier' : 'user'"
        :content="msg.content"
        :message-type="msg.type"
      />

      <!-- Loading indicator -->
      <div v-if="isConnected && !isWaitingForAnswer && !clarificationComplete" class="flex items-center gap-3 text-dark-400">
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0ms"/>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 150ms"/>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 300ms"/>
        </div>
        <span>Generating questions...</span>
      </div>
    </div>

    <!-- Answer Input -->
    <div v-if="isWaitingForAnswer && currentQuestions.length > 0" class="card p-6 mb-6 space-y-4">
      <div
        v-for="(question, index) in currentQuestions"
        :key="index"
        class="space-y-2"
      >
        <label class="label">Q{{ index + 1 }}: {{ question }}</label>
        <textarea
          v-model="currentAnswers[index]"
          class="textarea"
          placeholder="Type your answer here..."
          rows="3"
        />
      </div>

      <button
        @click="submitAnswers"
        class="btn-primary w-full"
        :disabled="currentAnswers.some(a => !a.trim()) || isSubmitting"
        :class="{ 'opacity-50 cursor-not-allowed': currentAnswers.some(a => !a.trim()) || isSubmitting }"
      >
        <span v-if="isSubmitting" class="flex items-center justify-center gap-2">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          Submitting...
        </span>
        <span v-else>Submit Answers</span>
      </button>
    </div>

    <!-- Complete -->
    <div v-if="clarificationComplete" class="card p-6 text-center">
      <div class="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-dark-100 mb-2">Clarification Complete</h3>
      <p class="text-dark-400 mb-6">We have gathered enough information. Ready to start the expert debate.</p>
      <button @click="proceedToDebate" class="btn-primary">
        Start Expert Debate
      </button>
    </div>
  </div>
</template>
