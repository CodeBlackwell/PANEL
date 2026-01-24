<script setup lang="ts">
import { RouterView } from 'vue-router'
import ProgressStepper from './components/ProgressStepper.vue'
import { useSessionStore } from './stores/session'

const sessionStore = useSessionStore()
</script>

<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Header -->
    <header class="border-b border-dark-800 bg-dark-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">AX</span>
            </div>
            <h1 class="text-xl font-bold text-dark-100">ArchitX</h1>
          </div>
          <p class="text-dark-400 text-sm">Multi-Agent PRD Generator</p>
        </div>
      </div>
    </header>

    <!-- Progress Stepper (shown when session exists) -->
    <div v-if="sessionStore.sessionId" class="border-b border-dark-800 bg-dark-900/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ProgressStepper :current-phase="sessionStore.phase" />
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="border-t border-dark-800 py-6 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-dark-500 text-sm">
        Powered by AutoGen + GPT-4o
      </div>
    </footer>
  </div>
</template>
