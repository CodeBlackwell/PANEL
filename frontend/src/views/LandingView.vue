<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../composables/useSession'
import { useAuthStore } from '../stores/auth'

const { startNewSession, store } = useSession()
const authStore = useAuthStore()
const router = useRouter()
const idea = ref('')
const isSubmitting = ref(false)

async function handleSubmit() {
  if (!idea.value.trim() || idea.value.length < 10) return

  isSubmitting.value = true
  try {
    await startNewSession(idea.value)
  } catch (e) {
    console.error('Failed to start session:', e)
  } finally {
    isSubmitting.value = false
  }
}

function handleUseGitHub() {
  if (authStore.isAuthenticated) {
    router.push('/repos')
  } else {
    // Store redirect destination
    localStorage.setItem('auth_redirect', '/repos')
    router.push('/login')
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl mb-6 shadow-lg shadow-primary-500/25">
        <span class="text-white font-bold text-2xl">AX</span>
      </div>
      <h1 class="text-4xl font-bold text-dark-100 mb-4">
        Transform Ideas into
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-400">
          Production-Ready PRDs
        </span>
      </h1>
      <p class="text-lg text-dark-400 max-w-xl mx-auto">
        Let our multi-agent system clarify your vision, debate the best approaches,
        and deliver a comprehensive Product Requirements Document.
      </p>
    </div>

    <!-- Input Form -->
    <div class="card p-8">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="idea" class="label">
            Describe Your Project Idea
          </label>
          <textarea
            id="idea"
            v-model="idea"
            class="textarea h-48"
            placeholder="Describe your project idea in detail. What problem does it solve? Who are the target users? What are the key features you envision?"
            :disabled="isSubmitting"
          />
          <p class="mt-2 text-sm text-dark-500">
            Minimum 10 characters. Be as detailed as possible for better results.
          </p>
        </div>

        <button
          type="submit"
          class="btn-primary w-full py-4 text-lg"
          :disabled="idea.length < 10 || isSubmitting"
          :class="{ 'opacity-50 cursor-not-allowed': idea.length < 10 || isSubmitting }"
        >
          <span v-if="isSubmitting" class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Creating Session...
          </span>
          <span v-else>Start PRD Generation</span>
        </button>
      </form>

      <!-- Divider -->
      <div class="relative my-8">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-dark-700" />
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-4 bg-dark-800 text-dark-400">or</span>
        </div>
      </div>

      <!-- GitHub Option -->
      <button
        @click="handleUseGitHub"
        class="w-full flex items-center justify-center gap-3 px-6 py-4 bg-dark-700 hover:bg-dark-600 text-dark-100 rounded-lg font-medium transition-colors border border-dark-600"
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
        </svg>
        Use existing GitHub repository
      </button>
      <p class="mt-3 text-center text-sm text-dark-500">
        Generate a PRD from an existing codebase. Requires GitHub sign-in for private repos.
      </p>
    </div>

    <!-- Features -->
    <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6 text-center">
        <div class="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-dark-100 mb-2">Smart Clarification</h3>
        <p class="text-dark-400 text-sm">AI asks targeted questions to understand your vision completely.</p>
      </div>

      <div class="card p-6 text-center">
        <div class="w-12 h-12 bg-accent-600/20 rounded-lg flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-dark-100 mb-2">Expert Debate</h3>
        <p class="text-dark-400 text-sm">Specialized AI agents debate architecture, security, UX, and more.</p>
      </div>

      <div class="card p-6 text-center">
        <div class="w-12 h-12 bg-green-600/20 rounded-lg flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-dark-100 mb-2">Judicial Review</h3>
        <p class="text-dark-400 text-sm">Three judges evaluate feasibility, technical soundness, and business value.</p>
      </div>
    </div>
  </div>
</template>
