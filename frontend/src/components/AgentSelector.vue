<script setup lang="ts">
import { computed } from 'vue'
import type { AgentInfo } from '../services/api'

const props = defineProps<{
  agents: AgentInfo[]
  min: number
  max: number
}>()

const model = defineModel<string[]>({ required: true })

function toggleAgent(agentId: string) {
  const index = model.value.indexOf(agentId)
  if (index === -1) {
    if (model.value.length < props.max) {
      model.value = [...model.value, agentId]
    }
  } else {
    if (model.value.length > props.min) {
      model.value = model.value.filter(id => id !== agentId)
    }
  }
}

function isSelected(agentId: string): boolean {
  return model.value.includes(agentId)
}

function canSelect(agentId: string): boolean {
  if (isSelected(agentId)) {
    return model.value.length > props.min
  }
  return model.value.length < props.max
}

const agentColors: Record<string, string> = {
  architect: 'from-blue-600 to-blue-700',
  devops: 'from-green-600 to-green-700',
  security: 'from-red-600 to-red-700',
  ux: 'from-purple-600 to-purple-700',
  qa: 'from-yellow-600 to-yellow-700',
  product_manager: 'from-pink-600 to-pink-700',
  data_engineer: 'from-cyan-600 to-cyan-700',
  ml_engineer: 'from-orange-600 to-orange-700',
  frontend_dev: 'from-indigo-600 to-indigo-700',
  backend_dev: 'from-teal-600 to-teal-700',
  mobile_dev: 'from-rose-600 to-rose-700',
  business_analyst: 'from-amber-600 to-amber-700',
  tech_lead: 'from-emerald-600 to-emerald-700',
}
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    <button
      v-for="agent in agents"
      :key="agent.id"
      @click="toggleAgent(agent.id)"
      class="relative p-4 rounded-xl border-2 text-left transition-all duration-200"
      :class="{
        'border-primary-500 bg-primary-500/10': isSelected(agent.id),
        'border-dark-700 bg-dark-800 hover:border-dark-600': !isSelected(agent.id),
        'opacity-50 cursor-not-allowed': !canSelect(agent.id) && !isSelected(agent.id),
      }"
      :disabled="!canSelect(agent.id) && !isSelected(agent.id)"
    >
      <div class="flex items-start gap-3">
        <div
          class="w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm shrink-0"
          :class="agentColors[agent.id] || 'from-gray-600 to-gray-700'"
        >
          {{ agent.name.slice(0, 2).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <h4 class="font-medium text-dark-100 flex items-center gap-2">
            {{ agent.name }}
            <span
              v-if="agent.default_selected"
              class="text-xs px-1.5 py-0.5 bg-primary-600/20 text-primary-400 rounded"
            >
              Default
            </span>
          </h4>
          <p class="text-sm text-dark-400 mt-1 line-clamp-2">{{ agent.focus_area }}</p>
        </div>
      </div>

      <!-- Selected indicator -->
      <div
        v-if="isSelected(agent.id)"
        class="absolute top-2 right-2 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center"
      >
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
      </div>
    </button>
  </div>
</template>
