import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionStore } from '../stores/session'

export function useSession() {
  const router = useRouter()
  const route = useRoute()
  const store = useSessionStore()

  const sessionId = computed(() => route.params.sessionId as string | undefined)

  async function initSession() {
    if (sessionId.value && sessionId.value !== store.sessionId) {
      await store.loadSession(sessionId.value)
    }
  }

  function navigateToPhase(phase: string) {
    if (!store.sessionId) return

    const routes: Record<string, string> = {
      idea_submitted: 'config',
      configured: 'questions',
      clarifying: 'questions',
      debating: 'debate',
      drafting: 'judge',
      judging: 'judge',
      completed: 'results',
    }

    const routeName = routes[phase]
    if (routeName) {
      router.push({ name: routeName, params: { sessionId: store.sessionId } })
    }
  }

  async function startNewSession(idea: string) {
    const id = await store.createSession()
    await store.submitIdea(idea)
    router.push({ name: 'config', params: { sessionId: id } })
  }

  return {
    sessionId,
    store,
    initSession,
    navigateToPhase,
    startNewSession,
  }
}
