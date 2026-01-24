<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import AgentSelector from '../components/AgentSelector.vue'
import RoundsSlider from '../components/RoundsSlider.vue'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()

const selectedAgents = ref<string[]>([])
const debateRounds = ref(5)
const isSubmitting = ref(false)

const sessionId = computed(() => route.params.sessionId as string)

onMounted(async () => {
  if (sessionId.value !== store.sessionId) {
    await store.loadSession(sessionId.value)
  }
  await store.fetchAgents()

  // Pre-select default agents
  selectedAgents.value = store.availableAgents
    .filter(a => a.default_selected)
    .map(a => a.id)
})

async function handleContinue() {
  if (selectedAgents.value.length < 2 || selectedAgents.value.length > 6) return

  isSubmitting.value = true
  try {
    await store.configureSession({
      selected_agents: selectedAgents.value,
      debate_rounds: debateRounds.value,
    })
    router.push({ name: 'questions', params: { sessionId: sessionId.value } })
  } catch (e) {
    console.error('Failed to configure session:', e)
  } finally {
    isSubmitting.value = false
  }
}

const canContinue = computed(() => {
  return selectedAgents.value.length >= 2 && selectedAgents.value.length <= 6
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-dark-100 mb-2">Configure Your Debate</h2>
      <p class="text-dark-400">Select the expert agents and number of debate rounds.</p>
    </div>

    <!-- Agent Selection -->
    <div class="card p-6 mb-6">
      <h3 class="text-lg font-semibold text-dark-100 mb-4">
        Select Expert Agents
        <span class="text-sm font-normal text-dark-400 ml-2">
          ({{ selectedAgents.length }}/6 selected, minimum 2)
        </span>
      </h3>
      <AgentSelector
        v-model="selectedAgents"
        :agents="store.availableAgents"
        :min="2"
        :max="6"
      />
    </div>

    <!-- Debate Rounds -->
    <div class="card p-6 mb-8">
      <h3 class="text-lg font-semibold text-dark-100 mb-4">Debate Rounds</h3>
      <RoundsSlider v-model="debateRounds" :min="3" :max="10" />
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-4">
      <button
        @click="router.push('/')"
        class="btn-secondary"
      >
        Back
      </button>
      <button
        @click="handleContinue"
        class="btn-primary"
        :disabled="!canContinue || isSubmitting"
        :class="{ 'opacity-50 cursor-not-allowed': !canContinue || isSubmitting }"
      >
        <span v-if="isSubmitting" class="flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          Saving...
        </span>
        <span v-else>Continue to Clarification</span>
      </button>
    </div>
  </div>
</template>
