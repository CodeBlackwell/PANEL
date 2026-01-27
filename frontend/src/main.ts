import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Views
import LandingView from './views/LandingView.vue'
import ConfigView from './views/ConfigView.vue'
import QuestionsView from './views/QuestionsView.vue'
import DebateView from './views/DebateView.vue'
import JudgeView from './views/JudgeView.vue'
import ResultsView from './views/ResultsView.vue'
import LoginView from './views/LoginView.vue'
import AuthCallbackView from './views/AuthCallbackView.vue'
import RepoSelectView from './views/RepoSelectView.vue'

// Stores
import { useAuthStore } from './stores/auth'

// Create app and pinia first
const app = createApp(App)
const pinia = createPinia()

// Use pinia before router so stores are available
app.use(pinia)

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/auth/callback', name: 'auth-callback', component: AuthCallbackView },
  { path: '/repos', name: 'repos', component: RepoSelectView, meta: { requiresAuth: true } },
  { path: '/config/:sessionId', name: 'config', component: ConfigView },
  { path: '/questions/:sessionId', name: 'questions', component: QuestionsView },
  { path: '/debate/:sessionId', name: 'debate', component: DebateView },
  { path: '/judge/:sessionId', name: 'judge', component: JudgeView },
  { path: '/results/:sessionId', name: 'results', component: ResultsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for protected routes
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore(pinia)

  // Initialize auth state if needed
  if (!authStore.initialized) {
    await authStore.initialize()
  }

  // Check if route requires auth
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Store intended destination
    localStorage.setItem('auth_redirect', to.fullPath)
    next({ name: 'login' })
  } else {
    next()
  }
})

app.use(router)
app.mount('#app')
