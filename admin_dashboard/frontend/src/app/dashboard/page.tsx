'use client'

import { useEffect, useState } from 'react'
import { analyticsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaUsers, FaComments, FaFacebook, FaLine } from 'react-icons/fa'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface Stats {
  total_users: number
  total_conversations: number
  total_messages: number
  total_facebook_comments: number
  line_users: number
  facebook_users: number
  today_messages: number
  today_comments: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await analyticsAPI.getStats()
      setStats(response.data.stats)
    } catch (error) {
      toast.error('ไม่สามารถโหลดสถิติได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    )
  }

  const chartData = [
    {
      name: 'LINE',
      users: stats?.line_users || 0,
    },
    {
      name: 'Facebook',
      users: stats?.facebook_users || 0,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">แดชบอร์ด</h1>
        <p className="text-gray-600 mt-1">ภาพรวมของระบบ Seoulholic Chatbot</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="ผู้ใช้งานทั้งหมด"
          value={stats?.total_users || 0}
          icon={<FaUsers className="w-8 h-8" />}
          color="bg-blue-500"
        />
        <StatCard
          title="บทสนทนา"
          value={stats?.total_conversations || 0}
          icon={<FaComments className="w-8 h-8" />}
          color="bg-green-500"
        />
        <StatCard
          title="ข้อความทั้งหมด"
          value={stats?.total_messages || 0}
          icon={<FaLine className="w-8 h-8" />}
          color="bg-purple-500"
        />
        <StatCard
          title="คอมเมนต์ Facebook"
          value={stats?.total_facebook_comments || 0}
          icon={<FaFacebook className="w-8 h-8" />}
          color="bg-pink-500"
        />
      </div>

      {/* Today's Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">กิจกรรมวันนี้</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">ข้อความวันนี้</p>
            <p className="text-3xl font-bold text-blue-600">{stats?.today_messages || 0}</p>
          </div>
          <div className="p-4 bg-pink-50 rounded-lg">
            <p className="text-sm text-gray-600">คอมเมนต์วันนี้</p>
            <p className="text-3xl font-bold text-pink-600">{stats?.today_comments || 0}</p>
          </div>
        </div>
      </div>

      {/* Platform Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">ผู้ใช้งานตาม Platform</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="users" fill="#ec4899" name="ผู้ใช้งาน" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickAction
          title="ดูผู้ใช้งาน"
          description="จัดการข้อมูลผู้ใช้งาน"
          href="/dashboard/users"
          color="bg-blue-500"
        />
        <QuickAction
          title="ส่งข้อความ"
          description="ส่งข้อความแบบ Broadcast"
          href="/dashboard/broadcast"
          color="bg-green-500"
        />
        <QuickAction
          title="โปรโมชั่น"
          description="จัดการโปรโมชั่น"
          href="/dashboard/promotions"
          color="bg-purple-500"
        />
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-800 mt-2">{value.toLocaleString()}</p>
        </div>
        <div className={`${color} text-white p-4 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function QuickAction({ title, description, href, color }: any) {
  return (
    <a
      href={href}
      className={`${color} text-white p-6 rounded-lg shadow hover:opacity-90 transition-opacity`}
    >
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="text-sm mt-2 opacity-90">{description}</p>
    </a>
  )
}
