<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  agentName: string
  agentType: string
  content: string
  messageType?: string
  roundNumber?: number
}>()

const avatarClass = computed(() => {
  const colorMap: Record<string, string> = {
    architect: 'bg-blue-600',
    devops: 'bg-green-600',
    security: 'bg-red-600',
    ux: 'bg-purple-600',
    qa: 'bg-yellow-600',
    product_manager: 'bg-pink-600',
    data_engineer: 'bg-cyan-600',
    ml_engineer: 'bg-orange-600',
    frontend_dev: 'bg-indigo-600',
    backend_dev: 'bg-teal-600',
    mobile_dev: 'bg-rose-600',
    business_analyst: 'bg-amber-600',
    tech_lead: 'bg-emerald-600',
    moderator: 'bg-gray-600',
    clarifier: 'bg-violet-600',
    user: 'bg-dark-600',
    judge_business: 'bg-amber-600',
    judge_technical: 'bg-blue-600',
    judge_feasibility: 'bg-green-600',
  }
  return colorMap[props.agentType] || 'bg-gray-600'
})

const messageTypeLabel = computed(() => {
  const labels: Record<string, { text: string; class: string }> = {
    proposal: { text: 'Proposal', class: 'bg-blue-500/20 text-blue-400' },
    critique: { text: 'Critique', class: 'bg-red-500/20 text-red-400' },
    agreement: { text: 'Agreement', class: 'bg-green-500/20 text-green-400' },
    summary: { text: 'Summary', class: 'bg-purple-500/20 text-purple-400' },
    question: { text: 'Question', class: 'bg-violet-500/20 text-violet-400' },
    answer: { text: 'Answer', class: 'bg-dark-500/20 text-dark-300' },
    evaluation: { text: 'Evaluation', class: 'bg-amber-500/20 text-amber-400' },
  }
  return labels[props.messageType || ''] || null
})

const initials = computed(() => {
  return props.agentName.slice(0, 2).toUpperCase()
})

const isUser = computed(() => props.agentType === 'user')
</script>

<template>
  <div
    class="flex gap-3 animate-fade-in"
    :class="{ 'flex-row-reverse': isUser }"
  >
    <!-- Avatar -->
    <div
      class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
      :class="avatarClass"
    >
      {{ initials }}
    </div>

    <!-- Message Content -->
    <div
      class="flex-1 max-w-[80%]"
      :class="{ 'text-right': isUser }"
    >
      <div class="flex items-center gap-2 mb-1" :class="{ 'justify-end': isUser }">
        <span class="font-medium text-dark-200">{{ agentName }}</span>
        <span
          v-if="messageTypeLabel"
          class="text-xs px-2 py-0.5 rounded-full"
          :class="messageTypeLabel.class"
        >
          {{ messageTypeLabel.text }}
        </span>
        <span v-if="roundNumber" class="text-xs text-dark-500">
          Round {{ roundNumber }}
        </span>
      </div>

      <div
        class="rounded-xl p-4 text-sm"
        :class="{
          'bg-dark-700 text-dark-200': !isUser,
          'bg-primary-600 text-white': isUser,
        }"
      >
        <p class="whitespace-pre-wrap">{{ content }}</p>
      </div>
    </div>
  </div>
</template>
