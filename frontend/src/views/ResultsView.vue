<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { api } from '../services/api'

const router = useRouter()
const route = useRoute()
const store = useSessionStore()

const sessionId = computed(() => route.params.sessionId as string)

onMounted(async () => {
  if (sessionId.value !== store.sessionId) {
    await store.loadSession(sessionId.value)
  }
})

function downloadZip() {
  window.location.href = api.getDownloadUrl(sessionId.value)
}

function startNew() {
  store.reset()
  router.push('/')
}

const artifacts = [
  { name: 'PRD.md', description: 'Complete Product Requirements Document', icon: 'document' },
  { name: 'README.md', description: 'Project overview and setup instructions', icon: 'book' },
  { name: 'original_prompt.txt', description: 'Your original project idea', icon: 'chat' },
  { name: 'transcripts/', description: 'Clarification, debate, and review logs', icon: 'folder' },
  { name: 'metadata/', description: 'Session data and scores', icon: 'data' },
  { name: 'exports/', description: 'Requirements and decisions as JSON', icon: 'code' },
]

const averageScore = computed(() => {
  if (store.judgeScores.length === 0) return 0
  const sum = store.judgeScores.reduce((acc, j) => acc + j.overallScore, 0)
  return (sum / store.judgeScores.length).toFixed(1)
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Success Header -->
    <div class="text-center mb-12">
      <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl mb-6 shadow-lg shadow-green-500/25">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
      </div>
      <h1 class="text-3xl font-bold text-dark-100 mb-2">PRD Generation Complete!</h1>
      <p class="text-dark-400 max-w-xl mx-auto">
        Your comprehensive Product Requirements Document has been generated and is ready for download.
      </p>
    </div>

    <!-- Score Summary -->
    <div class="card p-6 mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-dark-100 mb-1">Overall Project Score</h3>
          <p class="text-dark-400 text-sm">Based on business, technical, and feasibility evaluations</p>
        </div>
        <div class="text-right">
          <div class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-400">
            {{ averageScore }}
          </div>
          <p class="text-dark-400 text-sm">out of 10</p>
        </div>
      </div>

      <div v-if="store.overallVerdict" class="mt-4 pt-4 border-t border-dark-700">
        <p class="text-dark-300">{{ store.overallVerdict }}</p>
      </div>
    </div>

    <!-- Artifacts List -->
    <div class="card p-6 mb-8">
      <h3 class="text-lg font-semibold text-dark-100 mb-4">ZIP Contents</h3>
      <div class="space-y-3">
        <div
          v-for="artifact in artifacts"
          :key="artifact.name"
          class="flex items-center gap-4 p-3 bg-dark-700/50 rounded-lg"
        >
          <div class="w-10 h-10 bg-dark-600 rounded-lg flex items-center justify-center">
            <svg v-if="artifact.icon === 'document'" class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <svg v-else-if="artifact.icon === 'book'" class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
            <svg v-else-if="artifact.icon === 'chat'" class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <svg v-else-if="artifact.icon === 'folder'" class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            <svg v-else-if="artifact.icon === 'data'" class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
            </svg>
            <svg v-else class="w-5 h-5 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="font-medium text-dark-100">{{ artifact.name }}</h4>
            <p class="text-sm text-dark-400">{{ artifact.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-4">
      <button @click="downloadZip" class="btn-primary flex-1 py-4 text-lg flex items-center justify-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
        Download ZIP
      </button>
      <button @click="startNew" class="btn-secondary flex-1 py-4 text-lg">
        Start New Project
      </button>
    </div>
  </div>
</template>
