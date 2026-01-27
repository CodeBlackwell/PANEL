<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function closeDropdown() {
  showDropdown.value = false
}

async function handleLogout() {
  closeDropdown()
  await authStore.logout()
  router.push('/')
}

function navigateToRepos() {
  closeDropdown()
  router.push('/repos')
}
</script>

<template>
  <div class="relative">
    <!-- Login Button (when not authenticated) -->
    <router-link
      v-if="!authStore.isAuthenticated"
      to="/login"
      class="flex items-center gap-2 px-4 py-2 text-sm text-dark-300 hover:text-dark-100 transition-colors"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
      </svg>
      Sign in
    </router-link>

    <!-- User Avatar (when authenticated) -->
    <div v-else>
      <button
        @click="toggleDropdown"
        class="flex items-center gap-2 p-1 rounded-full hover:bg-dark-800 transition-colors"
      >
        <img
          v-if="authStore.avatarUrl"
          :src="authStore.avatarUrl"
          :alt="authStore.username || 'User'"
          class="w-8 h-8 rounded-full border-2 border-dark-700"
        />
        <div
          v-else
          class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-medium"
        >
          {{ authStore.username?.charAt(0).toUpperCase() || 'U' }}
        </div>
        <svg
          class="w-4 h-4 text-dark-400 transition-transform"
          :class="{ 'rotate-180': showDropdown }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      <!-- Dropdown Menu -->
      <div
        v-if="showDropdown"
        class="absolute right-0 mt-2 w-56 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50"
      >
        <!-- User Info -->
        <div class="px-4 py-3 border-b border-dark-700">
          <p class="text-sm font-medium text-dark-100">{{ authStore.username }}</p>
          <p v-if="authStore.user?.email" class="text-xs text-dark-400 truncate">
            {{ authStore.user.email }}
          </p>
        </div>

        <!-- Menu Items -->
        <div class="py-1">
          <button
            @click="navigateToRepos"
            class="w-full flex items-center gap-3 px-4 py-2 text-sm text-dark-300 hover:bg-dark-700 hover:text-dark-100 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            My Repositories
          </button>
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 px-4 py-2 text-sm text-dark-300 hover:bg-dark-700 hover:text-dark-100 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Sign out
          </button>
        </div>
      </div>

      <!-- Click outside to close -->
      <div
        v-if="showDropdown"
        class="fixed inset-0 z-40"
        @click="closeDropdown"
      />
    </div>
  </div>
</template>
