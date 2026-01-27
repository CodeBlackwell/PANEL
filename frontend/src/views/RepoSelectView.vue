<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGitHubStore } from '../stores/github'
import { useSessionStore } from '../stores/session'
import { useAuthStore } from '../stores/auth'
import RepoCard from '../components/RepoCard.vue'
import type { RepoInfo } from '../services/githubApi'
import { api } from '../services/api'

const router = useRouter()
const githubStore = useGitHubStore()
const sessionStore = useSessionStore()
const authStore = useAuthStore()

const isCreatingSession = ref(false)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (!githubStore.hasRepos) {
    await githubStore.fetchRepos(1, true)
  }
})

function handleRepoSelect(repo: RepoInfo) {
  githubStore.selectRepo(repo)
}

async function handleContinue() {
  if (!githubStore.selectedRepo) return

  isCreatingSession.value = true

  try {
    // Parse owner and repo name
    const [owner, repoName] = githubStore.selectedRepo.full_name.split('/')

    // Fetch repository context
    const context = await githubStore.fetchRepoContext(owner, repoName)

    // Create session with repo context
    const response = await api.createSession({ repo_context: context })

    // Update session store
    sessionStore.sessionId = response.session_id
    sessionStore.phase = response.phase as any

    // Navigate to config page
    router.push({ name: 'config', params: { sessionId: response.session_id } })
  } catch (e) {
    console.error('Failed to create session:', e)
  } finally {
    isCreatingSession.value = false
  }
}

function handleLoadMore() {
  githubStore.loadMoreRepos()
}

function handleSearch(event: Event) {
  const target = event.target as HTMLInputElement
  githubStore.setSearchQuery(target.value)
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-dark-100 mb-2">
        Select a Repository
      </h1>
      <p class="text-dark-400">
        Choose a repository to generate a PRD from. We'll analyze the codebase
        structure, README, and configuration files.
      </p>
    </div>

    <!-- Search Bar -->
    <div class="mb-6">
      <div class="relative">
        <svg
          class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          placeholder="Search repositories..."
          :value="githubStore.searchQuery"
          @input="handleSearch"
          class="input pl-12"
        />
      </div>
    </div>

    <!-- Error State -->
    <div v-if="githubStore.error" class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
      <p class="text-red-400">{{ githubStore.error }}</p>
      <button
        @click="githubStore.refreshRepos"
        class="mt-2 text-sm text-red-400 hover:text-red-300 underline"
      >
        Try again
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="githubStore.isLoading && !githubStore.hasRepos" class="text-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      <p class="text-dark-400">Loading repositories...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!githubStore.hasRepos && !githubStore.isLoading" class="text-center py-12">
      <div class="w-16 h-16 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
        </svg>
      </div>
      <p class="text-dark-300 mb-2">No repositories found</p>
      <p class="text-dark-500 text-sm">
        Make sure your GitHub account has accessible repositories.
      </p>
    </div>

    <!-- Repository List -->
    <div v-else class="space-y-3 mb-6">
      <RepoCard
        v-for="repo in githubStore.filteredRepos"
        :key="repo.id"
        :repo="repo"
        :selected="githubStore.selectedRepo?.id === repo.id"
        @select="handleRepoSelect"
      />

      <!-- Load More Button -->
      <div v-if="githubStore.hasMore && !githubStore.searchQuery" class="text-center pt-4">
        <button
          @click="handleLoadMore"
          :disabled="githubStore.isLoading"
          class="btn-secondary px-6 py-2"
          :class="{ 'opacity-50': githubStore.isLoading }"
        >
          <span v-if="githubStore.isLoading" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Loading...
          </span>
          <span v-else>Load more repositories</span>
        </button>
      </div>
    </div>

    <!-- Selected Repo Info & Continue Button -->
    <div
      v-if="githubStore.selectedRepo"
      class="fixed bottom-0 left-0 right-0 bg-dark-900 border-t border-dark-700 p-4"
    >
      <div class="max-w-4xl mx-auto flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-10 bg-dark-800 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-dark-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-dark-100 font-medium truncate">
              {{ githubStore.selectedRepo.name }}
            </p>
            <p class="text-dark-400 text-sm truncate">
              {{ githubStore.selectedRepo.full_name }}
            </p>
          </div>
        </div>

        <button
          @click="handleContinue"
          :disabled="isCreatingSession || githubStore.isLoadingContext"
          class="btn-primary px-6 py-3 flex-shrink-0"
          :class="{ 'opacity-50 cursor-not-allowed': isCreatingSession || githubStore.isLoadingContext }"
        >
          <span v-if="isCreatingSession || githubStore.isLoadingContext" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Analyzing...
          </span>
          <span v-else>Continue with this repo</span>
        </button>
      </div>
    </div>

    <!-- Spacer for fixed bottom bar -->
    <div v-if="githubStore.selectedRepo" class="h-24" />
  </div>
</template>
