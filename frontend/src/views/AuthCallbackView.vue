<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const status = ref<'processing' | 'success' | 'error'>('processing')
const errorMessage = ref('')

onMounted(async () => {
  const token = route.query.token as string | undefined
  const error = route.query.error as string | undefined

  if (error) {
    status.value = 'error'
    errorMessage.value = error
    return
  }

  if (!token) {
    status.value = 'error'
    errorMessage.value = 'No authentication token received'
    return
  }

  try {
    await authStore.handleCallback(token)
    status.value = 'success'
    setTimeout(() => router.push('/'), 1000)
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e instanceof Error ? e.message : 'Authentication failed'
  }
})

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="flex items-center justify-center h-full">
    <div class="card p-8 text-center max-w-sm">
      <!-- Processing -->
      <div v-if="status === 'processing'">
        <div class="inline-flex items-center justify-center w-12 h-12 mb-4">
          <svg class="animate-spin h-8 w-8 text-dusty" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        </div>
        <h1 class="text-lg font-heading font-bold text-chalk mb-1">Signing in...</h1>
        <p class="text-chalk-dim text-sm">Verifying authentication.</p>
      </div>

      <!-- Success -->
      <div v-else-if="status === 'success'">
        <div class="inline-flex items-center justify-center w-12 h-12 bg-agent-devops/20 rounded-full mb-4">
          <svg class="w-6 h-6 text-agent-devops" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h1 class="text-lg font-heading font-bold text-chalk mb-1">
          Welcome{{ authStore.user?.username ? ', ' + authStore.user.username : '' }}
        </h1>
        <p class="text-chalk-dim text-sm">Redirecting...</p>
      </div>

      <!-- Error -->
      <div v-else>
        <div class="inline-flex items-center justify-center w-12 h-12 bg-agent-security/20 rounded-full mb-4">
          <svg class="w-6 h-6 text-agent-security" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h1 class="text-lg font-heading font-bold text-chalk mb-1">Authentication Failed</h1>
        <p class="text-chalk-dim text-sm mb-4">{{ errorMessage }}</p>
        <button @click="goHome" class="btn-primary px-6 py-2">Back to PANEL</button>
      </div>
    </div>
  </div>
</template>
