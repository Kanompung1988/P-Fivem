import os
import re
import sys
import hashlib
import time
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
        
        # In-memory cache for fast response (Senior AI Engineer optimization)
        self.response_cache = {}  # {query_hash: {"response": str, "timestamp": float}}
        self.cache_ttl = 3600  # 1 hour
        self.cache_hits = 0
        self.cache_misses = 0
        
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
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text using hash"""
        return hashlib.md5(text.lower().strip().encode('utf-8')).hexdigest()
    
    def _clean_markdown(self, text: str) -> str:
        """AGGRESSIVE: Remove ALL markdown formatting from response"""
        import re
        
        # Remove bold **text** and __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Remove italic *text* and _text_
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)
        
        # Remove headers ### ## #
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove code blocks ```code```
        text = re.sub(r'```[\w]*\n?(.+?)```', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove horizontal rules
        text = re.sub(r'^(-{3,}|\*{3,}|_{3,})$', '', text, flags=re.MULTILINE)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _get_cached_response(self, query: str) -> Optional[str]:
        """Get cached response if exists and not expired"""
        cache_key = self._get_cache_key(query)
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                self.cache_hits += 1
                return cached["response"]
            else:
                # Expired - remove
                del self.response_cache[cache_key]
        self.cache_misses += 1
        return None
    
    def _set_cached_response(self, query: str, response: str):
        """Cache the response"""
        cache_key = self._get_cache_key(query)
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        # Limit cache size to 1000 entries
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            sorted_keys = sorted(self.response_cache.keys(), 
                               key=lambda k: self.response_cache[k]["timestamp"])
            for key in sorted_keys[:100]:
                del self.response_cache[key]
    
    def _expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms for better RAG matching"""
        # Keyword expansion mapping (Thai clinic terms)
        expansions = {
            'mts': 'MTS PDRN เข็ม ผิว',
            'pdrn': 'PDRN MTS ฟื้นฟู คอลลาเจน',
            'ฟิลเลอร์': 'Filler ฟิลเลอร์ เสริม',
            'filler': 'Filler ฟิลเลอร์ เสริม',
            'ปาก': 'Lip ริมฝีปาก ปาก',
            'lip': 'Lip ปาก ริมฝีปาก',
            'โปร': 'โปรโมชั่น promotion ลดราคา',
            'promotion': 'โปรโมชั่น promotion ลด',
            'คลินิก': 'คลินิก clinic ที่อยู่ สถานที่',
            'clinic': 'คลินิก clinic ที่ตั้ง',
            'จอง': 'จองคิว นัดหมาย ติดต่อ',
            'sculptra': 'Sculptra หน้าเด็ก คอลลาเจน',
            'หน้าเด็ก': 'Sculptra หน้าเด็ก ฟู',
            'ริ้วรอย': 'ริ้วรอย wrinkle anti-aging',
            'ผิวแห้ง': 'ผิวแห้ง dry ชุ่มชื้น',
        }
        
        query_lower = query.lower()
        expanded = query
        
        for keyword, expansion in expansions.items():
            if keyword in query_lower:
                expanded += f" {expansion}"
        
        return expanded

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API (Typhoon ยังไม่รองรับ embeddings)"""
        if not self.client:
            return []
        
        # Typhoon ยังไม่มี embedding API - ข้าม
        if "typhoon" in self.model_name.lower():
            return []
            
        try:
            # Normalize text (better for caching)
            text = text.replace("\n", " ").strip()
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
        Senior AI Engineer optimization: Better context extraction
        """
        # Quick return for simple queries
        if not history or not self.client or len(user_text) < 10:
            return user_text
            
        # Extract last few turns (last 4 pairs) for better context
        conversation_str = ""
        for msg in history[-8:]: 
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            # Skip system prompts or empty content
            if msg["role"] == "system" or not content:
                continue
            # Truncate long messages
            if len(content) > 200:
                content = content[:200] + "..."
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
                if count >= 2: break  # OPTIMIZED: Reduced from 5 to 2 documents for more focused responses
                if score < 0.20: break  # OPTIMIZED: Increased from 0.15 to 0.20 for better relevance
                
                # Avoid dupes
                if is_asking_promo and fb_promo and doc["source"] == "FacebookPromotions":
                    continue
                    
                relevant_docs.append(f"\n--- ข้อมูลเกี่ยวกับ {doc['source']} (Score: {score:.2f}) ---\n{doc['content']}")
                count += 1
                
            return "\n".join(relevant_docs[:2])  # OPTIMIZED: Reduced from 5 to 2
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
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "cache_size": len(self.response_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }

    def get_system_prompt(self) -> str:
        default_prompt = """คุณคือ "น้องโซระ" ที่ปรึกษาความงามมืออาชีพของ Seoulholic Clinic ให้คำปรึกษาแบบเฉพาะบุคคล คิดวิเคราะห์ และแนะนำอย่างชาญฉลาด

🎯 หลักการตอบที่ดี:
• คิดก่อนตอบ - วิเคราะห์ความต้องการและงบประมาณจริงๆ แล้วแนะนำเฉพาะที่เหมาะสม
• ตอบสั้น กระชับ ตรงประเด็น ไม่เกิน 3-4 ประโยคต่อคำถาม
• แนะนำแบบ personalized ตามบริบท ไม่ใช่ยิงรายการทั้งหมด
• ถ้าถามโปรโมชัน ให้วิเคราะห์งบและแนะนำ 1-2 ตัวที่เหมาะสมที่สุด ไม่ใช่บอกทุกโปร
• ถ้าถามว่า "มีอะไรแนะนำบ้าง" ถามกลับเพื่อทำความเข้าใจก่อน เช่น งบเท่าไหร่ ปัญหาอะไร
• พูดเป็นธรรมชาติ ไม่เป็นทางการจนเกินไป ไม่ต้องถามกลับทุกครั้ง
• ลงท้าย "ค่ะ" "นะคะ" อย่างเป็นธรรมชาติ ไม่ซ้ำซาก

⛔ ห้ามเด็ดขาด:
• ห้ามใช้ markdown ทุกรูปแบบ: ** __ * _ ## ### ``` [] ()
• ห้ามใช้ bold italic headers links code blocks
• ห้ามตอบยาวเกิน 5 บรรทัด ยกเว้นจำเป็นจริงๆ
• ห้ามยิงข้อมูลทั้งหมดถ้าคนถามแบบกว้างๆ ให้ถามกลับเพื่อทำความเข้าใจ
• ห้ามถามคำถามติดตามถ้าไม่จำเป็น
• ⚠️ ห้ามขอรูปภาพจาก user - ระบบยังไม่รองรับการวิเคราะห์รูป ถ้า user บอกอาการมาให้แนะนำตามอาการที่บอกเท่านั้น ไม่ต้องขอรูป

✅ รูปแบบที่ใช้ได้:
• ข้อความธรรมดา (plain text)
• emoji เบาๆ เช่น ✨ 💡
• bullet • หรือตัวเลข 1. 2. 3.
• URL แบบธรรมดา ไม่ต้อง wrap

📝 ตัวอย่างการตอบที่ดี:
ถาม: งบ 30,000 มีอะไรแนะนำบ้าง
ตอบดี: ถ้างบ 30,000 แนะนำ Sculptra 2 ขวด 20cc ราคา 35,900 ได้เลยค่ะ (ต้องเติมอีกนิดนึง) หรือเลือก Filler ราคาพอดี ทำได้ 2-3 CC ตามส่วนที่อยากเสริมค่ะ สนใจแบบไหนมากกว่ากันคะ?

ตอบแย่: เรามีโปรโมชั่นมากมาย มี Sculptra, Filler, Botox, Exion Clear... (ยาวเกินไป ไม่ personalized)

ถาม: ช่วยลดฝ้าได้ไหม
ตอบดี: ได้ค่ะ แนะนำ Exion Clear RF เลย รักษาฝ้า กระ จุดด่างดำ ด้วย Fractional RF ลงลึกถึงชั้นผิว สลายเม็ดสี ผลเห็นได้ชัดค่ะ

ตอบแย่: ได้ค่ะ เรามีหลายบริการเลย มี Exion Clear, Vitamin Drip, ... คุณสนใจแบบไหนคะ? (เสนอมากเกินไป)

ถาม: มีฝ้ามากคะ ช่วยได้ไหม
ตอบดี: แนะนำ Exion Clear RF ค่ะ ช่วยลดฝ้าได้ดี ถ้าอยากคำปรึกษาเฉพาะบุคคล ติดต่อคลินิกโดยตรงได้ที่ Line https://lin.ee/FhWfx5U หรือโทร 099-989-2893 นะคะ

ตอบแย่ (ห้ามทำ): เพื่อให้คุณหมอประเมินได้ดี ช่วยส่งรูปผิวหน้ามาหน่อยได้ไหมคะ? (ห้ามขอรูป!)

ถาม: หลุมสิวมาก ทำยังไงดี
ตอบดี: แนะนำ Signature Skin Reset ค่ะ โปรแกรมรีเซ็ตหลุมสิว ช่วยให้ผิวเรียบเนียน หลุมสิวดูตื้นลง ถ้าอยากปรึกษาเฉพาะเจาะจง แนะนำนัดหมายที่คลินิกค่ะ สนใจจองได้เลยค่ะ

ตอบแย่ (ห้ามทำ): ขอดูรูปหลุมสิวหน่อยได้ไหมคะ เพื่อประเมินว่าต้องทำกี่ครั้ง (ห้ามขอรูป!)

📍 ข้อมูลคลินิก:
Seoulholic Clinic (โซลฮอลิกคลินิก)
ที่ตั้ง: The Zone ซอยลาดพร้าว 94
เวลาทำการ: 12:00-20:00 น. (รับจองล่วงหน้า)
ติดต่อ: Line https://lin.ee/FhWfx5U | Tel 099-989-2893
Facebook: https://www.facebook.com/SeoulholicClinic
แผนที่: https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic
 
💉 บริการหลัก (แนะนำตามความเหมาะสม ไม่ต้องบอกทุกอย่าง):

1. Sculptra (หน้าเด็ก) - กระตุ้นคอลลาเจน ผิวฟูกระชับ ดูเด็กลงแบบธรรมชาติ
   โปร: 2 ขวด 20cc ราคา 35,900 บาท

2. Exion Clear RF - รักษาฝ้า กระ จุดด่างดำ ลงลึกถึงชั้นผิว สลายเม็ดสี

3. Filler (ฟิลเลอร์) - เสริมความสวย เพิ่มมิติใบหน้า (คาง กรอบหน้า แก้ม ปาก ใต้ตา)
   โปร: CC แรก 12,900 บาท | CC ถัดไป 9,999 บาท/cc

4. Lip Filler - เติมปากอิ่มฟู หลายทรง (สายฝอ เกาหลี กระจับ ธรรมชาติ)

5. Mounjaro (ปากกาลดน้ำหนัก) - คุมหิว อิ่มนาน ลดไขมัน

6. Signature Skin Reset - โปรแกรมรีเซ็ตหลุมสิว ผิวเรียบเนียน

7. Botox - โบกรอบหน้า/โบกราม ลิฟต์ กระชับ หน้าเรียว

8. Laser Hair Removal - กำจัดขน 3 พลังงาน

9. Vitamin Drip - ดริปวิตามินผิว (ผิวใส Detox บำรุงตับ)
 
🎨 แนวทางการตอบ:
• คิดก่อนตอบ - วิเคราะห์จริงๆ ว่าลูกค้าต้องการอะไร แล้วแนะนำเฉพาะที่เหมาะสม
• ตอบสั้น ไม่เกิน 3-5 บรรทัด
• ถ้าถามกว้างๆ เช่น "งบ XX มีอะไรบ้าง" ให้คิดแล้วแนะนำ 1-2 ตัวที่คุ้มค่าที่สุด
• ถ้าไม่มีข้อมูล บอกตรงๆ แล้วให้ช่องทางติดต่อ
• ไม่ต้องถามกลับทุกครั้ง ให้เป็นธรรมชาติ
• emoji ใช้น้อยๆ พอดี

💬 ตัวอย่างบทสนทนาที่ดี:

User: งบ 30,000 มีอะไรแนะนำบ้าง
Assistant: ถ้างบ 30,000 แนะนำ Sculptra 2 ขวด ราคา 35,900 ได้เลยค่ะ (เติมอีกนิดนึง) ช่วยกระตุ้นคอลลาเจน ผิวฟูกระชับ ดูเด็กลงแบบธรรมชาติ คุ้มค่าที่สุดเลยค่ะ

หรือถ้าอยากพอดีงบ เลือก Filler ได้ 2-3 CC เสริมคาง หรือกรอบหน้าก็ดูดีค่ะ

User: มีโปร Filler ไหม
Assistant: มีค่ะ CC แรก 12,900 บาท CC ถัดไป 9,999 บาท/cc เสริมได้ทั้งคาง กรอบหน้า แก้ม ปาก ใต้ตาค่ะ

User: สนใจจองคิว
Assistant: จองได้เลยค่ะ
Line https://lin.ee/FhWfx5U
Tel 099-989-2893

User: คลินิกอยู่ไหน
Assistant: The Zone ซอยลาดพร้าว 94 ค่ะ มีที่จอดรถสะดวกเลย
แผนที่ https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic

User: ช่วยลดฝ้าได้ไหม
Assistant: ได้ค่ะ แนะนำ Exion Clear RF เลย รักษาฝ้า กระ จุดด่างดำ ด้วย Fractional RF ลงลึกถึงชั้นผิว สลายเม็ดสี ผลเห็นได้ชัดค่ะ"""

        return _get_env("SYSTEM_PROMPT", default_prompt) or default_prompt

    def chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, use_cache: bool = True) -> Iterable[str]:
        """OPTIMIZED: Wrapper for calling OpenAI Chat Completion with caching and markdown removal"""
        if not self.client:
            yield "(Error: AI Service not initialized with API Key)"
            return
        
        # Check cache first (only for non-stream, single user message)
        if use_cache and not stream and len(messages) >= 2:
            user_msg = messages[-1].get("content", "")
            if user_msg:
                cached = self._get_cached_response(user_msg)
                if cached:
                    yield cached
                    return

        try:
            if stream:
                stream_resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True,
                    temperature=0.5,
                    max_tokens=200,  # AGGRESSIVE: Reduced from 300 to 200 for shorter responses
                )
                full_response = ""
                for event in stream_resp:
                    chunk = event.choices[0].delta.content
                    if chunk:
                        full_response += chunk
                        yield chunk
                # Clean markdown and cache
                full_response = self._clean_markdown(full_response)
                if use_cache and len(messages) >= 2:
                    user_msg = messages[-1].get("content", "")
                    if user_msg:
                        self._set_cached_response(user_msg, full_response)
            else:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=200,  # AGGRESSIVE: Reduced from 300 to 200 for shorter responses
                )
                response = resp.choices[0].message.content or ""
                # AGGRESSIVE: Clean ALL markdown
                response = self._clean_markdown(response)
                # Cache the response
                if use_cache and len(messages) >= 2:
                    user_msg = messages[-1].get("content", "")
                    if user_msg:
                        self._set_cached_response(user_msg, response)
                yield response
        except Exception as e:
            yield f"(Error calling OpenAI: {e})"
