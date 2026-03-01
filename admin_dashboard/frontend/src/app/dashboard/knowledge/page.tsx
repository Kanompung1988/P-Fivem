'use client'

import { useState } from 'react'
import { knowledgeAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaBook, FaSync, FaPlus } from 'react-icons/fa'

export default function KnowledgeBasePage() {
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    keywords: '',
  })

  const handleReload = async () => {
    setLoading(true)
    try {
      await knowledgeAPI.reloadKnowledge()
      toast.success('รีโหลดฐานความรู้สำเร็จ')
    } catch (error) {
      toast.error('ไม่สามารถรีโหลดฐานความรู้ได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title || !formData.content || !formData.category) {
      toast.error('กรุณากรอกข้อมูลให้ครบถ้วน')
      return
    }

    try {
      const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k)
      await knowledgeAPI.createKnowledge({
        title: formData.title,
        content: formData.content,
        category: formData.category,
        keywords,
      })
      toast.success('เพิ่มความรู้สำเร็จ')
      setShowAddForm(false)
      setFormData({ title: '', content: '', category: '', keywords: '' })
    } catch (error) {
      toast.error('ไม่สามารถเพิ่มความรู้ได้')
      console.error(error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">ฐานความรู้</h1>
          <p className="text-gray-600 mt-1">จัดการข้อมูลที่ใช้ในระบบ RAG</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <FaPlus />
            <span>เพิ่มความรู้</span>
          </button>
          <button
            onClick={handleReload}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            <FaSync className={loading ? 'animate-spin' : ''} />
            <span>รีโหลด RAG</span>
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">เพิ่มความรู้ใหม่</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">หัวข้อ</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">หมวดหมู่</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="เช่น services, pricing, location"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">เนื้อหา</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows={6}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  คำสำคัญ (คั่นด้วยเครื่องหมายจุลภาค)
                </label>
                <input
                  type="text"
                  value={formData.keywords}
                  onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="บริการ, ราคา, สถานที่"
                />
              </div>

              <div className="flex justify-end space-x-3">
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
                  บันทึก
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">ไฟล์ทั้งหมด</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">9</p>
            </div>
            <div className="p-4 bg-blue-100 rounded-lg">
              <FaBook className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">ตำแหน่งไฟล์</p>
              <p className="text-sm font-medium text-gray-800 mt-2">data/text/</p>
            </div>
            <div className="p-4 bg-green-100 rounded-lg">
              <FaBook className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">รีโหลดล่าสุด</p>
              <p className="text-sm font-medium text-gray-800 mt-2">เมื่อสักครู่</p>
            </div>
            <div className="p-4 bg-purple-100 rounded-lg">
              <FaSync className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">วิธีจัดการฐานความรู้</h2>
        <div className="space-y-3 text-gray-600">
          <p>1. เพิ่มไฟล์ .txt ลงในโฟลเดอร์ <code className="bg-gray-100 px-2 py-1 rounded">data/text/</code></p>
          <p>2. กด "รีโหลด RAG" เพื่ออัพเดทฐานความรู้</p>
          <p>3. ระบบจะนำข้อมูลใหม่มาใช้ในการตอบคำถามทันที</p>
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-medium text-blue-800">
              💡 หมายเหตุ: ไฟล์ที่รองรับ .txt, .md, .pdf (บางส่วน)
            </p>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">ไฟล์ในระบบ</h2>
        <div className="space-y-2">
          {[
            'Child.txt',
            'DarkSpots.txt',
            'FacebookPromotions.txt',
            'Filler.txt',
            'Infomation1.txt',
            'Information2.txt',
            'LipFull.txt',
            'Pen.txt',
            'SkinReset.txt',
          ].map((file) => (
            <div
              key={file}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
            >
              <div className="flex items-center space-x-3">
                <FaBook className="text-gray-400" />
                <span className="text-sm font-medium text-gray-700">{file}</span>
              </div>
              <span className="text-xs text-gray-500">data/text/{file}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
