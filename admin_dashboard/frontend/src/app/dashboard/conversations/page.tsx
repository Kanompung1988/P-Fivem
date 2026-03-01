'use client'

import { useEffect, useState } from 'react'
import { conversationsAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { FaComments, FaUser } from 'react-icons/fa'
import { format } from 'date-fns'

interface Message {
  id: number
  role: string
  content: string
  image_url: string | null
  created_at: string
}

interface Conversation {
  id: number
  user_id: number
  platform: string
  started_at: string
  status: string
  messages_count: number
}

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedConv, setSelectedConv] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingMessages, setLoadingMessages] = useState(false)

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    setLoading(true)
    try {
      const response = await conversationsAPI.getConversations({ limit: 50 })
      setConversations(response.data.conversations || [])
    } catch (error) {
      toast.error('ไม่สามารถโหลดบทสนทนาได้')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (convId: number) => {
    setSelectedConv(convId)
    setLoadingMessages(true)
    try {
      const response = await conversationsAPI.getMessages(convId, 100)
      setMessages(response.data.messages || [])
    } catch (error) {
      toast.error('ไม่สามารถโหลดข้อความได้')
      console.error(error)
    } finally {
      setLoadingMessages(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">บทสนทนา</h1>
        <p className="text-gray-600 mt-1">ดูประวัติบทสนทนาทั้งหมด</p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversations List */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 bg-primary-600 text-white">
            <h2 className="text-lg font-semibold">รายการบทสนทนา</h2>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="spinner"></div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-12">
              <FaComments className="mx-auto w-12 h-12 text-gray-400" />
              <p className="mt-4 text-gray-600">ไม่พบบทสนทนา</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => loadMessages(conv.id)}
                  className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                    selectedConv === conv.id ? 'bg-primary-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white">
                        <FaUser />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-800">
                          User #{conv.user_id}
                        </p>
                        <p className="text-xs text-gray-500">{conv.platform}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">
                        {conv.messages_count} ข้อความ
                      </p>
                      <p className="text-xs text-gray-400">
                        {format(new Date(conv.started_at), 'dd/MM HH:mm')}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Messages View */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 bg-gray-100 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">
              {selectedConv ? `บทสนทนา #${selectedConv}` : 'เลือกบทสนทนา'}
            </h2>
          </div>

          {!selectedConv ? (
            <div className="flex items-center justify-center h-[500px]">
              <div className="text-center">
                <FaComments className="mx-auto w-16 h-16 text-gray-300" />
                <p className="mt-4 text-gray-500">เลือกบทสนทนาที่ต้องการดู</p>
              </div>
            </div>
          ) : loadingMessages ? (
            <div className="flex justify-center items-center h-[500px]">
              <div className="spinner"></div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-[500px]">
              <p className="text-gray-500">ไม่พบข้อความ</p>
            </div>
          ) : (
            <div className="p-4 space-y-4 h-[500px] overflow-y-auto">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[70%] px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-gray-200 text-gray-800'
                        : 'bg-primary-600 text-white'
                    }`}
                  >
                    {msg.image_url && (
                      <img src={msg.image_url} alt="" className="max-w-full rounded mb-2" />
                    )}
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-gray-500' : 'text-primary-200'
                      }`}
                    >
                      {msg.created_at ? format(new Date(msg.created_at), 'HH:mm:ss') : ''}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
