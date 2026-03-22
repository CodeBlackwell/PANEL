<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  // If already authenticated, redirect
  if (authStore.isAuthenticated) {
    router.push(authStore.getRedirectPath())
  }
})

function handleLogin() {
  authStore.loginWithGitHub()
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card p-8 text-center">
      <!-- Logo -->
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl mb-6 shadow-lg shadow-primary-500/25">
        <span class="text-white font-bold text-xl">PN</span>
      </div>

      <h1 class="text-2xl font-bold text-dark-100 mb-2">
        Sign in to PANEL
      </h1>
      <p class="text-dark-400 mb-8">
        Connect your GitHub account to access your private repositories.
      </p>

      <!-- Error Message -->
      <div v-if="authStore.error" class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p class="text-red-400 text-sm">{{ authStore.error }}</p>
      </div>

      <!-- GitHub Login Button -->
      <button
        @click="handleLogin"
        :disabled="authStore.isLoading"
        class="w-full flex items-center justify-center gap-3 px-6 py-4 bg-dark-800 hover:bg-dark-700 text-dark-100 rounded-lg font-medium transition-colors border border-dark-700"
        :class="{ 'opacity-50 cursor-not-allowed': authStore.isLoading }"
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
        </svg>
        <span v-if="authStore.isLoading">Connecting...</span>
        <span v-else>Continue with GitHub</span>
      </button>

      <!-- Info -->
      <p class="mt-6 text-sm text-dark-500">
        We'll request access to read your repositories and profile information.
      </p>

      <!-- Back Link -->
      <router-link
        to="/"
        class="inline-block mt-6 text-sm text-primary-400 hover:text-primary-300 transition-colors"
      >
        Continue without signing in
      </router-link>
    </div>
  </div>
</template>
