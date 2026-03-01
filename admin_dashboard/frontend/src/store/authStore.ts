import { create } from 'zustand'

interface AdminUser {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  last_login: string | null
}

interface AuthState {
  user: AdminUser | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: AdminUser) => void
  logout: () => void
  loadFromStorage: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: (token: string, user: AdminUser) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('admin_user', JSON.stringify(user))
    set({ token, user, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('admin_user')
    set({ token: null, user: null, isAuthenticated: false })
  },

  loadFromStorage: () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      const userStr = localStorage.getItem('admin_user')
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr)
          set({ token, user, isAuthenticated: true })
        } catch (e) {
          // Invalid data, clear storage
          localStorage.removeItem('auth_token')
          localStorage.removeItem('admin_user')
        }
      }
    }
  },
}))
