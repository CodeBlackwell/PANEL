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

const routes = [
  { path: '/', name: 'landing', component: LandingView },
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

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
