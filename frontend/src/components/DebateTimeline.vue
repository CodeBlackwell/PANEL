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
    <div v-if="messages.length === 0" class="text-center text-chalk-faint py-8 font-chalk text-xl">
      Waiting for debate to begin...
    </div>

    <div v-for="round in rounds" :key="round" class="animate-chalk-fade">
      <!-- Round Header with line-draw dividers -->
      <div class="flex items-center gap-4 mb-5">
        <div class="h-px flex-1 bg-chalk-faint/20 origin-left animate-line-draw" />
        <span class="font-chalk text-2xl text-chalk-faint">
          Round {{ round }}
        </span>
        <div class="h-px flex-1 bg-chalk-faint/20 origin-right animate-line-draw" />
      </div>

      <!-- Messages in this round with staggered entry -->
      <div class="space-y-4">
        <AgentMessage
          v-for="(msg, index) in messagesByRound[round]"
          :key="`${round}-${index}`"
          :agent-name="msg.agentName"
          :agent-type="msg.agentType"
          :content="msg.content"
          :message-type="msg.messageType"
          :round-number="msg.roundNumber"
          :stagger-index="index"
        />
      </div>
    </div>
  </div>
</template>
