import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import PanelView from './views/PanelView.vue'
import AuthCallbackView from './views/AuthCallbackView.vue'

import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

const routes = [
  { path: '/', name: 'panel', component: PanelView },
  { path: '/auth/callback', name: 'auth-callback', component: AuthCallbackView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore(pinia)
  if (!authStore.initialized) {
    await authStore.initialize()
  }
  next()
})

app.use(router)
app.mount('#app')
