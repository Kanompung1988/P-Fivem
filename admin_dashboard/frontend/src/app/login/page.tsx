'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'
import { FaLock, FaUser } from 'react-icons/fa'

export default function LoginPage() {
  const router = useRouter()
  const login = useAuthStore((state) => state.login)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')

    if (!username || !password) {
      const msg = 'กรุณากรอกข้อมูลให้ครบถ้วน'
      setErrorMessage(msg)
      toast.error(msg)
      return
    }

    setLoading(true)

    try {
      const response = await authAPI.login(username, password)
      const { access_token } = response.data

      // Save token to localStorage FIRST so the interceptor can use it
      localStorage.setItem('auth_token', access_token)

      // Get user info (now the interceptor will include the token)
      let user: any = null
      try {
        const userResponse = await authAPI.getCurrentUser()
        user = userResponse.data
      } catch {
        user = {
          id: 0,
          username,
          email: '',
          role: 'admin',
          is_active: true,
          created_at: new Date().toISOString(),
          last_login: null,
        }
      }

      // Save to store (this also saves to localStorage, which is fine)
      login(access_token, user)

      toast.success(`ยินดีต้อนรับ, ${user.username}!`)
      router.replace('/dashboard')
      setTimeout(() => {
        if (typeof window !== 'undefined' && window.location.pathname === '/login') {
          window.location.href = '/dashboard'
        }
      }, 250)
    } catch (error: any) {
      console.error('Login error:', error)
      if (error.response?.status === 401) {
        const msg = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
        setErrorMessage(msg)
        toast.error(msg)
      } else {
        const msg = 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ (ตรวจสอบ API URL หรือเครือข่าย)'
        setErrorMessage(msg)
        toast.error(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-100 via-purple-50 to-blue-100">
      <div className="w-full max-w-md p-8 space-y-8 bg-white rounded-2xl shadow-2xl">
        {/* Logo/Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary-600">Seoulholic</h1>
          <p className="mt-2 text-lg text-gray-600">Admin Dashboard</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              ชื่อผู้ใช้
            </label>
            <div className="relative mt-1">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <FaUser className="text-gray-400" />
              </div>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="admin"
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              รหัสผ่าน
            </label>
            <div className="relative mt-1">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <FaLock className="text-gray-400" />
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                กำลังเข้าสู่ระบบ...
              </span>
            ) : (
              'เข้าสู่ระบบ'
            )}
          </button>

          {errorMessage && (
            <p className="text-sm text-red-600 text-center font-medium">{errorMessage}</p>
          )}
        </form>

        {/* Footer */}
        <p className="text-xs text-center text-gray-500">
          Seoulholic Multi-Platform Chatbot v2.0
        </p>
      </div>
    </div>
  )
}
