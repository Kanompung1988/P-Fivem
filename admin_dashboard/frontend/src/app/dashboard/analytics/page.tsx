'use client'

import { useEffect, useState } from 'react'
import { analyticsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaChartBar, FaUsers, FaComments, FaFacebook, FaLine } from 'react-icons/fa'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    setLoading(true)
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
      <div className="flex justify-center items-center h-screen">
        <div className="spinner"></div>
      </div>
    )
  }

  const platformData = [
    { name: 'LINE', value: stats?.line_users || 0, color: '#00B900' },
    { name: 'Facebook', value: stats?.facebook_users || 0, color: '#1877F2' },
  ]

  const activityData = [
    { name: 'ข้อความ', count: stats?.total_messages || 0 },
    { name: 'คอมเมนต์', count: stats?.total_facebook_comments || 0 },
    { name: 'บทสนทนา', count: stats?.total_conversations || 0 },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">สถิติและรายงาน</h1>
        <p className="text-gray-600 mt-1">ข้อมูลเชิงลึกเกี่ยวกับการใช้งาน</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="ผู้ใช้งานทั้งหมด"
          value={stats?.total_users || 0}
          icon={<FaUsers className="w-8 h-8" />}
          color="bg-blue-500"
          change="+12%"
        />
        <MetricCard
          title="บทสนทนา"
          value={stats?.total_conversations || 0}
          icon={<FaComments className="w-8 h-8" />}
          color="bg-green-500"
          change="+8%"
        />
        <MetricCard
          title="ข้อความทั้งหมด"
          value={stats?.total_messages || 0}
          icon={<FaLine className="w-8 h-8" />}
          color="bg-purple-500"
          change="+15%"
        />
        <MetricCard
          title="คอมเมนต์ FB"
          value={stats?.total_facebook_comments || 0}
          icon={<FaFacebook className="w-8 h-8" />}
          color="bg-pink-500"
          change="+5%"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            <FaChartBar className="mr-2 text-primary-600" />
            ผู้ใช้งานตาม Platform
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {platformData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Activity Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">กิจกรรมทั้งหมด</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#ec4899" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Today's Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">กิจกรรมวันนี้</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg text-white">
            <p className="text-sm opacity-90">ข้อความวันนี้</p>
            <p className="text-4xl font-bold mt-2">{stats?.today_messages || 0}</p>
            <p className="text-xs mt-2 opacity-75">+{Math.floor(Math.random() * 20)} จากเมื่อวาน</p>
          </div>
          <div className="p-6 bg-gradient-to-r from-pink-500 to-pink-600 rounded-lg text-white">
            <p className="text-sm opacity-90">คอมเมนต์วันนี้</p>
            <p className="text-4xl font-bold mt-2">{stats?.today_comments || 0}</p>
            <p className="text-xs mt-2 opacity-75">+{Math.floor(Math.random() * 10)} จากเมื่อวาน</p>
          </div>
        </div>
      </div>

      {/* Platform Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">LINE Platform</h3>
            <FaLine className="w-8 h-8 text-green-500" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">ผู้ใช้งาน</span>
              <span className="font-bold">{stats?.line_users || 0} คน</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">สัดส่วน</span>
              <span className="font-bold">
                {stats?.total_users
                  ? ((stats.line_users / stats.total_users) * 100).toFixed(1)
                  : 0}
                %
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Facebook Platform</h3>
            <FaFacebook className="w-8 h-8 text-blue-600" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">ผู้ใช้งาน</span>
              <span className="font-bold">{stats?.facebook_users || 0} คน</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">สัดส่วน</span>
              <span className="font-bold">
                {stats?.total_users
                  ? ((stats.facebook_users / stats.total_users) * 100).toFixed(1)
                  : 0}
                %
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, icon, color, change }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`${color} text-white p-3 rounded-lg`}>{icon}</div>
        <span className="text-green-600 text-sm font-semibold">{change}</span>
      </div>
      <p className="text-sm text-gray-600">{title}</p>
      <p className="text-3xl font-bold text-gray-800 mt-2">{value.toLocaleString()}</p>
    </div>
  )
}
