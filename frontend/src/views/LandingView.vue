<script setup lang="ts">
import { ref } from 'vue'
import { useSession } from '../composables/useSession'

const { startNewSession, store } = useSession()
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
