<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { onMounted, onErrorCaptured, ref } from 'vue'

const authStore = useAuthStore()
const appError = ref<string | null>(null)

onMounted(() => {
  authStore.initialize()
})

onErrorCaptured((err: Error) => {
  console.error('Application error:', err)
  appError.value = err.message || 'An unexpected error occurred'
  return false
})

function dismissError() {
  appError.value = null
}
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-slate bg-grain font-body">
    <!-- Global error banner -->
    <div
      v-if="appError"
      class="fixed top-0 left-0 right-0 z-[100] bg-agent-security/90 border-b border-agent-security px-4 py-2 flex items-center justify-between"
    >
      <p class="text-chalk text-sm">{{ appError }}</p>
      <button @click="dismissError" class="text-chalk/70 hover:text-chalk text-sm font-medium ml-4">
        Dismiss
      </button>
    </div>
    <RouterView />
  </div>
</template>
