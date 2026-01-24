<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  min: number
  max: number
}>()

const model = defineModel<number>({ required: true })

const percentage = computed(() => {
  return ((model.value - props.min) / (props.max - props.min)) * 100
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <span class="text-dark-400">Rounds:</span>
      <span class="text-2xl font-bold text-primary-400">{{ model }}</span>
    </div>

    <div class="relative">
      <input
        type="range"
        v-model.number="model"
        :min="min"
        :max="max"
        class="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
        :style="{
          background: `linear-gradient(to right, #3b82f6 ${percentage}%, #334155 ${percentage}%)`
        }"
      />
      <div class="flex justify-between mt-2 text-sm text-dark-500">
        <span>{{ min }} (Quick)</span>
        <span>{{ max }} (Thorough)</span>
      </div>
    </div>

    <p class="text-sm text-dark-400">
      <span v-if="model <= 4">Quick debate with essential discussion points.</span>
      <span v-else-if="model <= 7">Balanced debate covering most aspects.</span>
      <span v-else>Thorough debate exploring all perspectives.</span>
    </p>
  </div>
</template>

<style scoped>
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #1e293b;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #1e293b;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style>
