<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  agentName: string
  agentType: string
  content: string
  messageType?: string
  roundNumber?: number
  staggerIndex?: number
}>()

// Map agent type to its chalk color CSS variable for inline styles
const agentColor = computed(() => {
  const colors: Record<string, string> = {
    architect: '#7eaac4',
    devops: '#7cb88c',
    security: '#c47e7e',
    ux: '#a77ec4',
    qa: '#c4b87e',
    product_manager: '#c47eaa',
    data_engineer: '#7ec4c4',
    ml_engineer: '#c4a07e',
    frontend_dev: '#7e8cc4',
    backend_dev: '#7ec4a0',
    mobile_dev: '#c47e94',
    business_analyst: '#c4b07e',
    tech_lead: '#7ec4b0',
    moderator: '#8a8a8a',
    clarifier: '#9a7ec4',
    user: '#6b8cae',
    judge_business: '#e8d88c',
    judge_technical: '#6b8cae',
    judge_feasibility: '#7cb88c',
  }
  return colors[props.agentType] || '#8a8a8a'
})

const messageTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    proposal: 'Proposal',
    critique: 'Critique',
    agreement: 'Agreement',
    summary: 'Summary',
    question: 'Question',
    answer: 'Answer',
    evaluation: 'Evaluation',
  }
  return labels[props.messageType || ''] || null
})

const isUser = computed(() => props.agentType === 'user')

const staggerDelay = computed(() => {
  const idx = props.staggerIndex ?? 0
  return `${idx * 0.08}s`
})
</script>

<template>
  <div
    class="animate-chalk-in"
    :style="{ animationDelay: staggerDelay }"
  >
    <!-- User answers: compact, right-aligned -->
    <div
      v-if="isUser"
      class="ml-12 pl-4 pr-4 py-3 border-l-[3px] border rounded-sm"
      :style="{
        borderLeftColor: agentColor,
        borderColor: agentColor + '30',
        borderLeftWidth: '3px',
        backgroundColor: agentColor + '18',
      }"
    >
      <div class="flex items-center gap-2 mb-1 justify-end">
        <span class="font-chalk text-base" :style="{ color: agentColor }">You</span>
      </div>
      <p class="text-sm leading-relaxed whitespace-pre-wrap text-right" :style="{ color: agentColor }">{{ content }}</p>
    </div>

    <!-- Agent messages: chalk frame -->
    <div
      v-else
      class="pl-4 pr-4 py-3 border-l-[3px] border rounded-sm transition-colors duration-300"
      :style="{
        borderLeftColor: agentColor,
        borderColor: agentColor + '25',
        borderLeftWidth: '3px',
        backgroundColor: agentColor + '18',
      }"
    >
      <!-- Header: agent name + type badge -->
      <div class="flex items-baseline justify-between mb-2">
        <div class="flex items-baseline gap-2">
          <span
            class="font-chalk text-xl font-semibold"
            :style="{ color: agentColor }"
          >
            {{ agentName }}
          </span>
          <span v-if="roundNumber" class="font-chalk text-sm text-chalk-faint">
            r{{ roundNumber }}
          </span>
        </div>
        <span
          v-if="messageTypeLabel"
          class="font-chalk text-base px-2 rounded"
          :style="{
            color: agentColor,
            backgroundColor: agentColor + '15',
          }"
        >
          {{ messageTypeLabel }}
        </span>
      </div>

      <!-- Message body — in agent's chalk color, serif font -->
      <p
        class="text-sm leading-relaxed whitespace-pre-wrap pr-2 font-heading"
        :style="{ color: agentColor, opacity: 0.85 }"
      >{{ content }}</p>
    </div>
  </div>
</template>
