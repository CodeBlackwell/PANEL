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
  <div class="space-y-8">
    <div v-if="messages.length === 0" class="text-center text-dark-400 py-8">
      Waiting for debate to begin...
    </div>

    <div v-for="round in rounds" :key="round" class="space-y-4">
      <!-- Round Header -->
      <div class="flex items-center gap-4">
        <div class="h-px flex-1 bg-dark-700" />
        <span class="text-sm font-medium text-dark-400 px-3 py-1 bg-dark-800 rounded-full">
          Round {{ round }}
        </span>
        <div class="h-px flex-1 bg-dark-700" />
      </div>

      <!-- Messages in this round -->
      <div class="space-y-4 pl-4 border-l-2 border-dark-700">
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
