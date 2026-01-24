<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  score: number
  color?: 'blue' | 'amber' | 'green' | 'purple'
}>()

const colorClasses = computed(() => {
  const colors = {
    blue: 'bg-blue-500',
    amber: 'bg-amber-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
  }
  return colors[props.color || 'blue']
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
      <span class="text-dark-400">{{ formattedLabel }}</span>
      <span class="text-dark-200 font-medium">{{ score }}/10</span>
    </div>
    <div class="w-full bg-dark-700 rounded-full h-2 overflow-hidden">
      <div
        class="h-2 rounded-full transition-all duration-1000 ease-out"
        :class="colorClasses"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>
