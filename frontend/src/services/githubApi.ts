import { getAuthHeaders, clearAuthToken } from './authApi'
import type { RepoContext } from './api'

const API_BASE = '/api/v1'

export interface RepoInfo {
  id: number
  name: string
  full_name: string
  description: string | null
  private: boolean
  html_url: string
  default_branch: string
  language: string | null
  stargazers_count: number
  updated_at: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken()
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const githubApi = {
  /**
   * List repositories for the authenticated user
   */
  async listRepos(
    page: number = 1,
    perPage: number = 30,
    sort: string = 'updated'
  ): Promise<RepoInfo[]> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
      sort,
    })

    const response = await fetch(`${API_BASE}/github/repos?${params}`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
    return handleResponse(response)
  },

  /**
   * Get repository context for PRD generation
   */
  async getRepoContext(owner: string, repo: string): Promise<RepoContext> {
    const response = await fetch(`${API_BASE}/github/repos/${owner}/${repo}/context`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
    return handleResponse(response)
  },

  /**
   * Get repository README content
   */
  async getRepoReadme(owner: string, repo: string): Promise<{ content: string }> {
    const response = await fetch(`${API_BASE}/github/repos/${owner}/${repo}/readme`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
    return handleResponse(response)
  },

  /**
   * Get repository file tree
   */
  async getRepoTree(
    owner: string,
    repo: string,
    maxDepth: number = 3
  ): Promise<{ files: string[] }> {
    const params = new URLSearchParams({
      max_depth: maxDepth.toString(),
    })

    const response = await fetch(`${API_BASE}/github/repos/${owner}/${repo}/tree?${params}`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
    return handleResponse(response)
  },
}
