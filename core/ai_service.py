import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterable, Union
import numpy as np
from dotenv import load_dotenv

# Load env variables (Ensure this is called if used outside of main app)
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        # ลองใช้ Typhoon ก่อน ถ้าไม่มีค่อยใช้ OpenAI
        typhoon_key = _get_env("TYPHOON_API_KEY")
        if typhoon_key:
            self.api_key = typhoon_key
            self.base_url = "https://api.opentyphoon.ai/v1"
            self.model_name = _get_env("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct")
            print("[AI] Using Typhoon AI")
        else:
            self.api_key = _get_env("OPENAI_API_KEY")
            self.base_url = _get_env("OPENAI_BASE_URL")
            self.model_name = _get_env("OPENAI_MODEL", "gpt-4o-mini")
            print("[AI] Using OpenAI")
            
        self.client = self._create_openai_client()
        self.knowledge_base = []
        
        # Load knowledge immediately
        self.reload_knowledge_base()
        
        self.initialized = True

    def _create_openai_client(self):
        """Create an OpenAI client if configuration exists; otherwise return None."""
        if not self.api_key:
            return None

        try:
            from openai import OpenAI
            if self.base_url:
                return OpenAI(api_key=self.api_key, base_url=self.base_url)
            return OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"Error creating OpenAI client: {e}")
            return None

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API (Typhoon ยังไม่รองรับ embeddings)"""
        if not self.client:
            return []
        
        # Typhoon ยังไม่มี embedding API - ข้าม
        if "typhoon" in self.model_name.lower():
            return []
            
        try:
            # Normalize text
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
        except Exception as e:
            # Suppress embedding errors for Typhoon
            if "typhoon" not in self.model_name.lower():
                print(f"Embedding error: {e}")
            return []

    def reload_knowledge_base(self):
        """Reloads the knowledge base from disk and updates embeddings."""
        print("Reloading Knowledge Base...")
        self.knowledge_base = self._load_knowledge_base_from_files()
        print(f"Knowledge Base Loaded: {len(self.knowledge_base)} documents.")

    def _load_knowledge_base_from_files(self) -> List[Dict[str, Any]]:
        """Download data from files /data/text"""
        knowledge = []
        # Path to data/text relative to this file core/ai_service.py -> ../data/text
        data_path = Path(__file__).resolve().parents[1] / "data" / "text"
        
        if not data_path.exists():
            return knowledge
        
        for txt_file in data_path.glob("*.txt"):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    doc = {
                        "source": txt_file.stem,
                        "content": content,
                        "embedding": []
                    }
                    
                    # Compute embedding
                    if self.client:
                        doc["embedding"] = self._get_embedding(content)
                        
                    knowledge.append(doc)
            except Exception as e:
                print(f"Error reading file {txt_file}: {e}")
                continue
        
        return knowledge

    def rewrite_query(self, user_text: str, history: List[Dict[str, str]]) -> str:
        """
        Rewrite user query based on conversation history to make it standalone.
        Uses a lightweight model call for speed and cost.
        """
        if not history or not self.client:
            return user_text
            
        # Extract last few turns (e.g., last 3 pairs) to keep context manageable
        # Filter out system prompts or irrelevant messages
        conversation_str = ""
        for msg in history[-6:]: 
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            # Skip system prompts or empty content
            if msg["role"] == "system" or not content:
                continue
            conversation_str += f"{role}: {content}\n"
            
        if not conversation_str.strip():
            return user_text
            
        prompt = f"""Conversation History:
{conversation_str}
User's Follow-up Question: {user_text}

Task: Rephrase the user's follow-up question to be a standalone question that includes necessary context from the history. If the user's question is already standalone or changes the topic completely, return it exactly as is. Do not answer the question.

Standalone Question:"""

        try:
            # Use gpt-3.5-turbo or gpt-4o-mini for speed here
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            rewritten = resp.choices[0].message.content.strip()
            # If model returns empty or quote, fallback
            if not rewritten:
                return user_text
            print(f"Rewritten Query: '{user_text}' -> '{rewritten}'")
            return rewritten
        except Exception as e:
            print(f"Rewrite error: {e}")
            return user_text

    def find_relevant_info(self, user_text: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Find relevant info using Vector Similarity Search with Contextual Rewriting"""
        if not self.knowledge_base:
            return ""
            
        search_query = user_text
        
        # Rewrite query if history is provided
        if history:
            search_query = self.rewrite_query(user_text, history)
            
        # Check if we have embeddings
        has_embeddings = any(len(doc["embedding"]) > 0 for doc in self.knowledge_base)
        
        if not self.client or not has_embeddings:
            # Fallback to simple keyword match (use original text mostly, or rewritten if simple)
            # For keyword match, sometimes rewritten query is better, sometimes worse.
            # Let's use search_query generally.
            query_lower = search_query.lower()
            found = []
            for doc in self.knowledge_base:
                if doc["source"].lower() in query_lower:
                    found.append(f"--- {doc['source']} ---\n{doc['content']}")
            return "\n\n".join(found[:2])
        
        try:
            # 1. Get query embedding
            query_embedding = self._get_embedding(search_query)
            if not query_embedding:
                return ""
                
            # 2. Calculate Cosine Similarity
            results = []
            query_vec = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vec)
            
            if query_norm == 0:
                return ""
                
            for doc in self.knowledge_base:
                if not doc["embedding"]: continue
                
                doc_vec = np.array(doc["embedding"])
                doc_norm = np.linalg.norm(doc_vec)
                
                if doc_norm == 0:
                    score = 0
                else:
                    score = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
                    
                results.append((score, doc))
                
            # Sort by score descending
            results.sort(key=lambda x: x[0], reverse=True)
            
            # 3. Filter and Format Results
            relevant_docs = []
            
            # Special Logic: Promo check (Use original user_text for simple keyword check as it is more direct)
            promo_keywords = ["โปร", "promotion", "ลด", "discount", "ราคา", "price", "โปรโมชั่น"]
            is_asking_promo = any(k in user_text.lower() for k in promo_keywords)
            
            fb_promo = next((doc for doc in self.knowledge_base if doc["source"] == "FacebookPromotions"), None)
            
            if is_asking_promo and fb_promo:
                 relevant_docs.append(f"\n--- โปรโมชั่นล่าสุดจาก Facebook ---\n{fb_promo['content']}")
            
            count = 0
            for score, doc in results:
                if count >= 2: break
                if score < 0.35: break # Confidence threshold
                
                # Avoid dupes
                if is_asking_promo and fb_promo and doc["source"] == "FacebookPromotions":
                    continue
                    
                relevant_docs.append(f"\n--- ข้อมูลเกี่ยวกับ {doc['source']} (Score: {score:.2f}) ---\n{doc['content']}")
                count += 1
                
            return "\n".join(relevant_docs[:2])
        except Exception as e:
            print(f"RAG Error: {e}")
            return ""

    def get_image_for_topic(self, user_text: str) -> Optional[str]:
        """Find relevant image based on topic"""
        user_lower = user_text.lower()
        
        image_map = {
            "sculptra|หน้าเด็ก|biostimulator": "Child.png",
            "ฝ้า|กระ|จุดด่างดำ|exion|clear": "DarkSpots.png",
            "ฟิลเลอร์|filler|เสริมหน้า|คาง(?!มัน)": "Filler.png",
            "ปาก|ริมฝีปาก|lip": "LipFull.png",
            "mounjaro|ปากกา|ลดน้ำหนัก": "Pen.png",
            "หลุมสิว|รีเซ็ตผิว|signature": "SkinReset.png",
            "ดื้อสบู่|รูขุมขน|คอเหี่ยว": "Imfomation1.png",
            "โบท็อกซ์|botox|โบก|กราม|รอบหน้า": "Information2.png"
        }
        
        for pattern, image_name in image_map.items():
            if re.search(pattern, user_lower):
                return image_name
        
        return None

    def get_system_prompt(self) -> str:
        default_prompt = """คุณคือ "น้องโซระ" ผู้เชี่ยวชาญด้านความงามและผิวพรรณของ Seoulholic Clinic ให้คำปรึกษาเกี่ยวกับการดูแลผิว บริการต่างๆ และโปรโมชั่น

วิธีการตอบ:
- พูดคุยแบบธรรมชาติ เหมือนให้คำปรึกษาจริงๆ ไม่ใช่บอท
- ใช้ภาษาไทยสุภาพ ลงท้าย "ค่ะ" หรือ "นะคะ" ตามบริบท
- ให้ข้อมูลที่ตรงประเด็น ไม่ยืดเยื้อ
- ถ้าไม่แน่ใจเรื่องราคาหรือรายละเอียดเฉพาะ แนะนำให้ปรึกษาเพิ่มเติม
- ไม่ต้องถามคำถามติดตามทุกครั้ง ให้เป็นไปตามบริบทการสนทนา

ข้อมูลคลินิก:
- Seoulholic Clinic (โซลฮอลิกคลินิก)
- ที่ตั้ง: The Zone (Town in Town) ซอยลาดพร้าว 94
- เวลาทำการ: 12:00-20:00 น. ทุกวัน (รับจองล่วงหน้า)
- ติดต่อ: Line @seoulholicclinic (https://lin.ee/FhWfx5U) | Tel 099-989-2893
- Facebook: https://www.facebook.com/SeoulholicClinic
- แผนที่: https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic
 
# Brand Information (ข้อมูลคลินิก)
- ชื่อ: Seoulholic Clinic (โซลฮอลิกคลินิก) หรือ SHLC
- สโลแกน: คลินิกความงามสไตล์เกาหลี ดูแลผิวพรรณครบวงจร
- Facebook: https://www.facebook.com/SeoulholicClinic
- ที่ตั้ง: โครงการ The Zone (Town in Town) ซอยลาดพร้าว 94
- เวลาทำการ: เปิดทุกวัน 12:00 - 20:00 น.
- การจอง: รับจองล่วงหน้าเท่านั้น (Walk-in อาจต้องรอคิว)
- ติดต่อ: Line: https://lin.ee/FhWfx5U (@seoulholicclinic) | Tel: 099-989-2893
- แผนที่: https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic
 
# Services & Products (บริการและสินค้าหลัก)
1. **Sculptra (หน้าเด็ก)** - กระตุ้นคอลลาเจนใต้ผิว ผิวฟู กระชับ ดูเด็กลงอย่างเป็นธรรมชาติ
   - โปร: 2 ขวด 20cc เพียง 35,900.- (จากปกติ 47,800.-)

2. **Exion Clear RF** - รักษาฝ้า กระ จุดด่างดำ ด้วย Fractional RF
   - ปล่อยพลังงานลงลึกถึงชั้นผิว สลายเม็ดสี กระตุ้นคอลลาเจน

3. **Filler (ฟิลเลอร์)** - เสริมความสวย เพิ่มมิติใบหน้า
   - โปร (15-31 ม.ค. 2569): CC แรก 12,900.- | CC ถัดไป 9,999.-/cc
   - เสริมได้: คาง กรอบหน้า แก้ม ริมฝีปาก ใต้ตา

4. **Lip Filler (ฟิลเลอร์ปาก)** - เติมปากให้อิ่มฟูตามสไตล์ที่ต้องการ
   - มีหลายทรง: สายฝอ, สายเกาหลี, ทรงกระจับ, ธรรมชาติ

5. **Mounjaro (ปากกาลดน้ำหนัก)** - ควบคุมความอยากอาหาร คุมหิว อิ่มนาน
   - ช่วยลดไขมันและน้ำตาล ปรับพฤติกรรมการกิน

6. **Signature Skin Reset** - โปรแกรมรีเซ็ตหลุมสิวซิกเนเจอร์
   - ผิวเรียบเนียนขึ้น หลุมสิวดูตื้นลง

7. **Botox (โบท็อกซ์)** - โบกรอบหน้า / โบกราม
   - โบกรอบหน้า: ลิฟต์ให้คมขึ้น กระชับ
   - โบกราม: ลดขนาดกล้ามเนื้อ ใบหน้าเรียว

8. **Laser Hair Removal** - กำจัดขน 3 พลังงาน (YAG/Diode/Alexandrite)

9. **Vitamin Drip** - ดริปวิตามินผิว (สูตรผิวใส, Detox, บำรุงตับ)
 
# Response Guidelines (แนวทางการตอบ)
1. ตอบเป็นภาษาไทยสุภาพ ลงท้าย 'ค่ะ' หรือ 'นะคะ' แบบธรรมชาติ ไม่ซ้ำซากจนเกินไป
2. ตอบสั้นกระชับ เข้าประเด็น ไม่ยืดเยื้อหรือเสนอขายมากเกินไป
3. อ้างอิงจากข้อมูลที่มี ถ้าไม่มีข้อมูลให้บอกตรงๆ แล้วแนะนำให้ติดต่อคลินิก
4. ถ้าถามเรื่องราคาหรือโปรโมชั่น ให้ข้อมูลพร้อมแนะนำดูรายละเอียดที่ Facebook: https://www.facebook.com/SeoulholicClinic
5. ถ้าลูกค้าต้องการจองหรือสอบถามเพิ่ม ให้ช่องทางติดต่อ ไม่ต้องถามทุกครั้ง
6. หลีกเลี่ยงการใช้ emoji มากเกินไป ใช้เท่าที่จำเป็นเพื่อความเป็นกันเอง

ดูแผนที่: https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic

# Example Dialogue (ตัวอย่างบทสนทนา)
User: มีโปรโมชั่น Sculptra ไหมคะ
Assistant: มีค่ะ ตอนนี้มีโปร Sculptra หน้าเด็ก 2 ขวด 20cc ราคา 35,900.- (จากปกติ 47,800.-) จำกัด 5 ท่านแรกนะคะ

Sculptra จะช่วยกระตุ้นคอลลาเจนใต้ผิว ทำให้ผิวฟูกระชับดูเด็กลงแบบธรรมชาติค่ะ

ดูโปรอื่นๆ ได้ที่ https://www.facebook.com/SeoulholicClinic

User: สนใจจองคิวค่ะ
Assistant: จองได้เลยค่ะ ติดต่อได้ที่

Line: https://lin.ee/FhWfx5U (@seoulholicclinic)
Tel: 099-989-2893
Facebook: https://www.facebook.com/SeoulholicClinic

User: คลินิกอยู่ที่ไหนคะ
Assistant: อยู่ที่ The Zone (Town in Town) ซอยลาดพร้าว 94 ค่ะ มีที่จอดรถสะดวกเลย"""

        return _get_env("SYSTEM_PROMPT", default_prompt) or default_prompt

    def chat_completion(self, messages: List[Dict[str, str]], stream: bool = False) -> Iterable[str]:
        """Wrapper for calling OpenAI Chat Completion"""
        if not self.client:
            yield "(Error: AI Service not initialized with API Key)"
            return

        try:
            if stream:
                stream_resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True,
                    temperature=0.3,
                )
                for event in stream_resp:
                    chunk = event.choices[0].delta.content
                    if chunk:
                        yield chunk
            else:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.3,
                )
                yield resp.choices[0].message.content or ""
        except Exception as e:
            yield f"(Error calling OpenAI: {e})"
