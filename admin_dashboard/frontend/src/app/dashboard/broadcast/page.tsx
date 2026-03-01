'use client'

import { useEffect, useState } from 'react'
import { broadcastAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaBullhorn, FaPaperPlane, FaHistory } from 'react-icons/fa'

export default function BroadcastPage() {
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<any[]>([])
  const [formData, setFormData] = useState({
    platform: 'all',
    message: '',
    target_tags: '',
    image_url: '',
  })

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await broadcastAPI.getHistory(10)
      setHistory(response.data.broadcasts || [])
    } catch (error) {
      console.error('Failed to load broadcast history:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.message) {
      toast.error('กรุณากรอกข้อความ')
      return
    }

    setLoading(true)
    try {
      const tags = formData.target_tags
        ? formData.target_tags.split(',').map(t => t.trim()).filter(t => t)
        : undefined

      await broadcastAPI.sendBroadcast({
        platform: formData.platform,
        message: formData.message,
        target_tags: tags,
        image_url: formData.image_url || undefined,
      })

      toast.success('ส่งข้อความสำเร็จ (ยังไม่ได้ implement จริง)')
      setFormData({
        platform: 'all',
        message: '',
        target_tags: '',
        image_url: '',
      })
      fetchHistory()
    } catch (error) {
      toast.error('ไม่สามารถส่งข้อความได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Broadcast Center</h1>
        <p className="text-gray-600 mt-1">ส่งข้อความถึงผู้ใช้งานทั้งหมดหรือกลุ่มเฉพาะ</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Broadcast Form */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-3 bg-primary-100 rounded-lg">
              <FaBullhorn className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-800">สร้างข้อความ</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                เลือก Platform
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'all', label: 'ทั้งหมด', color: 'bg-gray-500' },
                  { value: 'line', label: 'LINE', color: 'bg-green-500' },
                  { value: 'facebook', label: 'Facebook', color: 'bg-blue-500' },
                ].map((platform) => (
                  <button
                    key={platform.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, platform: platform.value })}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      formData.platform === platform.value
                        ? `${platform.color} text-white border-transparent`
                        : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {platform.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ข้อความ <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                rows={6}
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="พิมพ์ข้อความที่ต้องการส่ง..."
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                {formData.message.length} / 500 ตัวอักษร
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags เป้าหมาย (ไม่บังคับ)
              </label>
              <input
                type="text"
                value={formData.target_tags}
                onChange={(e) => setFormData({ ...formData, target_tags: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="vip, interested, คั่นด้วยเครื่องหมายจุลภาค"
              />
              <p className="mt-1 text-sm text-gray-500">
                เว้นว่างไว้เพื่อส่งให้ทุกคน
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                URL รูปภาพ (ไม่บังคับ)
              </label>
              <input
                type="url"
                value={formData.image_url}
                onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={() =>
                  setFormData({
                    platform: 'all',
                    message: '',
                    target_tags: '',
                    image_url: '',
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                ล้างข้อมูล
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex items-center space-x-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                <FaPaperPlane />
                <span>{loading ? 'กำลังส่ง...' : 'ส่งข้อความ'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Stats & History */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">สถิติ</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ส่งไปแล้ววันนี้</span>
                <span className="font-bold text-primary-600">0</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ส่งสำเร็จ</span>
                <span className="font-bold text-green-600">0</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ล้มเหลว</span>
                <span className="font-bold text-red-600">0</span>
              </div>
            </div>
          </div>

          {/* Recent Broadcasts */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <FaHistory className="text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-800">ประวัติล่าสุด</h3>
            </div>
            <div className="space-y-3">
              {history.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">ยังไม่มีประวัติการส่ง</p>
              ) : (
                history.map((item: any, idx: number) => (
                  <div key={idx} className="p-3 border border-gray-200 rounded-lg text-sm">
                    <p className="font-medium text-gray-800">{item.platform}</p>
                    <p className="text-gray-600 truncate">{item.message}</p>
                    <p className="text-xs text-gray-400 mt-1">{item.sent_at}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>⚠️ คำเตือน:</strong> การส่ง broadcast จะส่งข้อความไปยังผู้ใช้งานทั้งหมด
              กรุณาตรวจสอบข้อความให้ดีก่อนส่ง
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
