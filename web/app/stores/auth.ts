import { defineStore } from 'pinia'
import type { AuthUser } from '~/types/api'
import { ApiError } from '~/composables/useApi'

export const useAuthStore = defineStore('auth', {
  // Only the current user's own public profile shape lives here — never a
  // bearer token or session secret. The session itself is an HttpOnly
  // cookie the browser manages; Pinia state resets per SSR request.
  state: () => ({
    user: null as AuthUser | null,
    status: 'idle' as 'idle' | 'loading' | 'ready',
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
  },

  actions: {
    async fetchCurrentUser() {
      const api = useApi()
      this.status = 'loading'
      try {
        this.user = await api<AuthUser>('/accounts/me/')
      } catch (error) {
        if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
          this.user = null
        } else {
          throw error
        }
      } finally {
        this.status = 'ready'
      }
    },

    async ensureCsrfCookie() {
      const api = useApi()
      await api('/accounts/csrf/')
    },

    async login(username: string, password: string) {
      const api = useApi()
      await this.ensureCsrfCookie()
      this.user = await api<AuthUser>('/accounts/login/', { method: 'POST', body: { username, password } })
    },

    async register(username: string, email: string, password: string) {
      const api = useApi()
      await this.ensureCsrfCookie()
      this.user = await api<AuthUser>('/accounts/register/', {
        method: 'POST',
        body: { username, email, password },
      })
    },

    async logout() {
      const api = useApi()
      await api('/accounts/logout/', { method: 'POST' })
      this.user = null
    },
  },
})
