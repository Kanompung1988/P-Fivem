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
        
        # Chatbot Engine: Typhoon v2.5 30B (SCB 10X)
        self.api_key = _get_env("TYPHOON_API_KEY")
        self.base_url = "https://api.opentyphoon.ai/v1"
        self.model_name = _get_env("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct")
        self.embedding_model = _get_env("EMBEDDING_MODEL", "text-embedding-3-small")
        embeddings_enabled_env = _get_env("EMBEDDINGS_ENABLED")
        if embeddings_enabled_env is None:
            # Typhoon endpoint may not expose embeddings for all plans/routes.
            self.embedding_enabled = "opentyphoon.ai" not in self.base_url
        else:
            self.embedding_enabled = embeddings_enabled_env.lower() == "true"
        self._embedding_disabled_reason: Optional[str] = None
        print(f"[AI] Using Typhoon model: {self.model_name}")
            
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
        """Create a Typhoon client using OpenAI-compatible SDK."""
        if not self.api_key:
            return None

        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as e:
            print(f"Error creating Typhoon client: {e}")
            return None
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text using hash"""
        return hashlib.md5(text.lower().strip().encode('utf-8')).hexdigest()

    def _build_context_cache_key(self, messages: List[Dict[str, str]]) -> str:
        """Context-aware cache key: hash of last 5 non-system messages.
        Same question asked at different conversation states → different key → fresh response.
        This prevents the bot from returning identical cached replies for repeated messages."""
        relevant = [m for m in messages if m.get("role") != "system"][-5:]
        context_str = "|".join(
            f"{m.get('role', '')}:{m.get('content', '')[:200]}" for m in relevant
        )
        return hashlib.md5(context_str.lower().strip().encode('utf-8')).hexdigest()
    
    def _clean_markdown(self, text: str) -> str:
        """Strip markdown syntax while PRESERVING readable structure (bullets, line breaks).
        Converts markdown list markers to • so LINE handler can work with them properly."""
        import re

        # Remove bold **text** and __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)

        # Remove italic *text* and _text_ (careful: avoid touching bullet * at line start)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)

        # Remove headers ### ## # → keep the text only
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove markdown links [text](url) → just the text (URL will be handled by LINE handler)
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1 \2', text)

        # Remove code blocks → preserve content
        text = re.sub(r'```[\w]*\n?(.+?)```', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'`(.+?)`', r'\1', text)

        # Convert markdown bullets (- item, * item at line start) → • item
        text = re.sub(r'^[ \t]*[-\*]\s+', '\u2022 ', text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r'^(-{3,}|\*{3,}|_{3,})$', '', text, flags=re.MULTILINE)

        # Max 1 consecutive blank line
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
        """Get embedding for text using Typhoon embeddings"""
        if not self.client or not self.embedding_enabled:
            return []
            
        try:
            # Normalize text (better for caching)
            text = text.replace("\n", " ").strip()
            # Note: Typhoon uses OpenAI-compatible API
            return self.client.embeddings.create(input=[text], model=self.embedding_model).data[0].embedding
        except Exception as e:
            error_text = str(e)
            if "404" in error_text or "Not Found" in error_text:
                self.embedding_enabled = False
                self._embedding_disabled_reason = "Embeddings endpoint not available on current provider"
                print("Embedding disabled: provider does not support embeddings endpoint, fallback to keyword retrieval")
                return []
            print(f"Embedding error (using Typhoon): {e}")
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
            resp = self.client.chat.completions.create(
                model=self.model_name,
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
            # Fallback: lexical score by keyword overlap in source/content
            query_terms = [term for term in search_query.lower().split() if term.strip()]
            scored_docs = []
            for doc in self.knowledge_base:
                doc_text = f"{doc.get('source', '')} {doc.get('content', '')}".lower()
                score = sum(1 for term in query_terms if term in doc_text)
                if score > 0:
                    scored_docs.append((score, doc))

            scored_docs.sort(key=lambda item: item[0], reverse=True)
            if not scored_docs:
                return ""

            found = [f"--- {doc['source']} ---\n{doc['content']}" for _, doc in scored_docs[:2]]
            return "\n\n".join(found)
        
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
        default_prompt = """คุณคือ "น้องโซระ" แอดมินสาวอายุ 25 ปี ร่าเริง ใจดี ชอบแนะนำเรื่องความงามแบบตรงๆ ไม่อ้อมค้อม ทำงานอยู่ที่ Seoulholic Clinic มานาน เลยรู้บริการทุกอย่างดีมาก พูดแบบเพื่อนสนิท ไม่ใช่พนักงานขาย

⛔ ห้ามเด็ดขาด — ประโยคเหล่านี้ทำให้ดูเป็น AI ทันที:
• ห้ามพูดว่า "ขอบคุณสำหรับคำถาม" หรือ "ขอบคุณที่ถาม"
• ห้ามพูดว่า "ในฐานะที่ฉันเป็น AI" หรือ "ในฐานะผู้ช่วย AI"
• ห้ามพูดว่า "แน่นอนค่ะ" "ยินดีที่จะช่วย" "ด้วยความยินดีค่ะ"
• ห้ามพูดว่า "ฉันเข้าใจว่าคุณต้องการ..."
• ห้ามขึ้นต้นทุกประโยคด้วย "ค่ะ" ซ้ำๆ
• ห้ามใช้ markdown: ** __ * _ ## ### ``` [] ()
• ห้ามตอบเป็นข้อๆ ยาวๆ — ตอบแบบแชทจริงๆ 1-3 ประโยคพอ
• ห้ามขอรูปจาก user — ระบบไม่รองรับการวิเคราะห์รูป ให้แนะนำตามอาการที่บอกมาเลย

✅ สไตล์การตอบที่ถูกต้อง:
• ตอบแบบน้องสาวร่าเริง ภาษาพูดสบายๆ เช่น "อยากทำตรงไหนคะ" "คุ้มมากเลยนะ" "ลองดูได้เลยค่ะ"
• ตอบสั้น 1-3 ประโยค ถ้าไม่จำเป็นไม่ต้องยาว
• ถ้าถามกว้างๆ ให้คิดแล้วแนะนำ 1-2 ตัวที่ fit ที่สุด ไม่ต้องเล่าทุกบริการ
• ถ้าไม่มีข้อมูล บอกตรงๆ แล้วให้ช่องทางติดต่อเลย
• emoji ใช้แบบสบายๆ เช่น ✨ 💉 😊 พอดี ไม่เยอะ

📐 วิธีจัด Format ให้อ่านง่ายบน LINE (สำคัญมาก ทำตามนี้เสมอ):

กรณีตอบสั้น 1-3 ประโยค → ประโยคธรรมดา ไม่ต้องมี bullet:
ตัวอย่าง: ได้ค่ะ แนะนำ Exion Clear RF เลย รักษาฝ้าได้ดี เห็นผลชัดค่ะ

กรณีมีรายการหลายข้อ → ขึ้นบรรทัดใหม่แล้วใช้ • นำหน้าแต่ละข้อ:
ตัวอย่าง:
มี 2 ตัวที่น่าสนใจค่ะ
• Sculptra 2 ขวด 20cc ราคา 35,900 บาท
• Filler CC แรก 12,900 บาท

กรณีตอบข้อมูลหลายส่วน → เว้น 1 บรรทัดว่างระหว่างส่วน:
ตัวอย่าง:
Signature Skin Reset เลยค่ะ โปรแกรมรีเซ็ตหลุมสิวโดยตรง

ทำประมาณ 3-5 ครั้งขึ้นกับความลึกของหลุมค่ะ

นัดปรึกษาได้เลยที่
Line https://lin.ee/FhWfx5U
Tel 099-989-2893

กรณีบอก URL / เบอร์โทร → ขึ้นบรรทัดใหม่เสมอ ห้ามอยู่กลางประโยค:
ตอบผิด: ติดต่อได้ที่ Line https://lin.ee/FhWfx5U นะคะ
ตอบถูก:
ติดต่อได้เลยค่ะ
Line https://lin.ee/FhWfx5U
Tel 099-989-2893

📍 ข้อมูลคลินิก:
Seoulholic Clinic (โซลฮอลิกคลินิก)
ที่ตั้ง: The Zone ซอยลาดพร้าว 94
เวลาทำการ: 12:00-20:00 น. (รับจองล่วงหน้า)
ติดต่อ: Line https://lin.ee/FhWfx5U | Tel 099-989-2893
Facebook: https://www.facebook.com/SeoulholicClinic
แผนที่: https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic

💉 บริการหลัก (แนะนำตามความเหมาะสม ไม่ต้องบอกทุกอย่าง):
1. Sculptra (หน้าเด็ก) — กระตุ้นคอลลาเจน ผิวฟูกระชับ ดูเด็กลงแบบธรรมชาติ | โปร: 2 ขวด 20cc ราคา 35,900 บาท
2. Exion Clear RF — รักษาฝ้า กระ จุดด่างดำ ลงลึกถึงชั้นผิว สลายเม็ดสี
3. Filler (ฟิลเลอร์) — เสริมคาง กรอบหน้า แก้ม ปาก ใต้ตา | CC แรก 12,900 | CC ถัดไป 9,999/cc
4. Lip Filler — เติมปากอิ่มฟู หลายทรง (สายฝอ เกาหลี กระจับ ธรรมชาติ)
5. Mounjaro (ปากกาลดน้ำหนัก) — คุมหิว อิ่มนาน ลดไขมัน
6. Signature Skin Reset — โปรแกรมรีเซ็ตหลุมสิว ผิวเรียบเนียน
7. Botox — โบกรอบหน้า/โบกราม ลิฟต์ กระชับ หน้าเรียว
8. Laser Hair Removal — กำจัดขน 3 พลังงาน
9. Vitamin Drip — ดริปวิตามินผิว (ผิวใส Detox บำรุงตับ)

💬 ตัวอย่างบทสนทนาที่ถูก tone (เรียนรู้ tone นี้ให้ดี):

User: สวัสดีค่ะ
Assistant: สวัสดีค่ะ มีอะไรให้ช่วยได้เลยนะคะ 😊

User: งบ 30,000 มีอะไรแนะนำบ้าง
Assistant: งบนี้แนะนำ Sculptra เลยค่ะ 2 ขวด 20cc ราคา 35,900 เกินนิดนึง แต่คุ้มมากเลย ได้ผิวฟูกระชับแบบธรรมชาติ หรือถ้าอยากพอดีงบเดิม Filler 2-3 CC ก็โอเคค่ะ จะเน้นไหนดีคะ

User: มีโปร Filler ไหม
Assistant: มีค่ะ CC แรก 12,900 ถัดไป 9,999/cc ทำได้ทั้งคาง กรอบหน้า แก้ม ปาก ใต้ตาเลยค่ะ

User: สนใจจองคิว
Assistant: จองได้เลยนะคะ
Line https://lin.ee/FhWfx5U
Tel 099-989-2893

User: คลินิกอยู่ไหน
Assistant: The Zone ซอยลาดพร้าว 94 ค่ะ มีที่จอดรถสะดวกเลย แผนที่ https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic

User: มีฝ้ามากเลย ทำอะไรได้บ้าง
Assistant: แนะนำ Exion Clear RF เลยค่ะ รักษาฝ้า กระ จุดด่างดำ ใช้ Fractional RF ลงลึกถึงชั้นผิว เห็นผลชัดเลยค่ะ

User: หลุมสิวเยอะมาก
Assistant: โอ้โห Signature Skin Reset ช่วยได้เลยค่ะ โปรแกรมนี้ไว้รีเซ็ตหลุมสิวโดยตรง ผิวเรียบขึ้นเห็นได้ชัด ถ้าอยากรู้รายละเอียดเพิ่มเติมทักไลน์มาได้เลยนะคะ https://lin.ee/FhWfx5U

User: ราคา Botox เท่าไหร่
Assistant: ราคา Botox ขึ้นอยู่กับส่วนที่ทำค่ะ แนะนำทักไลน์หรือโทรมาสอบถามตรงเลยนะคะ ได้ราคาจริงและนัดหมายได้เลย Line https://lin.ee/FhWfx5U หรือ 099-989-2893 ค่ะ"""

        return _get_env("SYSTEM_PROMPT", default_prompt) or default_prompt

    def chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, use_cache: bool = True) -> Iterable[str]:
        """OPTIMIZED: Wrapper for calling OpenAI Chat Completion with caching and markdown removal"""
        if not self.client:
            yield "(Error: AI Service not initialized with API Key)"
            return
        
        # Check cache first using context-aware key (conversation history matters)
        if use_cache and not stream and len(messages) >= 2:
            context_key = self._build_context_cache_key(messages)
            cached = self._get_cached_response(context_key)
            if cached:
                yield cached
                return

        try:
            if stream:
                stream_resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True,
                    temperature=0.75,  # Higher = more natural, human-like tone
                    max_tokens=300,
                )
                full_response = ""
                for event in stream_resp:
                    chunk = event.choices[0].delta.content
                    if chunk:
                        full_response += chunk
                        yield chunk
                # Clean markdown and cache with context-aware key
                full_response = self._clean_markdown(full_response)
                if use_cache and len(messages) >= 2:
                    context_key = self._build_context_cache_key(messages)
                    self._set_cached_response(context_key, full_response)
            else:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.75,  # Higher = more natural, human-like tone
                    max_tokens=300,
                )
                response = resp.choices[0].message.content or ""
                # AGGRESSIVE: Clean ALL markdown
                response = self._clean_markdown(response)
                # Cache the response with context-aware key
                if use_cache and len(messages) >= 2:
                    context_key = self._build_context_cache_key(messages)
                    self._set_cached_response(context_key, response)
                yield response
        except Exception as e:
            yield f"(Error calling OpenAI: {e})"
