<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  score: number
  color?: 'dusty' | 'yellow' | 'green' | 'purple'
  staggerIndex?: number
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

const glowClass = computed(() => {
  const glows = {
    dusty: 'glow-dusty',
    yellow: 'glow-yellow',
    green: 'glow-dusty',
    purple: 'glow-dusty',
  }
  return glows[props.color || 'dusty']
})

const percentage = computed(() => (props.score / 10) * 100)

const formattedLabel = computed(() => {
  return props.label
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
})

const fillDelay = computed(() => {
  const idx = props.staggerIndex ?? 0
  return `${idx * 0.15}s`
})
</script>

<template>
  <div class="animate-chalk-in" :style="{ animationDelay: fillDelay }">
    <div class="flex justify-between mb-1">
      <span class="text-chalk-faint font-chalk text-base">{{ formattedLabel }}</span>
      <span class="text-chalk font-chalk text-lg font-semibold">{{ score }}/10</span>
    </div>
    <div class="w-full bg-slate-border/60 rounded-full h-1.5 overflow-hidden">
      <div
        class="h-1.5 rounded-full animate-score-fill"
        :class="[colorClasses, glowClass]"
        :style="{ width: `${percentage}%`, animationDelay: fillDelay }"
      />
    </div>
  </div>
</template>
