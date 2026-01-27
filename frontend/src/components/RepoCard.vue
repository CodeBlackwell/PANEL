<script setup lang="ts">
import { computed } from 'vue'
import type { RepoInfo } from '../services/githubApi'

const props = defineProps<{
  repo: RepoInfo
  selected?: boolean
}>()

const emit = defineEmits<{
  select: [repo: RepoInfo]
}>()

const formattedDate = computed(() => {
  const date = new Date(props.repo.updated_at)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Updated today'
  if (diffDays === 1) return 'Updated yesterday'
  if (diffDays < 7) return `Updated ${diffDays} days ago`
  if (diffDays < 30) return `Updated ${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `Updated ${Math.floor(diffDays / 30)} months ago`
  return `Updated ${Math.floor(diffDays / 365)} years ago`
})

const languageColor = computed(() => {
  const colors: Record<string, string> = {
    JavaScript: 'bg-yellow-400',
    TypeScript: 'bg-blue-500',
    Python: 'bg-green-500',
    Rust: 'bg-orange-500',
    Go: 'bg-cyan-500',
    Java: 'bg-red-500',
    Ruby: 'bg-red-400',
    PHP: 'bg-purple-500',
    'C++': 'bg-pink-500',
    C: 'bg-gray-500',
    'C#': 'bg-green-600',
    Swift: 'bg-orange-400',
    Kotlin: 'bg-purple-400',
    Vue: 'bg-emerald-500',
    React: 'bg-cyan-400',
  }
  return colors[props.repo.language || ''] || 'bg-gray-400'
})

function handleSelect() {
  emit('select', props.repo)
}
</script>

<template>
  <div
    @click="handleSelect"
    class="card p-4 cursor-pointer transition-all hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/10"
    :class="{
      'border-primary-500 bg-primary-500/10': selected,
      'border-dark-700': !selected,
    }"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <!-- Repo Name -->
        <div class="flex items-center gap-2 mb-1">
          <h3 class="text-lg font-semibold text-dark-100 truncate">
            {{ repo.name }}
          </h3>
          <span
            v-if="repo.private"
            class="px-2 py-0.5 text-xs font-medium bg-yellow-500/20 text-yellow-400 rounded"
          >
            Private
          </span>
        </div>

        <!-- Full Name -->
        <p class="text-sm text-dark-400 mb-2 truncate">
          {{ repo.full_name }}
        </p>

        <!-- Description -->
        <p v-if="repo.description" class="text-sm text-dark-300 line-clamp-2 mb-3">
          {{ repo.description }}
        </p>

        <!-- Meta Info -->
        <div class="flex items-center gap-4 text-xs text-dark-400">
          <!-- Language -->
          <div v-if="repo.language" class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" :class="languageColor" />
            <span>{{ repo.language }}</span>
          </div>

          <!-- Stars -->
          <div v-if="repo.stargazers_count > 0" class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span>{{ repo.stargazers_count }}</span>
          </div>

          <!-- Updated -->
          <span>{{ formattedDate }}</span>
        </div>
      </div>

      <!-- Selection Indicator -->
      <div
        v-if="selected"
        class="flex-shrink-0 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center"
      >
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
      </div>
    </div>
  </div>
</template>
