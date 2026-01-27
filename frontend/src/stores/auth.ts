import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  authApi,
  type UserPublic,
  getAuthToken,
  setAuthToken,
  clearAuthToken,
} from '../services/authApi'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserPublic | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const initialized = ref(false)

  // Computed
  const isAuthenticated = computed(() => user.value !== null)
  const username = computed(() => user.value?.username || null)
  const avatarUrl = computed(() => user.value?.avatar_url || null)

  // Actions
  async function initialize(): Promise<void> {
    if (initialized.value) return

    const token = getAuthToken()
    if (token) {
      try {
        isLoading.value = true
        user.value = await authApi.getCurrentUser()
      } catch (e) {
        // Token is invalid or expired
        clearAuthToken()
        user.value = null
      } finally {
        isLoading.value = false
      }
    }
    initialized.value = true
  }

  function loginWithGitHub(): void {
    // Store current path to redirect back after login
    const currentPath = window.location.pathname
    if (currentPath !== '/' && currentPath !== '/login') {
      localStorage.setItem('auth_redirect', currentPath)
    }
    // Redirect to GitHub OAuth
    window.location.href = authApi.getGitHubLoginUrl()
  }

  async function handleCallback(token: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      // Store the token
      setAuthToken(token)

      // Fetch user info
      user.value = await authApi.getCurrentUser()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Authentication failed'
      clearAuthToken()
      user.value = null
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    isLoading.value = true
    try {
      await authApi.logout()
    } finally {
      user.value = null
      isLoading.value = false
    }
  }

  function getRedirectPath(): string {
    const redirect = localStorage.getItem('auth_redirect')
    localStorage.removeItem('auth_redirect')
    return redirect || '/'
  }

  function setError(message: string): void {
    error.value = message
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,
    initialized,
    // Computed
    isAuthenticated,
    username,
    avatarUrl,
    // Actions
    initialize,
    loginWithGitHub,
    handleCallback,
    logout,
    getRedirectPath,
    setError,
    clearError,
  }
})
