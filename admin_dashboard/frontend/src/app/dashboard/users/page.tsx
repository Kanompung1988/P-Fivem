'use client'

import { useEffect, useState } from 'react'
import { usersAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaUser, FaTag, FaFilter } from 'react-icons/fa'
import { format } from 'date-fns'

interface User {
  id: number
  platform: string
  platform_user_id: string
  display_name: string
  profile_pic_url: string
  first_interaction: string
  last_interaction: string
  total_messages: number
  tags: string[]
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all')
  const [editingTags, setEditingTags] = useState<number | null>(null)
  const [newTags, setNewTags] = useState<string>('')

  useEffect(() => {
    fetchUsers()
  }, [selectedPlatform])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params = selectedPlatform !== 'all' ? { platform: selectedPlatform, limit: 100 } : { limit: 100 }
      const response = await usersAPI.getUsers(params)
      setUsers(response.data.users)
    } catch (error) {
      toast.error('ไม่สามารถโหลดข้อมูลผู้ใช้ได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveTags = async (userId: number) => {
    try {
      const tags = newTags.split(',').map(t => t.trim()).filter(t => t)
      await usersAPI.updateUserTags(userId, tags)
      toast.success('บันทึก tags สำเร็จ')
      setEditingTags(null)
      fetchUsers()
    } catch (error) {
      toast.error('ไม่สามารถบันทึก tags ได้')
      console.error(error)
    }
  }

  const getPlatformBadge = (platform: string) => {
    const colors: any = {
      line: 'bg-green-100 text-green-800',
      facebook: 'bg-blue-100 text-blue-800',
      instagram: 'bg-pink-100 text-pink-800',
    }
    return colors[platform] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">ผู้ใช้งาน</h1>
          <p className="text-gray-600 mt-1">จัดการข้อมูลผู้ใช้งานทั้งหมด</p>
        </div>
        <button
          onClick={fetchUsers}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          รีเฟรช
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <FaFilter className="text-gray-500" />
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">ทุก Platform</option>
            <option value="line">LINE</option>
            <option value="facebook">Facebook</option>
            <option value="instagram">Instagram</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="spinner"></div>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <FaUser className="mx-auto w-12 h-12 text-gray-400" />
            <p className="mt-4 text-gray-600">ไม่พบข้อมูลผู้ใช้งาน</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ผู้ใช้งาน
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Platform
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ข้อความ
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    แท็ก
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    เข้าสู่ระบบล่าสุด
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
                            {user.display_name?.charAt(0) || 'U'}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.display_name || 'ไม่ระบุชื่อ'}
                          </div>
                          <div className="text-sm text-gray-500">{user.platform_user_id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPlatformBadge(
                          user.platform
                        )}`}
                      >
                        {user.platform.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.total_messages} ข้อความ
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {editingTags === user.id ? (
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={newTags}
                            onChange={(e) => setNewTags(e.target.value)}
                            placeholder="tag1, tag2"
                            className="px-2 py-1 border border-gray-300 rounded text-sm"
                          />
                          <button
                            onClick={() => handleSaveTags(user.id)}
                            className="px-2 py-1 bg-green-500 text-white text-xs rounded"
                          >
                            บันทึก
                          </button>
                          <button
                            onClick={() => setEditingTags(null)}
                            className="px-2 py-1 bg-gray-500 text-white text-xs rounded"
                          >
                            ยกเลิก
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <div className="flex flex-wrap gap-1">
                            {user.tags && user.tags.length > 0 ? (
                              user.tags.map((tag, i) => (
                                <span
                                  key={i}
                                  className="px-2 py-0.5 bg-purple-100 text-purple-800 text-xs rounded"
                                >
                                  {tag}
                                </span>
                              ))
                            ) : (
                              <span className="text-gray-400 text-xs">ไม่มีแท็ก</span>
                            )}
                          </div>
                          <button
                            onClick={() => {
                              setEditingTags(user.id)
                              setNewTags(user.tags?.join(', ') || '')
                            }}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            <FaTag />
                          </button>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_interaction
                        ? format(new Date(user.last_interaction), 'dd/MM/yyyy HH:mm')
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">สถิติ</h3>
        <p className="text-gray-600">จำนวนผู้ใช้งานทั้งหมด: <span className="font-bold">{users.length}</span> คน</p>
      </div>
    </div>
  )
}
