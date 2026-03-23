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
  return `agent-${props.agentType}`
})

const messageTypeLabel = computed(() => {
  const labels: Record<string, { text: string; class: string }> = {
    proposal: { text: 'Proposal', class: 'bg-dusty/15 text-dusty' },
    critique: { text: 'Critique', class: 'bg-agent-security/15 text-agent-security' },
    agreement: { text: 'Agreement', class: 'bg-agent-devops/15 text-agent-devops' },
    summary: { text: 'Summary', class: 'bg-agent-ux/15 text-agent-ux' },
    question: { text: 'Question', class: 'bg-agent-clarifier/15 text-agent-clarifier' },
    answer: { text: 'Answer', class: 'bg-dusty/15 text-dusty' },
    evaluation: { text: 'Evaluation', class: 'bg-yellow/15 text-yellow' },
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
    class="flex gap-3 animate-chalk-in"
    :class="{ 'flex-row-reverse': isUser }"
  >
    <!-- Avatar -->
    <div
      class="w-8 h-8 rounded-full flex items-center justify-center text-slate font-bold text-xs shrink-0"
      :class="avatarClass"
    >
      {{ initials }}
    </div>

    <!-- Message Content -->
    <div
      class="flex-1 max-w-[85%]"
      :class="{ 'text-right': isUser }"
    >
      <div class="flex items-center gap-2 mb-1" :class="{ 'justify-end': isUser }">
        <span class="font-medium text-chalk text-sm">{{ agentName }}</span>
        <span
          v-if="messageTypeLabel"
          class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
          :class="messageTypeLabel.class"
        >
          {{ messageTypeLabel.text }}
        </span>
        <span v-if="roundNumber" class="text-[10px] text-chalk-faint">
          Round {{ roundNumber }}
        </span>
      </div>

      <div
        class="rounded-lg px-4 py-3 text-sm leading-relaxed"
        :class="{
          'bg-slate border border-slate-border text-chalk-dim': !isUser,
          'bg-dusty/15 border border-dusty/20 text-chalk': isUser,
        }"
      >
        <p class="whitespace-pre-wrap">{{ content }}</p>
      </div>
    </div>
  </div>
</template>
