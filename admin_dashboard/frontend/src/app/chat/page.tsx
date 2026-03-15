'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  FiHome, FiMail, FiCalendar, FiSearch, FiSettings, FiPlus,
  FiStar, FiCheck, FiMoreHorizontal, FiFilter, FiSend,
  FiPaperclip, FiSmile, FiEdit3, FiX
} from 'react-icons/fi'
import { BiMessageSquareDetail, BiUserCircle } from 'react-icons/bi'
import { IoSparklesSharp } from 'react-icons/io5'
import { conversationsAPI } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export default function ChatPlatform() {
  const router = useRouter()
  const { isAuthenticated, loadFromStorage } = useAuthStore()
  const [showAppointment, setShowAppointment] = useState(true);
  const [conversations, setConversations] = useState<any[]>([]);
  const [activeChat, setActiveChat] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState("");

  // Auth guard
  useEffect(() => {
    loadFromStorage()
  }, [loadFromStorage])

  useEffect(() => {
    if (!isAuthenticated) {
      const token = localStorage.getItem('auth_token')
      if (!token) router.replace('/login')
    }
  }, [isAuthenticated, router])

  const handleSendMessage = async () => {
    if (!inputText.trim() || !activeChat) return;

    // Optimistically update
    const newMessage = {
      content: inputText,
      role: 'assistant', // Matches DB model
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMessage]);
    const currentInput = inputText;
    setInputText("");

    try {
      await conversationsAPI.sendMessage(activeChat.id, {
        message: currentInput,
        reply_to_platform: true // Optionally notify the webhook
      });
      // A realtime update would fetch real DB id, but optimistic is visually fine for now
    } catch (e) {
      toast.error('Failed to send message');
    }
  };

  useEffect(() => {
    // Fetch conversations on load
    const fetchConversations = async () => {
      try {
        const res = await conversationsAPI.getConversations();
        setConversations(res.data.conversations || []);
      } catch (e) {
        console.error('Failed to load conversations', e);
      }
    };
    fetchConversations();
    
    // Auto-refresh conversations
    const interval = setInterval(fetchConversations, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Fetch messages when activeChat changes
    if (activeChat) {
      const fetchMessages = async () => {
        try {
          const res = await conversationsAPI.getMessages(activeChat.id);
          setMessages(res.data.messages || []);
        } catch (e) {
          console.error('Failed to load messages', e);
        }
      };
      fetchMessages();

      // Auto-refresh active chat
      const interval = setInterval(fetchMessages, 3000);
      return () => clearInterval(interval);
    } else {
      setMessages([]);
    }
  }, [activeChat]);

  return (
    <div className="flex h-screen bg-[#F5F7F9] text-[#1D1D21] font-sans overflow-hidden">
      
      {/* 1. Left Icon Sidebar */}
      <div className="w-[70px] bg-white border-r border-gray-200 flex flex-col items-center py-4 justify-between h-full z-10 shrink-0">
        <div className="flex flex-col items-center space-y-6">
          <div className="w-10 h-10 bg-black rounded-xl text-white flex items-center justify-center cursor-pointer shadow-sm">
            <FiPlus size={20} />
          </div>
          <button className="text-gray-400 hover:text-black p-2 transition-colors"><FiHome size={22} /></button>
          <button className="text-black bg-gray-100 p-2 rounded-xl"><FiMail size={22} /></button>
          <button className="text-gray-400 hover:text-black p-2 transition-colors"><FiCalendar size={22} /></button>
          <button className="text-gray-400 hover:text-black p-2 transition-colors"><FiSearch size={22} /></button>
        </div>
        
        <div className="flex flex-col items-center space-y-6 mb-4">
          <button className="text-gray-400 hover:text-black p-2 transition-colors"><FiSettings size={22} /></button>
          <div className="w-9 h-9 rounded-full bg-blue-100 overflow-hidden ring-2 ring-white shadow-sm cursor-pointer hover:opacity-80 transition-opacity">
            <img src="https://i.pravatar.cc/150?img=68" alt="Profile" className="w-full h-full object-cover" />
          </div>
        </div>
      </div>

      {/* 2. Inbox Categories / Folders */}
      <div className="w-[240px] bg-white border-r border-gray-100 flex flex-col h-full overflow-y-auto shrink-0 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">
        <div className="p-5 font-bold text-2xl tracking-tight text-gray-900 border-b border-transparent">Inbox</div>
        
        <div className="px-3 space-y-1 text-[13px] font-semibold text-gray-600 mt-2">
          <div className="flex items-center justify-between p-2.5 bg-gray-50 shadow-sm rounded-xl border border-gray-100 text-black cursor-pointer">
            <div className="flex items-center gap-2.5">
              <img src="https://i.pravatar.cc/150?img=68" className="w-5 h-5 rounded-full" />
              <span>Your Inbox</span>
            </div>
            <span className="text-gray-400 text-xs">5</span>
          </div>

          <div className="flex items-center justify-between p-2.5 hover:bg-gray-50 rounded-xl cursor-pointer mt-2 transition-colors">
            <div className="flex items-center gap-2.5"><BiMessageSquareDetail size={18} className="text-gray-400"/><span>All Chat</span></div>
            <span className="text-gray-400 text-xs">5</span>
          </div>
          <div className="flex items-center justify-between p-2.5 hover:bg-gray-50 rounded-xl cursor-pointer transition-colors">
            <div className="flex items-center gap-2.5"><FiStar size={18} className="text-gray-400"/><span>Favorite</span></div>
            <span className="text-gray-400 text-xs">1</span>
          </div>
          <div className="flex items-center justify-between p-2.5 hover:bg-gray-50 rounded-xl cursor-pointer transition-colors">
            <div className="flex items-center gap-2.5"><BiUserCircle size={18} className="text-gray-400"/><span>UnAssign</span></div>
            <span className="text-gray-400 text-xs">2</span>
          </div>
        </div>

        <div className="mt-8 px-5 font-bold text-[11px] text-gray-400 flex justify-between uppercase tracking-wider">
          <span>Team</span> <FiPlus className="cursor-pointer hover:text-black" />
        </div>
        <div className="px-3 mt-2">
           <div className="flex items-center justify-between p-2.5 text-gray-600 hover:bg-gray-50 rounded-xl cursor-pointer text-[13px] font-semibold transition-colors">
             <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> Drive.Dev</div>
             <span className="text-gray-400 text-xs">5</span>
           </div>
        </div>

        <div className="mt-6 px-5 font-bold text-[11px] text-gray-400 uppercase tracking-wider flex justify-between">
          <span>Stage</span> 
        </div>
        <div className="px-3 mt-2 space-y-0.5 text-[13px] font-medium text-gray-600">
          <StageItem color="bg-gray-300" label="มาใหม่" count={1} />
          <StageItem color="bg-blue-500" label="กำลังคุย" count={1} />
          <StageItem color="bg-yellow-400" label="รอนัด" count={4} />
          <StageItem color="bg-green-500" label="นัดแล้ว" count={1} />
          <StageItem color="bg-purple-500" label="ติดตาม" count={6} />
        </div>
      </div>

      {/* 3. Message List */}
      <div className="w-[300px] bg-white border-r border-gray-100 flex flex-col h-full shrink-0">
        <div className="p-5 flex items-center justify-between border-b border-gray-50">
          <div className="font-bold text-xl tracking-tight">Message</div>
          <button className="text-gray-400 hover:text-black transition-colors"><FiFilter size={18}/></button>
        </div>
        
        <div className="flex px-5 py-3 gap-6 font-semibold text-[13px] text-gray-400 border-b border-gray-100">
          <button className="text-black border-b-2 border-black pb-3 -mb-[13px]">All</button>
          <button className="hover:text-black pb-3 -mb-[13px]">Direct</button>
          <button className="hover:text-black pb-3 -mb-[13px]">Unread</button>
        </div>

        <div className="overflow-y-auto flex-1 p-3 space-y-2">
          {conversations.map((conv, i) => (
            <div 
              key={i}
              onClick={() => setActiveChat(conv)}
              className={`p-4 rounded-2xl cursor-pointer transition-shadow border 
                ${activeChat?.id === conv.id 
                  ? 'bg-white border-gray-200 shadow-[0_2px_8px_rgba(0,0,0,0.04)] ring-1 ring-black/5' 
                  : 'bg-transparent hover:bg-gray-50 border-transparent'
                }`}
            >
              <div className="flex justify-between items-start mb-1.5">
                <div className="flex items-center gap-2.5 font-bold text-[15px] text-gray-700">
                  <div className="relative">
                    {conv.user_profile_pic ? (
                      <img src={conv.user_profile_pic} className="w-9 h-9 rounded-full ring-2 ring-pink-100 p-0.5 object-cover" />
                    ) : (
                      <BiUserCircle className="w-9 h-9 text-gray-400" />
                    )}
                    {/* Status dot */}
                    <div className="absolute -bottom-1 -right-1 bg-green-500 w-3 h-3 border-2 border-white rounded-full"></div>
                  </div>
                  <span className="truncate max-w-[120px]">{conv.user_display_name || 'Unknown User'}</span>
                </div>
                <span className="text-[11px] text-gray-400 font-medium whitespace-nowrap">
                  {new Date(conv.started_at || new Date()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </span>
              </div>
              <p className="text-[13px] text-gray-500 truncate mt-1">
                {messages.length > 0 && activeChat?.id === conv.id ? messages[messages.length - 1].content : 'View messages...'}
              </p>
              <div className="mt-3 flex gap-2">
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-[11px] font-semibold">{conv.platform}</span>
                <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-[11px] font-semibold">{conv.status || 'มาใหม่'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Main Chat Area */}
      <div className="flex-1 flex flex-col bg-[#F8FAFC] relative h-full min-w-0">
        {/* Chat Header */}
        <div className="h-[70px] bg-white border-b border-gray-100 flex items-center justify-between px-8 shrink-0 shadow-sm z-10">
          <div className="flex items-center gap-3">
            <h2 className="font-bold text-xl tracking-tight text-gray-800">
              {activeChat ? activeChat.user_display_name : 'Select a conversation'}
            </h2>
            {activeChat && (
              <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-[11px] font-semibold ml-2">
                {activeChat.platform}
              </span>
            )}
          </div>
          <button className="text-gray-300 hover:text-yellow-400 transition-colors"><FiStar size={22}/></button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-8 flex flex-col gap-5">
          
          {/* Sticky Note (mock) */}
          <div className="bg-[#FFF9E6] border border-yellow-200/60 rounded-2xl p-5 shadow-sm relative">
            <div className="flex items-center gap-2 font-bold text-yellow-700 mb-2 text-sm">
               Note
            </div>
            <p className="text-[14px] text-yellow-900/80 leading-relaxed font-medium">
              ลูกค้า sensitive เรื่องราคามาก อย่าพูดก่อนที่เขาจะถาม สามีทำงานต่างประเทศ กลับ 20 มี.ค. อาจรอให้สามีกลับก่อน
            </p>
            <div className="mt-3 text-[12px] text-yellow-600/70 flex items-center gap-3 font-semibold">
              <span>14:02</span>
              <img src="https://i.pravatar.cc/150?img=68" className="w-5 h-5 rounded-full" />
            </div>
            <button className="absolute top-4 right-4 text-[11px] bg-yellow-200/50 hover:bg-yellow-300/50 text-yellow-700 px-3 py-1.5 rounded-lg font-bold transition-colors">
              ยกเลิกปักหมุด ✕
            </button>
          </div>

          <div className="text-center w-full my-6 flex items-center justify-center gap-4">
             <div className="h-px bg-gray-200 flex-1"></div>
             <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">{new Date().toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: 'numeric'})}</span>
             <div className="h-px bg-gray-200 flex-1"></div>
          </div>

          {/* Render Messages from DB */}
          {!activeChat ? (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm font-medium">
              Please select a chat from the sidebar to start messaging.
            </div>
          ) : messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm font-medium">
              No messages yet in this conversation.
            </div>
          ) : (
            messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div key={idx} className={`flex items-end gap-3 max-w-[80%] ${isUser ? '' : 'self-end'}`}>
                  {isUser && (
                    <img 
                      src={activeChat.user_profile_pic || `https://ui-avatars.com/api/?name=${activeChat.user_display_name || 'U'}&background=random`} 
                      className="w-8 h-8 rounded-full mb-5 object-cover" 
                    />
                  )}
                  <div className={`flex flex-col ${isUser ? '' : 'items-end'}`}>
                    <div className={`p-4 shadow-sm inline-block ${
                      isUser 
                        ? 'bg-white border border-gray-100 rounded-2xl rounded-bl-sm' 
                        : 'bg-[#EDEDF4] rounded-2xl rounded-br-sm'
                    }`}>
                      <p className={`text-[14px] leading-relaxed ${isUser ? 'text-gray-700' : 'text-gray-800'} whitespace-pre-wrap`}>
                        {msg.content}
                      </p>
                    </div>
                    <p className={`text-[11px] text-gray-400 mt-1.5 font-medium ${isUser ? 'ml-1' : 'mr-1'}`}>
                      {new Date(msg.created_at || new Date()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </p>
                  </div>
                  {!isUser && (
                    <img src="https://i.pravatar.cc/150?img=68" className="w-8 h-8 rounded-full mb-5 object-cover" />
                  )}
                </div>
              );
            })
          )}

          {/* Interactive Appointment Modal inside Chat (as shown in image) */}
          {showAppointment && (
            <div className="w-[480px] bg-white border border-gray-100 shadow-xl rounded-2xl p-6 relative ml-11 mt-2">
              <button 
                onClick={() => setShowAppointment(false)} 
                className="absolute top-4 right-4 text-gray-400 hover:text-black bg-gray-100 rounded-full p-1"
              >
                <FiX size={16}/>
              </button>
              <h3 className="font-bold text-[15px] mb-1">นัดหมายลูกค้า</h3>
              <p className="text-[12px] text-gray-400 mb-6">นัดหมายออนไลน์</p>
              
              {/* Stepper */}
              <div className="flex justify-between items-center mb-8 px-2 relative">
                 <div className="absolute top-3.5 left-6 right-6 h-[2px] bg-gray-100 z-0"></div>
                 {[
                   {num: 1, label: 'โปรแกรม', active: true},
                   {num: 2, label: 'แพทย์', active: false},
                   {num: 3, label: 'วันที่', active: false},
                   {num: 4, label: 'เวลา', active: false},
                   {num: 5, label: 'ยืนยัน', active: false}
                 ].map((step, idx) => (
                   <div key={idx} className="flex flex-col items-center gap-2 relative z-10">
                     <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold ${step.active ? 'bg-black text-white' : 'bg-white border-2 border-gray-200 text-gray-400'}`}>
                       {step.num}
                     </div>
                     <span className={`text-[11px] font-bold ${step.active ? 'text-black' : 'text-gray-400'}`}>{step.label}</span>
                   </div>
                 ))}
              </div>

              {/* Service Selection Grid */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                {['Consult ฟรี', 'โบท็อกซ์', 'ฟิลเลอร์', 'เลเซอร์หน้าใส', 'ดูดไขมัน', 'ฉีดวิตามิน', 'ลดน้ำหนัก', 'ตรวจสุขภาพ'].map(srv => (
                  <button key={srv} className="py-2.5 px-4 rounded-xl border border-gray-200 text-[13px] font-semibold text-gray-600 hover:border-black hover:text-black transition-colors">
                    {srv}
                  </button>
                ))}
              </div>

            </div>
          )}

        </div>

        {/* Input Area */}
        <div className="p-5 bg-[#F8FAFC]">
          <div className="bg-white border border-gray-200/80 rounded-2xl shadow-sm p-4 flex flex-col focus-within:ring-2 focus-within:ring-black/5 focus-within:border-gray-300 transition-all">
            <input 
              type="text" 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="คุณอยากรู้อะไรเพิ่มเติมหรือไม่..... |" 
              className="w-full text-[14px] outline-none bg-transparent mb-4 placeholder-gray-400 text-gray-800"
            />
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <button className="flex items-center gap-1.5 text-[13px] font-bold text-gray-600 hover:bg-gray-50 px-3 py-2 rounded-xl border border-gray-100 transition-colors">
                  <FiEdit3 size={15}/> Note
                </button>
                <button onClick={() => setShowAppointment(!showAppointment)} className={`flex items-center gap-1.5 text-[13px] font-bold px-3 py-2 rounded-xl border transition-colors ${showAppointment ? 'bg-blue-50 text-blue-600 border-blue-200' : 'text-gray-600 hover:bg-gray-50 border-gray-100'}`}>
                  <FiCalendar size={15}/> นัดหมาย
                </button>
              </div>
              <div className="flex items-center gap-4">
                <button className="text-[13px] font-bold text-purple-600 flex items-center gap-1.5 hover:bg-purple-50 px-3 py-2 rounded-xl transition-colors">
                  <IoSparklesSharp size={15}/> Ai แก้ไขคำ
                </button>
                <button 
                  onClick={handleSendMessage}
                  disabled={!inputText.trim()}
                  className="bg-black hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white text-[14px] font-bold px-5 py-2.5 rounded-xl flex items-center gap-2 transition-transform active:scale-95 shadow-md">
                  Sent <FiSend />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Right Details Panel */}
      <div className="w-[340px] bg-[#FAFAFA] border-l border-gray-200 flex flex-col h-full overflow-y-auto shrink-0 shadow-[-2px_0_10px_rgba(0,0,0,0.01)]">
        
        {/* AI Summary Section */}
        <div className="p-6 bg-white border-b border-gray-100">
          <div className="flex items-center justify-between w-full mb-5">
            <div className="font-bold tracking-tight text-gray-900">Ai Summary</div>
            <button className="bg-black hover:bg-gray-800 text-white px-3 py-1.5 rounded-full text-[11px] font-bold flex items-center gap-1.5 shadow-sm transition-colors">
              สรุปด้วย AI <IoSparklesSharp size={12}/>
            </button>
          </div>
          
          <div className="flex gap-2 mb-6">
            <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-[12px] font-bold">มาใหม่</span>
            <span className="px-3 py-1 bg-yellow-50 text-yellow-800 rounded-lg text-[12px] font-bold border border-yellow-200/50">🤔 กำลังพิจารณา</span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="font-bold text-gray-400 text-[11px] mb-1.5 uppercase tracking-wider">• สนใจ</div>
              <p className="text-gray-800 font-semibold text-[13px] leading-relaxed">ลูกค้าสนใจโบท็อกซ์ และต้องการทราบรายละเอียดราคา</p>
            </div>
            <div>
              <div className="font-bold text-gray-400 text-[11px] mb-1.5 uppercase tracking-wider">• คุยถึง</div>
              <p className="text-gray-500 font-medium text-[13px] leading-relaxed">
                เจ้าหน้าที่เชิญปรึกษาหมอฟรี แต่ลูกค้ายังกังวลเรื่องค่าใช้จ่ายและต้องการยืนยันว่าไม่มีค่าใช้จ่ายซ่อนเร้น
              </p>
            </div>
            <div>
              <div className="font-bold text-gray-400 text-[11px] mb-1.5 uppercase tracking-wider">• Next action</div>
              <p className="text-gray-500 font-medium text-[13px] leading-relaxed">
                ยืนยันว่าปรึกษาฟรีจริงไม่มีค่าใช้จ่าย แต่ระวังอย่ากดดันเรื่องราคา 
                และอาจเสนอช่วงเวลาหลัง 20 มี.ค. เพื่อรอสามีกลับมา
              </p>
            </div>
          </div>
        </div>

        {/* Customer Details Section */}
        <div className="p-6 pb-2">
           <h3 className="font-bold text-[14px] text-gray-800 mb-5">Detail</h3>
           
           <div className="space-y-4">
             <div className="flex items-center justify-between text-[13px]">
               <span className="text-gray-500 font-medium">Customer</span>
               <div className="flex items-center gap-2 font-bold text-gray-800 bg-white border border-gray-100 px-3 py-1.5 rounded-xl shadow-sm">
                 <img src="https://i.pravatar.cc/150?img=5" className="w-5 h-5 rounded-full" />
                 Amily
               </div>
             </div>
             
             <div className="flex items-center justify-between text-[13px]">
               <span className="text-gray-500 font-medium">Stage</span>
               <div className="flex items-center gap-2">
                 <span className="bg-white border border-gray-100 shadow-sm px-3 py-1.5 rounded-xl font-bold flex items-center gap-2 cursor-pointer">
                   มาใหม่ <span className="text-gray-400">⌄</span>
                 </span>
                 <button className="w-8 h-8 flex items-center justify-center text-gray-400 border border-gray-200 border-dashed rounded-full hover:border-black hover:text-black transition-colors"><FiPlus size={16}/></button>
               </div>
             </div>

             <div className="flex items-center justify-between text-[13px]">
               <span className="text-gray-500 font-medium">Assigned</span>
               <div className="flex items-center gap-2">
                 <div className="flex items-center gap-2 font-bold text-gray-800 bg-white border border-gray-100 px-3 py-1.5 rounded-xl shadow-sm">
                   <img src="https://i.pravatar.cc/150?img=12" className="w-5 h-5 rounded-full" />
                   Team Sale
                 </div>
                 <button className="w-8 h-8 flex items-center justify-center text-gray-400 border border-gray-200 border-dashed rounded-full hover:border-black hover:text-black transition-colors"><FiPlus size={16}/></button>
               </div>
             </div>
           </div>
        </div>

        {/* Lead Information Section */}
        <div className="px-6 py-6 border-t border-gray-100 mt-2 bg-white flex-1">
             <div className="flex items-center justify-between font-bold text-[14px] text-gray-800 mb-6 cursor-pointer">
               <span>Lead Information</span>
               <span className="text-gray-400">⌄</span>
             </div>

             <div className="text-[12px] font-bold text-gray-400 mb-3">Lead status</div>
             <div className="flex flex-wrap gap-2 mb-6">
               <span className="px-3.5 py-1.5 bg-black text-white rounded-full text-[12px] font-bold shadow-sm">มาใหม่</span>
               <span className="px-3.5 py-1.5 bg-gray-50 border border-gray-100 text-gray-600 hover:border-gray-300 cursor-pointer transition-colors rounded-full text-[12px] font-bold">สนใจ</span>
               <span className="px-3.5 py-1.5 bg-gray-50 border border-gray-100 text-gray-600 hover:border-gray-300 cursor-pointer transition-colors rounded-full text-[12px] font-bold">กำลังนัด</span>
               <span className="px-3.5 py-1.5 bg-gray-50 border border-gray-100 text-gray-600 hover:border-gray-300 cursor-pointer transition-colors rounded-full text-[12px] font-bold">นัดแล้ว</span>
             </div>

             <div className="text-[12px] font-bold text-gray-400 mb-3 mt-2">ความสนใจ</div>
             <div className="flex flex-wrap gap-2 mb-6">
               <span className="px-3.5 py-1.5 bg-gray-50 border border-gray-100 text-gray-700 rounded-full text-[12px] font-bold">โบท็อกซ์</span>
               <span className="px-3.5 py-1.5 bg-gray-50 border border-gray-100 text-gray-700 rounded-full text-[12px] font-bold">ทำฟัน</span>
               <button className="w-7 h-7 flex items-center justify-center text-gray-400 border border-gray-200 border-dashed rounded-full hover:border-black hover:text-black transition-colors"><FiPlus size={14}/></button>
             </div>
             
             <div className="flex gap-3 mt-4">
                <div className="flex-1 bg-white border border-gray-100 shadow-sm p-3.5 rounded-xl">
                  <div className="text-[11px] font-bold text-gray-400 mb-1">งบประมาณ</div>
                  <div className="font-bold text-[14px] text-gray-800">10,000 +</div>
                </div>
                <div className="flex-[1.8] bg-white border border-gray-100 shadow-sm p-3.5 rounded-xl">
                  <div className="text-[11px] font-bold text-gray-400 mb-1">ข้อกังวล</div>
                  <div className="font-bold text-[14px] text-gray-800 truncate">กังวลเรื่องความปลอดภัย</div>
                </div>
             </div>

        </div>
      </div>
      
    </div>
  )
}

function StageItem({ color, label, count }: { color: string, label: string, count: number }) {
  return (
    <div className="flex items-center justify-between p-2.5 hover:bg-gray-50 rounded-xl cursor-pointer transition-colors border border-transparent hover:border-gray-100">
      <div className="flex items-center gap-3">
        <span className={`w-2 h-2 rounded-full ${color}`}></span>
        <span>{label}</span>
      </div>
      <span className="text-gray-400 text-xs font-bold">{count}</span>
    </div>
  )
}
