<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { useSSE } from '../composables/useSSE'
import { api, type ClarificationAnswer } from '../services/api'
import AgentMessage from '../components/AgentMessage.vue'

interface ClarificationOption {
  id: string
  text: string
}

interface ClarificationQuestion {
  question: string
  context?: string
  options: ClarificationOption[]
}

interface AnswerSelection {
  selectedOption: string | null  // Option ID or 'custom'
  customAnswer: string
}

const router = useRouter()
const route = useRoute()
const store = useSessionStore()
const { connect, disconnect, isConnected } = useSSE()

const messagesContainer = ref<HTMLElement | null>(null)
const currentAnswers = ref<AnswerSelection[]>([])
const currentQuestions = ref<ClarificationQuestion[]>([])
const isWaitingForAnswer = ref(false)
const isSubmitting = ref(false)
const clarificationComplete = ref(false)

const sessionId = computed(() => route.params.sessionId as string)

// Check if all questions have valid answers
const allQuestionsAnswered = computed(() => {
  return currentAnswers.value.every((answer, index) => {
    if (!answer.selectedOption) return false
    if (answer.selectedOption === 'custom') {
      return answer.customAnswer.trim().length > 0
    }
    return true
  })
})

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
      // Parse questions with options
      currentQuestions.value = (data.questions || []).map((q: any) => ({
        question: q.question || '',
        context: q.context || undefined,
        options: (q.options || []).map((opt: any) => ({
          id: opt.id || '',
          text: opt.text || '',
        })),
      }))

      // Initialize answers array
      currentAnswers.value = currentQuestions.value.map(() => ({
        selectedOption: null,
        customAnswer: '',
      }))

      isWaitingForAnswer.value = true
      store.setClarificationRound(data.round_number)

      // Add questions to message history
      currentQuestions.value.forEach((q: ClarificationQuestion) => {
        let content = q.question
        if (q.context) {
          content += `\n_${q.context}_`
        }
        if (q.options.length > 0) {
          content += '\n' + q.options.map(opt => `${opt.id}) ${opt.text}`).join('\n')
        }
        store.addClarificationMessage({
          type: 'question',
          content,
          roundNumber: data.round_number,
        })
      })
      scrollToBottom()

      // Disconnect after receiving questions to prevent auto-reconnect
      // We'll reconnect after user submits answers
      disconnect()
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
  if (!allQuestionsAnswered.value) return

  isSubmitting.value = true
  isWaitingForAnswer.value = false

  try {
    // Build structured answers
    const structuredAnswers: ClarificationAnswer[] = currentQuestions.value.map((q, index) => {
      const answer = currentAnswers.value[index]
      const isCustom = answer.selectedOption === 'custom'

      // Find the selected option text if not custom
      let selectedOptionText: string | null = null
      if (!isCustom && answer.selectedOption) {
        const option = q.options.find(opt => opt.id === answer.selectedOption)
        selectedOptionText = option?.text || null
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

    <!-- Answer Input with Multiple Choice -->
    <div v-if="isWaitingForAnswer && currentQuestions.length > 0" class="space-y-6 mb-6">
      <div
        v-for="(question, qIndex) in currentQuestions"
        :key="qIndex"
        class="card p-6 space-y-4"
      >
        <!-- Question header -->
        <div>
          <h3 class="text-lg font-semibold text-dark-100">
            Q{{ qIndex + 1 }}: {{ question.question }}
          </h3>
          <p v-if="question.context" class="text-sm text-dark-400 mt-1 italic">
            {{ question.context }}
          </p>
        </div>

        <!-- Multiple choice options -->
        <div class="space-y-3">
          <label
            v-for="option in question.options"
            :key="option.id"
            class="flex items-start gap-3 p-3 rounded-lg border border-dark-600 hover:border-primary-500 cursor-pointer transition-colors"
            :class="{
              'border-primary-500 bg-primary-500/10': currentAnswers[qIndex]?.selectedOption === option.id
            }"
          >
            <input
              type="radio"
              :name="`question-${qIndex}`"
              :value="option.id"
              v-model="currentAnswers[qIndex].selectedOption"
              class="mt-1 w-4 h-4 text-primary-500 bg-dark-700 border-dark-500 focus:ring-primary-500 focus:ring-offset-dark-800"
            />
            <span class="flex-1">
              <span class="font-medium text-primary-400">{{ option.id }}.</span>
              <span class="text-dark-200 ml-1">{{ option.text }}</span>
            </span>
          </label>

          <!-- Type your own answer option -->
          <label
            class="flex items-start gap-3 p-3 rounded-lg border border-dark-600 hover:border-primary-500 cursor-pointer transition-colors"
            :class="{
              'border-primary-500 bg-primary-500/10': currentAnswers[qIndex]?.selectedOption === 'custom'
            }"
          >
            <input
              type="radio"
              :name="`question-${qIndex}`"
              value="custom"
              v-model="currentAnswers[qIndex].selectedOption"
              class="mt-1 w-4 h-4 text-primary-500 bg-dark-700 border-dark-500 focus:ring-primary-500 focus:ring-offset-dark-800"
            />
            <span class="flex-1">
              <span class="font-medium text-dark-200">Type your own answer</span>
            </span>
          </label>

          <!-- Custom answer textarea -->
          <div
            v-if="currentAnswers[qIndex]?.selectedOption === 'custom'"
            class="pl-7"
          >
            <textarea
              v-model="currentAnswers[qIndex].customAnswer"
              class="textarea w-full"
              placeholder="Type your answer here..."
              rows="3"
            />
          </div>
        </div>
      </div>

      <!-- Submit button -->
      <button
        @click="submitAnswers"
        class="btn-primary w-full"
        :disabled="!allQuestionsAnswered || isSubmitting"
        :class="{ 'opacity-50 cursor-not-allowed': !allQuestionsAnswered || isSubmitting }"
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

    <!-- Skip to Debate (shown after at least 1 round of answers submitted) -->
    <div v-if="!clarificationComplete && store.clarificationRound >= 1 && isWaitingForAnswer" class="text-center mb-6">
      <button
        @click="proceedToDebate"
        class="text-sm text-dark-400 hover:text-primary-400 underline underline-offset-4 transition-colors"
      >
        Skip remaining questions and start debate
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
