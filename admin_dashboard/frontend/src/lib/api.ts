import axios, { AxiosInstance, AxiosError } from 'axios'
import toast from 'react-hot-toast'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('admin_user')
        window.location.href = '/login'
      }
    } else if (error.response?.status === 403) {
      toast.error('คุณไม่มีสิทธิ์เข้าถึงข้อมูลนี้')
    } else if (error.response?.status === 500) {
      toast.error('เกิดข้อผิดพลาดจากเซิร์ฟเวอร์')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('การเชื่อมต่อหมดเวลา')
    } else if (!error.response) {
      toast.error('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์')
    }
    return Promise.reject(error)
  }
)

// API functions
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/api/admin/auth/login', { username, password }),
  
  getCurrentUser: () =>
    api.get('/api/admin/auth/me'),
}

export const usersAPI = {
  getUsers: (params?: { platform?: string; limit?: number; offset?: number }) =>
    api.get('/api/admin/users', { params }),
  
  updateUserTags: (userId: number, tags: string[]) =>
    api.put(`/api/admin/users/${userId}/tags`, { tags }),
}

export const conversationsAPI = {
  getConversations: (params?: { user_id?: number; platform?: string; limit?: number }) =>
    api.get('/api/admin/conversations', { params }),
  
  getMessages: (conversationId: number, limit?: number) =>
    api.get(`/api/admin/conversations/${conversationId}/messages`, {
      params: { limit },
    }),

  sendMessage: (
    conversationId: number,
    data: { message: string; reply_to_platform?: boolean }
  ) => api.post(`/api/admin/conversations/${conversationId}/reply`, data),
}

export const knowledgeAPI = {
  getKnowledge: (params?: { category?: string; search?: string }) =>
    api.get('/api/admin/knowledge', { params }),
  
  createKnowledge: (data: {
    title: string
    content: string
    category: string
    keywords?: string[]
  }) => api.post('/api/admin/knowledge', data),
  
  reloadKnowledge: () =>
    api.post('/api/admin/knowledge/reload'),
}

export const promotionsAPI = {
  getPromotions: (activeOnly: boolean = true) =>
    api.get('/api/admin/promotions', { params: { active_only: activeOnly } }),
  
  createPromotion: (data: {
    title: string
    description: string
    promotion_type: string
    discount_value?: string
    start_date?: string
    end_date?: string
  }) => api.post('/api/admin/promotions', data),
}

export const analyticsAPI = {
  getStats: () =>
    api.get('/api/admin/analytics/stats'),
  
  getFacebookCommentsAnalytics: (days: number = 7) =>
    api.get('/api/admin/analytics/facebook-comments', { params: { days } }),
}

export const broadcastAPI = {
  sendBroadcast: (data: {
    platform: string
    message: string
    target_tags?: string[]
    image_url?: string
  }) => api.post('/api/admin/broadcast', data),
  
  getHistory: (limit: number = 50) =>
    api.get('/api/admin/broadcast/history', { params: { limit } }),
}

export const adminUsersAPI = {
  createAdmin: (data: {
    username: string
    email: string
    password: string
    role: string
  }) => api.post('/api/admin/admins', data),
}

export default api
