<script setup lang="ts">
import { computed } from 'vue'
import type { SessionPhase } from '../stores/session'

interface Step {
  id: string
  name: string
  phases: SessionPhase[]
}

const props = defineProps<{
  currentPhase: SessionPhase
}>()

const steps: Step[] = [
  { id: 'idea', name: 'Idea', phases: ['created', 'idea_submitted'] },
  { id: 'config', name: 'Configure', phases: ['configured'] },
  { id: 'clarify', name: 'Clarify', phases: ['clarifying'] },
  { id: 'debate', name: 'Debate', phases: ['debating'] },
  { id: 'judge', name: 'Judge', phases: ['drafting', 'judging'] },
  { id: 'results', name: 'Results', phases: ['completed'] },
]

const currentStepIndex = computed(() => {
  return steps.findIndex(step => step.phases.includes(props.currentPhase))
})

function getStepStatus(index: number): 'completed' | 'current' | 'upcoming' {
  if (index < currentStepIndex.value) return 'completed'
  if (index === currentStepIndex.value) return 'current'
  return 'upcoming'
}
</script>

<template>
  <nav aria-label="Progress">
    <ol class="flex items-center justify-between">
      <li
        v-for="(step, index) in steps"
        :key="step.id"
        class="flex items-center"
        :class="{ 'flex-1': index < steps.length - 1 }"
      >
        <div class="flex items-center">
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-all"
            :class="{
              'bg-primary-600 text-white': getStepStatus(index) === 'completed',
              'bg-primary-500 text-white ring-2 ring-primary-400 ring-offset-2 ring-offset-dark-900': getStepStatus(index) === 'current',
              'bg-dark-700 text-dark-400': getStepStatus(index) === 'upcoming',
            }"
          >
            <svg
              v-if="getStepStatus(index) === 'completed'"
              class="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span
            class="ml-2 text-sm font-medium hidden sm:block"
            :class="{
              'text-primary-400': getStepStatus(index) === 'current',
              'text-dark-300': getStepStatus(index) === 'completed',
              'text-dark-500': getStepStatus(index) === 'upcoming',
            }"
          >
            {{ step.name }}
          </span>
        </div>
        <div
          v-if="index < steps.length - 1"
          class="flex-1 mx-4 h-0.5"
          :class="{
            'bg-primary-600': getStepStatus(index) === 'completed',
            'bg-dark-700': getStepStatus(index) !== 'completed',
          }"
        />
      </li>
    </ol>
  </nav>
</template>
