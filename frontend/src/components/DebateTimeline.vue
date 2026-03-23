<script setup lang="ts">
import { computed } from 'vue'
import type { DebateMessage } from '../stores/session'
import AgentMessage from './AgentMessage.vue'

const props = defineProps<{
  messages: DebateMessage[]
}>()

// Group messages by round
const messagesByRound = computed(() => {
  const grouped: Record<number, DebateMessage[]> = {}
  props.messages.forEach(msg => {
    if (!grouped[msg.roundNumber]) {
      grouped[msg.roundNumber] = []
    }
    grouped[msg.roundNumber].push(msg)
  })
  return grouped
})

const rounds = computed(() => {
  return Object.keys(messagesByRound.value).map(Number).sort((a, b) => a - b)
})
</script>

<template>
  <div class="space-y-6">
    <div v-if="messages.length === 0" class="text-center text-chalk-faint py-8 text-sm">
      Waiting for debate to begin...
    </div>

    <div v-for="round in rounds" :key="round" class="space-y-4">
      <!-- Round Header -->
      <div class="flex items-center gap-4">
        <div class="h-px flex-1 bg-slate-border" />
        <span class="text-xs font-medium text-chalk-faint px-3 py-1 bg-slate-light rounded-full font-heading">
          Round {{ round }}
        </span>
        <div class="h-px flex-1 bg-slate-border" />
      </div>

      <!-- Messages in this round -->
      <div class="space-y-3 pl-3 border-l border-slate-border">
        <AgentMessage
          v-for="(msg, index) in messagesByRound[round]"
          :key="`${round}-${index}`"
          :agent-name="msg.agentName"
          :agent-type="msg.agentType"
          :content="msg.content"
          :message-type="msg.messageType"
          :round-number="msg.roundNumber"
        />
      </div>
    </div>
  </div>
</template>
