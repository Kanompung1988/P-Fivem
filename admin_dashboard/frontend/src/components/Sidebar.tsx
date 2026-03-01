'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  FaHome, FaUsers, FaComments, FaBook, FaTags, 
  FaBullhorn, FaChartBar, FaSignOutAlt 
} from 'react-icons/fa'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'

const menuItems = [
  { name: 'แดชบอร์ด', href: '/dashboard', icon: FaHome },
  { name: 'ผู้ใช้งาน', href: '/dashboard/users', icon: FaUsers },
  { name: 'บทสนทนา', href: '/dashboard/conversations', icon: FaComments },
  { name: 'ฐานความรู้', href: '/dashboard/knowledge', icon: FaBook },
  { name: 'โปรโมชั่น', href: '/dashboard/promotions', icon: FaTags },
  { name: 'ส่งข้อความ', href: '/dashboard/broadcast', icon: FaBullhorn },
  { name: 'สถิติ', href: '/dashboard/analytics', icon: FaChartBar },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary-600">Seoulholic</h1>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
            {user?.username.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-800">{user?.username}</p>
            <p className="text-xs text-gray-500">{user?.role}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Logout Button */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 w-full px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <FaSignOutAlt className="w-5 h-5" />
          <span>ออกจากระบบ</span>
        </button>
      </div>
    </div>
  )
}
