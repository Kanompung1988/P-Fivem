'use client'

import { useEffect, useState } from 'react'
import { promotionsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaTags, FaPlus, FaEdit } from 'react-icons/fa'
import { format } from 'date-fns'

interface Promotion {
  id: number
  title: string
  description: string
  promotion_type: string
  discount_value: string | null
  start_date: string
  end_date: string | null
  is_active: boolean
  created_at: string
}

export default function PromotionsPage() {
  const [promotions, setPromotions] = useState<Promotion[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    promotion_type: 'discount',
    discount_value: '',
    start_date: '',
    end_date: '',
  })

  useEffect(() => {
    fetchPromotions()
  }, [])

  const fetchPromotions = async () => {
    setLoading(true)
    try {
      const response = await promotionsAPI.getPromotions(false)
      setPromotions(response.data.promotions || [])
    } catch (error) {
      toast.error('ไม่สามารถโหลดโปรโมชั่นได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title || !formData.description) {
      toast.error('กรุณากรอกข้อมูลให้ครบถ้วน')
      return
    }

    try {
      await promotionsAPI.createPromotion({
        title: formData.title,
        description: formData.description,
        promotion_type: formData.promotion_type,
        discount_value: formData.discount_value || undefined,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
      })
      toast.success('สร้างโปรโมชั่นสำเร็จ')
      setShowAddForm(false)
      setFormData({
        title: '',
        description: '',
        promotion_type: 'discount',
        discount_value: '',
        start_date: '',
        end_date: '',
      })
      fetchPromotions()
    } catch (error) {
      toast.error('ไม่สามารถสร้างโปรโมชั่นได้')
      console.error(error)
    }
  }

  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
        ใช้งานอยู่
      </span>
    ) : (
      <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-semibold rounded-full">
        ไม่ใช้งาน
      </span>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">โปรโมชั่น</h1>
          <p className="text-gray-600 mt-1">จัดการโปรโมชั่นและส่วนลด</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <FaPlus />
          <span>สร้างโปรโมชั่น</span>
        </button>
      </div>

      {/* Add Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">สร้างโปรโมชั่นใหม่</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">ชื่อโปรโมชั่น</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">รายละเอียด</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">ประเภท</label>
                  <select
                    value={formData.promotion_type}
                    onChange={(e) => setFormData({ ...formData, promotion_type: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="discount">ส่วนลด</option>
                    <option value="bundle">ชุดพิเศษ</option>
                    <option value="freegift">ของแถม</option>
                    <option value="seasonal">ตามฤดูกาล</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    มูลค่าส่วนลด
                  </label>
                  <input
                    type="text"
                    value={formData.discount_value}
                    onChange={(e) => setFormData({ ...formData, discount_value: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="เช่น 20%, 500 บาท"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">วันเริ่มต้น</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">วันสิ้นสุด</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  ยกเลิก
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  สร้างโปรโมชั่น
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Promotions Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="spinner"></div>
        </div>
      ) : promotions.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FaTags className="mx-auto w-16 h-16 text-gray-300" />
          <p className="mt-4 text-gray-600">ยังไม่มีโปรโมชั่น</p>
          <button
            onClick={() => setShowAddForm(true)}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            สร้างโปรโมชั่นแรก
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {promotions.map((promo) => (
            <div key={promo.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800">{promo.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{promo.promotion_type}</p>
                  </div>
                  {getStatusBadge(promo.is_active)}
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{promo.description}</p>

                {promo.discount_value && (
                  <div className="mb-4 p-3 bg-primary-50 rounded-lg">
                    <p className="text-2xl font-bold text-primary-600">
                      {promo.discount_value}
                    </p>
                  </div>
                )}

                <div className="space-y-2 text-xs text-gray-500">
                  {promo.start_date && (
                    <p>
                      เริ่ม: {format(new Date(promo.start_date), 'dd/MM/yyyy')}
                    </p>
                  )}
                  {promo.end_date && (
                    <p>
                      สิ้นสุด: {format(new Date(promo.end_date), 'dd/MM/yyyy')}
                    </p>
                  )}
                </div>

                <button className="mt-4 w-full py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors flex items-center justify-center space-x-2">
                  <FaEdit />
                  <span>แก้ไข</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
