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

    // Short delay before redirect for visual feedback
    setTimeout(() => {
      const redirectPath = authStore.getRedirectPath()
      // If redirect was to repos and we have it stored, go there
      if (redirectPath.includes('/repos')) {
        router.push('/repos')
      } else {
        router.push(redirectPath)
      }
    }, 1000)
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e instanceof Error ? e.message : 'Authentication failed'
  }
})

function retryLogin() {
  router.push('/login')
}

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card p-8 text-center">
      <!-- Processing -->
      <div v-if="status === 'processing'">
        <div class="inline-flex items-center justify-center w-16 h-16 mb-6">
          <svg class="animate-spin h-10 w-10 text-primary-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-dark-100 mb-2">
          Completing sign in...
        </h1>
        <p class="text-dark-400">
          Please wait while we verify your authentication.
        </p>
      </div>

      <!-- Success -->
      <div v-else-if="status === 'success'">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-6">
          <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-dark-100 mb-2">
          Welcome, {{ authStore.username }}!
        </h1>
        <p class="text-dark-400">
          Redirecting you now...
        </p>
      </div>

      <!-- Error -->
      <div v-else>
        <div class="inline-flex items-center justify-center w-16 h-16 bg-red-500/20 rounded-full mb-6">
          <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-dark-100 mb-2">
          Authentication Failed
        </h1>
        <p class="text-dark-400 mb-6">
          {{ errorMessage }}
        </p>
        <div class="flex gap-3 justify-center">
          <button
            @click="retryLogin"
            class="btn-primary px-6 py-2"
          >
            Try Again
          </button>
          <button
            @click="goHome"
            class="btn-secondary px-6 py-2"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
