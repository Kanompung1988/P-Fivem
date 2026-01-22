import os
from pathlib import Path
from typing import List, Dict
import sys

import streamlit as st
from dotenv import load_dotenv

# Add parent dir to path to find core module
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.ai_service import AIService


def _demo_fallback_answer(user_text: str) -> str:
    return (
        "(โหมดเดโม: ยังไม่ได้ตั้งค่า OPENAI_API_KEY)\n\n"
        "คุณพิมพ์ว่า: "
        + user_text
        + "\n\n"
        "ตั้งค่า .env ก่อนเพื่อให้เชื่อมโมเดลจริงได้: OPENAI_API_KEY, OPENAI_MODEL (และ OPENAI_BASE_URL ถ้าใช้ endpoint ภายใน)"
    )


def main() -> None:
    # Load .env
    repo_root_env = Path(__file__).resolve().parents[1] / ".env"
    if repo_root_env.exists():
        load_dotenv(dotenv_path=repo_root_env)
    else:
        load_dotenv()

    st.set_page_config(page_title="Seoulholic Clinic Chatbot", page_icon="💖")
    st.title("💖 Seoulholic Clinic - Seoul Bot")

    # Initialize AI Service
    ai_service = AIService()

    with st.sidebar:
        st.subheader("Config")
        st.caption("ตั้งค่าผ่าน ENV/.env")
        st.text_input("Model", value=ai_service.model_name, disabled=True)
        st.text_input("Base URL", value=ai_service.base_url or "", disabled=True)
        st.toggle("Streaming", value=True, disabled=True)
        if not ai_service.api_key:
            st.warning("ยังไม่ได้ตั้งค่า OPENAI_API_KEY (กำลังใช้โหมดเดโม)")
        
        st.divider()
        st.subheader("📱 Facebook Integration")
        
        # ตรวจสอบสถานะ Facebook
        fb_token = os.getenv("FB_ACCESS_TOKEN")
        fb_status = "🟢 เชื่อมต่อแล้ว" if fb_token else "🔴 ยังไม่ได้ตั้งค่า"
        st.caption(f"สถานะ: {fb_status}")
        
        # แสดงข้อมูลการอัปเดตล่าสุด
        fb_promo_file = Path(__file__).resolve().parents[1] / "data" / "text" / "FacebookPromotions.txt"
        if fb_promo_file.exists():
            import os
            modified_time = os.path.getmtime(fb_promo_file)
            from datetime import datetime
            last_update = datetime.fromtimestamp(modified_time)
            st.caption(f"อัปเดตล่าสุด: {last_update.strftime('%d/%m/%Y %H:%M')}")
        else:
            st.caption("ยังไม่มีข้อมูลจาก Facebook")
        
        # ปุ่มอัปเดตข้อมูล
        if st.button("🔄 อัปเดตข้อมูล Facebook", use_container_width=True):
            with st.spinner("กำลังดึงข้อมูลจาก Facebook..."):
                try:
                    sys.path.append(str(Path(__file__).resolve().parents[1] / "facebook_integration"))
                    from auto_updater import FacebookAutoUpdater
                    
                    updater = FacebookAutoUpdater()
                    updater.update_once()
                    
                    # โหลด knowledge base ใหม่
                    ai_service.reload_knowledge_base()
                    st.success("✅ อัปเดตข้อมูลสำเร็จ!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        
        # ลิงก์ Facebook Page
        st.markdown("📲 [ดู Facebook Page](https://www.facebook.com/SeoulholicClinic)")


    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": ai_service.get_system_prompt()},
            {"role": "assistant", "content": "สวัสดีค่ะ 💖 ยินดีต้อนรับสู่ Seoulholic Clinic นะคะ อยากสอบถามเรื่องอะไรคะ?"},
        ]

    # Render chat history (skip system message)
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ตัวอย่างคำถามสำหรับทดสอบ (แสดงตลอดเวลา)
    with st.expander("💡 ตัวอย่างคำถามที่น่าสนใจ", expanded=(len(st.session_state.messages) <= 2)):
        cols = st.columns(4)
        
        example_questions = [
            "มีโปรโมชั่น Sculptra ไหมคะ",
            "อยากรักษาฝ้า กระ จุดด่างดำ",
            "สนใจเติมปากให้อิ่มฟู",
            "บอกเรื่อง Mounjaro หน่อย",
            "ราคาฟิลเลอร์เท่าไหร่คะ",
            "อยากรักษาหลุมสิว",
            "โบท็อกซ์โบกรามกับโบกหน้าต่างกันไหม",
            "คลินิกอยู่ที่ไหนคะ"
        ]
        
        for i, question in enumerate(example_questions[:4]):
            with cols[i]:
                if st.button(question, key=f"example_{i}", use_container_width=True):
                    st.session_state.pending_question = question
                    st.rerun()
        
        # แถวที่สอง
        cols2 = st.columns(4)
        for i, question in enumerate(example_questions[4:8]):
            with cols2[i]:
                if st.button(question, key=f"example_{i+4}", use_container_width=True):
                    st.session_state.pending_question = question
                    st.rerun()

    # ตรวจสอบว่ามีการคลิกตัวอย่างคำถามหรือไม่
    user_text = None
    if "pending_question" in st.session_state and st.session_state.pending_question:
        user_text = st.session_state.pending_question
        st.session_state.pending_question = None  # รีเซ็ต
    
    # รับ input จาก user (แสดงเสมอ)
    user_input = st.chat_input("พิมพ์ข้อความ…")
    if user_input:
        user_text = user_input
    
    # ถ้าไม่มีข้อความใหม่ ให้หยุดตรงนี้
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        if not ai_service.client:
            answer = _demo_fallback_answer(user_text)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            return

        # ค้นหาข้อมูลที่เกี่ยวข้อง (ส่ง history เพื่อทำ query rewriting)
        relevant_info = ai_service.find_relevant_info(user_text, st.session_state.messages)
        
        # ค้นหารูปภาพที่เกี่ยวข้อง
        relevant_image = ai_service.get_image_for_topic(user_text)

        placeholder = st.empty()
        acc = ""

        # Send messages including system prompt.
        messages_to_send: List[Dict[str, str]] = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ("system", "user", "assistant")
        ]
        
        # เพิ่มข้อมูลที่เกี่ยวข้องใน context ถ้ามี
        if relevant_info:
            context_msg = f"CONTEXT (ข้อมูลเพิ่มเติมสำหรับคำถามนี้):\n{relevant_info}\n\nคำถามของลูกค้า: {user_text}"
            messages_to_send[-1] = {"role": "user", "content": context_msg}

        # Call AI Service
        for chunk in ai_service.chat_completion(messages_to_send, stream=True):
            acc += chunk
            placeholder.markdown(acc)
        
        # แสดงข้อความสุดท้าย
        placeholder.markdown(acc)
        
        # ตรวจสอบว่าลูกค้าสนใจจริงจังหรือไม่
        try:
            sys.path.append(str(Path(__file__).resolve().parents[1] / "notifications"))
            from line_notify import LineNotifier, detect_customer_intent
            
            intent = detect_customer_intent(user_text)
            
            if intent:
                # ส่งการแจ้งเตือนไปยังทีมงาน
                notifier = LineNotifier()
                notifier.notify_customer_interest(
                    customer_message=user_text,
                    bot_response=acc,
                    intent_type=intent,
                    conversation_history=st.session_state.messages
                )
                
                # แสดงข้อความให้ลูกค้าทราบ
                notify_message = "\n\n---\n\n✨ **ทีมงานได้รับข้อความของคุณแล้วค่ะ จะติดต่อกลับเร็วๆ นี้นะคะ** 💖"
                acc += notify_message
                placeholder.markdown(acc)
        except Exception as e:
            # ถ้า error ก็ไม่ต้องทำอะไร ให้ chatbot ทำงานปกติ
            pass
        
        # 
        # แสดงรูปภาพถ้ามี (แสดงหลังข้อความ)
        if relevant_image:
            img_path = Path(__file__).resolve().parents[1] / "data" / "img" / relevant_image
            if img_path.exists():
                st.image(str(img_path), use_container_width=True, caption=f"ข้อมูลเพิ่มเติมค่ะ 💖")
                acc += f"\n\n[แสดงรูปภาพ: {relevant_image}]"

        st.session_state.messages.append({"role": "assistant", "content": acc})


if __name__ == "__main__":
    main()
