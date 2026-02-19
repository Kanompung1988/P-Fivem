# 🔧 Integration Guide

**Guide for integrating the selected AI model into Seoulholic Clinic LINE Bot**

---

## 📋 Overview

This guide shows how to integrate **Typhoon-v2.5-30B** or **DeepSeek-v3** into the existing LINE Bot system.

### Architecture

```
LINE User → LINE Bot (line_bot/app.py)
                ↓
         Message Handler (line_bot/message_handler.py)
                ↓
         AI Service (core/ai_service.py) ← **INTEGRATE HERE**
                ↓
         RAG Service (core/rag_service.py)
                ↓
         Cache Service (core/cache_service.py)
                ↓
         Return Response to User
```

---

## 🚀 Quick Start

### Option 1: Typhoon-v2.5-30B (Recommended)

```python
# In core/ai_service.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Typhoon API (OpenAI-compatible)
        self.client = OpenAI(
            api_key=os.getenv("TYPHOON_API_KEY"),
            base_url="https://api.opentyphoon.ai/v1"
        )
        self.model = "typhoon-v2.5-30b-a3b-instruct"
        
        # Load optimized prompt
        from modeleval.optimized_prompts import get_prompt
        self.system_prompt = get_prompt("v6_fewshot")
    
    def get_response(self, user_query: str, context: str = "") -> str:
        """
        Get AI response for user query
        
        Args:
            user_query: User's question
            context: RAG context (optional)
        
        Returns:
            AI response text
        """
        # Combine context with query if available
        if context:
            enhanced_query = f"ข้อมูลที่เกี่ยวข้อง:\n{context}\n\nคำถาม: {user_query}"
        else:
            enhanced_query = user_query
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": enhanced_query}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling AI: {e}")
            return "ขออภัยค่ะ ระบบมีปัญหาชั่วคราว กรุณาลองใหม่อีกครั้งหรือติดต่อเจ้าหน้าที่ค่ะ"
```

### Option 2: DeepSeek-v3 (Faster Alternative)

```python
# In core/ai_service.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # DeepSeek API (OpenAI-compatible)
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
        
        # Load optimized prompt
        from modeleval.optimized_prompts import get_prompt
        self.system_prompt = get_prompt("v6_fewshot")
    
    def get_response(self, user_query: str, context: str = "") -> str:
        """Get AI response (same as Typhoon)"""
        # ... same implementation as above ...
```

---

## 🔗 Full Integration Example

### 1. Update `core/ai_service.py`

```python
"""
AI Service - Main AI model interface
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
from .cache_service import CacheService
from .rag_service import RAGService

load_dotenv()


class AIService:
    def __init__(
        self, 
        model_provider: str = "typhoon",  # or "deepseek"
        use_cache: bool = True,
        use_rag: bool = True
    ):
        """
        Initialize AI Service
        
        Args:
            model_provider: "typhoon" or "deepseek"
            use_cache: Enable response caching
            use_rag: Enable RAG context retrieval
        """
        # Model configuration
        if model_provider == "typhoon":
            self.client = OpenAI(
                api_key=os.getenv("TYPHOON_API_KEY"),
                base_url="https://api.opentyphoon.ai/v1"
            )
            self.model = "typhoon-v2.5-30b-a3b-instruct"
        elif model_provider == "deepseek":
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
        else:
            raise ValueError(f"Unknown provider: {model_provider}")
        
        # Load system prompt
        from modeleval.optimized_prompts import get_prompt
        self.system_prompt = get_prompt("v6_fewshot")
        
        # Initialize services
        self.cache = CacheService() if use_cache else None
        self.rag = RAGService() if use_rag else None
        self.use_rag = use_rag
    
    def get_response(self, user_query: str, user_id: str = None) -> dict:
        """
        Get AI response with caching and RAG
        
        Args:
            user_query: User's question
            user_id: User identifier (for cache)
        
        Returns:
            {
                "response": "AI response text",
                "cached": bool,
                "context_used": bool,
                "tokens": int
            }
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(user_query)
            if cached:
                return {
                    "response": cached,
                    "cached": True,
                    "context_used": False,
                    "tokens": 0
                }
        
        # Get RAG context
        context = ""
        context_used = False
        if self.rag and self.use_rag:
            context = self.rag.get_context(user_query)
            context_used = len(context) > 0
        
        # Prepare query
        if context_used:
            enhanced_query = f"""ข้อมูลที่เกี่ยวข้องจากฐานข้อมูล:
{context}

คำถามของลูกค้า: {user_query}

กรุณาตอบโดยอ้างอิงข้อมูลข้างต้นเป็นหลัก"""
        else:
            enhanced_query = user_query
        
        # Call AI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": enhanced_query}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            # Cache the response
            if self.cache:
                self.cache.set(user_query, answer)
            
            return {
                "response": answer,
                "cached": False,
                "context_used": context_used,
                "tokens": tokens
            }
            
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return {
                "response": "ขออภัยค่ะ ระบบมีปัญหาชั่วคราว กรุณาลองใหม่อีกครั้งหรือติดต่อเจ้าหน้าที่ที่ LINE: @seoulholic ค่ะ",
                "cached": False,
                "context_used": False,
                "tokens": 0,
                "error": str(e)
            }
```

### 2. Update `line_bot/message_handler.py`

```python
"""
Message Handler for LINE Bot
"""

from linebot.models import TextSendMessage
from core.ai_service import AIService
from core.input_guard import InputGuard

# Initialize services
ai_service = AIService(model_provider="typhoon", use_cache=True, use_rag=True)
input_guard = InputGuard()


def handle_text_message(event, line_bot_api):
    """Handle incoming text message"""
    user_id = event.source.user_id
    user_message = event.message.text
    
    # Input validation
    if not input_guard.is_safe(user_message):
        reply = "ขออภัยค่ะ ข้อความไม่เหมาะสม กรุณาถามคำถามที่เกี่ยวกับบริการของคลินิกค่ะ"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
        return
    
    # Get AI response
    result = ai_service.get_response(user_message, user_id=user_id)
    
    # Log for monitoring
    print(f"Query: {user_message[:50]}...")
    print(f"Cached: {result['cached']}, RAG: {result['context_used']}, Tokens: {result['tokens']}")
    
    # Reply to user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result['response'])
    )
```

### 3. Update `.env` with API Keys

```bash
# .env file

# LINE Bot
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token

# AI Models
TYPHOON_API_KEY=your_typhoon_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Optional: Fallback
OPENAI_API_KEY=your_openai_key
```

---

## 🧪 Testing Integration

### Local Testing Script

```python
# test_integration.py

from core.ai_service import AIService

def test_ai_service():
    """Test AI service locally"""
    
    # Initialize
    ai = AIService(model_provider="typhoon", use_cache=False, use_rag=True)
    
    # Test queries
    test_queries = [
        "โบท็อกซ์ราคาเท่าไหร่คะ",
        "ทำฟิลเลอร์เจ็บไหม",
        "มีโปรโมชั่นอะไรบ้างคะ",
    ]
    
    print("🧪 Testing AI Service Integration\n")
    
    for query in test_queries:
        print(f"📝 Query: {query}")
        result = ai.get_response(query)
        print(f"✅ Response: {result['response'][:100]}...")
        print(f"   Cached: {result['cached']}, RAG: {result['context_used']}, Tokens: {result['tokens']}\n")

if __name__ == "__main__":
    test_ai_service()
```

Run test:
```bash
python test_integration.py
```

---

## 📊 Monitoring & Logging

### Add Monitoring

```python
# core/monitoring.py

import time
from datetime import datetime
import json

class MonitoringService:
    def __init__(self, log_file="logs/ai_queries.jsonl"):
        self.log_file = log_file
    
    def log_query(self, query, response, metadata):
        """Log query for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:200],  # First 200 chars
            "cached": metadata.get("cached", False),
            "context_used": metadata.get("context_used", False),
            "tokens": metadata.get("tokens", 0),
            "latency_ms": metadata.get("latency_ms", 0),
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
```

### Add to AIService

```python
# In AIService.get_response()

start_time = time.time()

# ... your AI call ...

latency_ms = (time.time() - start_time) * 1000

# Log
if self.monitoring:
    self.monitoring.log_query(
        query=user_query,
        response=answer,
        metadata={
            "cached": False,
            "context_used": context_used,
            "tokens": tokens,
            "latency_ms": latency_ms
        }
    )
```

---

## ⚡ Performance Optimization

### 1. Enable Caching

Cache frequently asked questions to reduce API calls:

```python
# In AIService.__init__
self.cache = CacheService(ttl=3600)  # 1 hour cache
```

### 2. Implement Smart Routing (Advanced)

Route simple queries to cheaper models:

```python
def get_response_with_routing(self, user_query: str):
    """Smart model routing based on query complexity"""
    
    # Classify query complexity (simple heuristic)
    is_simple = any(keyword in user_query.lower() for keyword in [
        "ราคา", "เท่าไหร่", "จองคิว", "เวลา", "ที่อยู่"
    ])
    
    if is_simple:
        # Use cheaper model for simple queries
        model = "gpt-4o-mini"
        base_url = "https://api.openai.com/v1"
    else:
        # Use Typhoon for complex queries
        model = self.model
        base_url = self.base_url
    
    # Make API call with selected model
    # ...
```

### 3. Set Timeouts

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    max_tokens=800,
    temperature=0.7,
    timeout=10.0  # 10 second timeout
)
```

---

## 🚨 Error Handling

### Implement Graceful Fallbacks

```python
def get_response(self, user_query: str):
    """Get response with fallback"""
    
    try:
        # Try primary model (Typhoon)
        return self._call_model(self.primary_client, self.primary_model, user_query)
    
    except Exception as e:
        print(f"Primary model failed: {e}")
        
        try:
            # Fallback to DeepSeek
            return self._call_model(self.fallback_client, self.fallback_model, user_query)
        
        except Exception as e2:
            print(f"Fallback model failed: {e2}")
            
            # Final fallback: generic message
            return {
                "response": "ขออภัยค่ะ ระบบไม่สามารถตอบได้ในขณะนี้ กรุณาติดต่อที่ LINE: @seoulholic หรือโทร 02-xxx-xxxx ค่ะ",
                "error": True
            }
```

---

## ✅ Pre-Launch Checklist

- [ ] API keys configured in `.env`
- [ ] Test AI service with sample queries
- [ ] Verify RAG context retrieval works
- [ ] Test caching functionality  
- [ ] Set up error handling and fallbacks
- [ ] Configure monitoring and logging
- [ ] Test with LINE Bot locally (ngrok)
- [ ] Conduct user acceptance testing
- [ ] Set up alerts for errors/latency
- [ ] Document incident response process

---

## 📞 Troubleshooting

### Issue: API Key Invalid

```
Error: 401 Unauthorized
```

**Solution:** Check API key in `.env` file, verify it's correct

### Issue: Slow Response

```
Latency > 10 seconds
```

**Solution:** 
- Switch to DeepSeek (faster)
- Enable caching
- Reduce `max_tokens`

### Issue: High Cost

```
Monthly bill > expected
```

**Solution:**
- Enable caching (save 50-70%)
- Implement smart routing
- Reduce `max_tokens` to 600

---

## 📚 Additional Resources

- [Typhoon API Docs](https://opentyphoon.ai/docs)
- [DeepSeek API Docs](https://platform.deepseek.com/api-docs)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

**Last Updated:** February 19, 2026  
**Version:** 1.0
