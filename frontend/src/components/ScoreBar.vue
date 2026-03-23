<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  score: number
  color?: 'dusty' | 'yellow' | 'green' | 'purple'
}>()

const colorClasses = computed(() => {
  const colors = {
    dusty: 'bg-dusty',
    yellow: 'bg-yellow',
    green: 'bg-agent-devops',
    purple: 'bg-agent-ux',
  }
  return colors[props.color || 'dusty']
})

const percentage = computed(() => (props.score / 10) * 100)

// Format label to title case
const formattedLabel = computed(() => {
  return props.label
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
})
</script>

<template>
  <div>
    <div class="flex justify-between text-sm mb-1">
      <span class="text-chalk-faint">{{ formattedLabel }}</span>
      <span class="text-chalk font-medium">{{ score }}/10</span>
    </div>
    <div class="w-full bg-slate-border rounded-full h-1.5 overflow-hidden">
      <div
        class="h-1.5 rounded-full animate-score-fill"
        :class="colorClasses"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>
