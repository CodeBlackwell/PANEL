const API_BASE = '/api/v1'

export interface UserPublic {
  id: string
  username: string
  email: string | null
  avatar_url: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserPublic
}

/**
 * Get the stored auth token from localStorage
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('auth_token')
}

/**
 * Set the auth token in localStorage
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('auth_token', token)
}

/**
 * Remove the auth token from localStorage
 */
export function clearAuthToken(): void {
  localStorage.removeItem('auth_token')
}

/**
 * Check if user is authenticated (has valid token)
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}

/**
 * Get auth headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken()
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid - clear it
      clearAuthToken()
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const authApi = {
  /**
   * Get the GitHub login URL - redirects user to GitHub OAuth
   */
  getGitHubLoginUrl(): string {
    return `${API_BASE}/auth/github/login`
  },

  /**
   * Get current authenticated user info
   */
  async getCurrentUser(): Promise<UserPublic> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
    return handleResponse(response)
  },

  /**
   * Logout the current user
   */
  async logout(): Promise<void> {
    const token = getAuthToken()
    if (token) {
      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: {
            ...getAuthHeaders(),
          },
        })
      } catch {
        // Ignore errors during logout
      }
    }
    clearAuthToken()
  },
}
