import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { githubApi, type RepoInfo } from '../services/githubApi'
import type { RepoContext } from '../services/api'

export const useGitHubStore = defineStore('github', () => {
  // State
  const repos = ref<RepoInfo[]>([])
  const selectedRepo = ref<RepoInfo | null>(null)
  const repoContext = ref<RepoContext | null>(null)
  const isLoading = ref(false)
  const isLoadingContext = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const hasMore = ref(true)
  const searchQuery = ref('')

  // Computed
  const filteredRepos = computed(() => {
    if (!searchQuery.value) return repos.value
    const query = searchQuery.value.toLowerCase()
    return repos.value.filter(
      (repo) =>
        repo.name.toLowerCase().includes(query) ||
        repo.full_name.toLowerCase().includes(query) ||
        repo.description?.toLowerCase().includes(query)
    )
  })

  const hasRepos = computed(() => repos.value.length > 0)

  // Actions
  async function fetchRepos(page: number = 1, reset: boolean = false): Promise<void> {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      const fetchedRepos = await githubApi.listRepos(page, 30, 'updated')

      if (reset) {
        repos.value = fetchedRepos
      } else {
        repos.value = [...repos.value, ...fetchedRepos]
      }

      currentPage.value = page
      hasMore.value = fetchedRepos.length === 30
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch repositories'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function loadMoreRepos(): Promise<void> {
    if (!hasMore.value || isLoading.value) return
    await fetchRepos(currentPage.value + 1)
  }

  async function refreshRepos(): Promise<void> {
    await fetchRepos(1, true)
  }

  async function selectRepo(repo: RepoInfo): Promise<void> {
    selectedRepo.value = repo
    repoContext.value = null
  }

  async function fetchRepoContext(owner: string, repoName: string): Promise<RepoContext> {
    isLoadingContext.value = true
    error.value = null

    try {
      const context = await githubApi.getRepoContext(owner, repoName)
      repoContext.value = context
      return context
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch repository context'
      throw e
    } finally {
      isLoadingContext.value = false
    }
  }

  function setSearchQuery(query: string): void {
    searchQuery.value = query
  }

  function clearSelection(): void {
    selectedRepo.value = null
    repoContext.value = null
  }

  function reset(): void {
    repos.value = []
    selectedRepo.value = null
    repoContext.value = null
    isLoading.value = false
    isLoadingContext.value = false
    error.value = null
    currentPage.value = 1
    hasMore.value = true
    searchQuery.value = ''
  }

  return {
    // State
    repos,
    selectedRepo,
    repoContext,
    isLoading,
    isLoadingContext,
    error,
    currentPage,
    hasMore,
    searchQuery,
    // Computed
    filteredRepos,
    hasRepos,
    // Actions
    fetchRepos,
    loadMoreRepos,
    refreshRepos,
    selectRepo,
    fetchRepoContext,
    setSearchQuery,
    clearSelection,
    reset,
  }
})
