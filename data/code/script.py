#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEOULHOLIC CLINIC SYNTHETIC DATA GENERATOR v3.0
Enterprise-grade synthetic data pipeline for beauty clinic LLM training
Compatible: OpenAI GPT-4o / Google Gemini 1.5 Pro/Flash
Author: Senior AI Engineer
"""

import os
import sys
import json
import time
import random
import asyncio
import logging
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import argparse

# Third-party imports with graceful fallback
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from tqdm.asyncio import tqdm_asyncio
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm_asyncio = None

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('seoulholic_generator.log')
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class DataCategory(Enum):
    IG_POSTS = "ig_posts"
    CUSTOMER_QA = "customer_qa"
    SERVICE_DESCRIPTIONS = "service_descriptions"
    REVIEWS = "reviews"
    CONVERSATIONS = "conversations"


@dataclass
class GenerationConfig:
    """Configuration for data generation"""
    provider: Literal["openai", "gemini"]
    model: str
    temperature: float
    max_tokens: int
    target_total: int
    batch_size: int = 50
    max_retries: int = 3
    retry_delay: float = 2.0
    rate_limit_rpm: int = 60  # Requests per minute
    output_dir: str = "./seoulholic_data"
    
    def validate(self):
        assert self.provider in ["openai", "gemini"], "Invalid provider"
        assert 0 <= self.temperature <= 2, "Temperature out of range"
        assert self.target_total > 0, "Target must be positive"


@dataclass
class GeneratedItem:
    """Base structure for generated data"""
    id: str
    category: str
    content: Dict
    metadata: Dict
    generated_at: str
    model_used: str
    token_usage: Optional[int] = None


# ============================================================================
# PROVIDER ABSTRACTION
# ============================================================================

class LLMProvider(ABC):
    """Abstract base for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, config: GenerationConfig) -> Dict:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4o implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Default, can override
        
    async def generate(self, prompt: str, config: GenerationConfig) -> Dict:
        try:
            response = await self.client.chat.completions.create(
                model=config.model or self.model,
                messages=[
                    {"role": "system", "content": "You are a data generation engine. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return {
                "content": json.loads(content),
                "tokens": response.usage.total_tokens if response.usage else 0,
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def get_model_name(self) -> str:
        return "gpt-4o-mini"


class GeminiProvider(LLMProvider):
    """Google Gemini implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Gemini package not installed. Run: pip install google-generativeai")
        
        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.model = None
        
    def _get_model(self, model_name: str):
        return genai.GenerativeModel(model_name or "gemini-1.5-flash")
    
    async def generate(self, prompt: str, config: GenerationConfig) -> Dict:
        try:
            model = self._get_model(config.model)
            
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config.temperature,
                    max_output_tokens=config.max_tokens,
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return {
                "content": json.loads(text.strip()),
                "tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                "model": config.model or "gemini-1.5-flash"
            }
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    def get_model_name(self) -> str:
        return "gemini-1.5-flash"


# ============================================================================
# PROMPT ENGINEERING
# ============================================================================

class PromptEngine:
    """Enterprise-grade prompt templates"""
    
    BRAND_CONTEXT = """
    Brand: Seoulholic Clinic (Premium Korean Beauty Clinic in Thailand)
    Positioning: Authentic Korean techniques, Korean doctors, affordable luxury, natural results
    Target: 20-45 years old, middle-upper class, beauty-conscious
    Tone: Professional yet friendly, trustworthy, not pushy
    Services: Filler, Botox, Thread lift, Skin boosters, HIFU, Fat reduction
    Price Range: 1,990 - 35,000 THB
    Locations: Emporium, Siam (Bangkok)
    """
    
    TEMPLATES = {
        DataCategory.IG_POSTS: {
            "system": "Generate Instagram marketing content for a Korean beauty clinic",
            "schema": {
                "posts": [
                    {
                        "id": "string",
                        "caption": "string (150-300 chars, with emojis)",
                        "hashtags": ["list of 5-8 hashtags"],
                        "service_type": "filler_cheek/filler_nose/filler_lips/botox/thread/hifu/skin/fat",
                        "price_mentioned": "number or null",
                        "tone": "promotional/educational/testimonial",
                        "engagement_estimate": "high/medium/low"
                    }
                ]
            },
            "examples": [
                "✨ แก้มป่องๆ ดูอ่อนเยาว์ขึ้น 10 ปี! ฟิลเลอร์แก้ม Seoulholic 4,900 บาท 💕 #SeoulholicClinic",
                "ทำไมต้องโบท็อกซ์ที่ Seoulholic? 🧐 แพทย์เกาหลีปรับเองทุกเคส ไม่ใช่พนักงานฉีด!"
            ]
        },
        
        DataCategory.CUSTOMER_QA: {
            "system": "Generate realistic customer service Q&A pairs",
            "schema": {
                "qa_pairs": [
                    {
                        "id": "string",
                        "question": "string (natural Thai, conversational)",
                        "answer": "string (professional, empathetic, with CTA)",
                        "category": "pricing/procedure/safety/booking/comparison/side_effects/location",
                        "urgency": "high/medium/low",
                        "services_mentioned": ["list"],
                        "follow_up_suggested": "boolean"
                    }
                ]
            },
            "personas": [
                "First-time customer, price-sensitive, worried about safety",
                "Returning customer, asking about combo packages",
                "Male customer, interested in jawline contouring",
                "Young student (20-25), limited budget",
                "Working professional (30-40), values convenience"
            ]
        },
        
        DataCategory.SERVICE_DESCRIPTIONS: {
            "system": "Generate detailed service descriptions",
            "schema": {
                "services": [
                    {
                        "id": "string",
                        "name": "string (creative Korean-style naming)",
                        "category": "filler/botox/thread/skin/hifu/fat/laser",
                        "price_thb": "number",
                        "duration_minutes": "number",
                        "description": "string (3-4 sentences, technical but understandable)",
                        "benefits": ["3-4 bullet points"],
                        "suitable_for": "string",
                        "not_suitable_for": "string",
                        "aftercare": "string",
                        "results_duration": "string",
                        "pain_level": "0-10",
                        "downtime_days": "number"
                    }
                ]
            }
        },
        
        DataCategory.REVIEWS: {
            "system": "Generate authentic customer reviews",
            "schema": {
                "reviews": [
                    {
                        "id": "string",
                        "customer_profile": {
                            "age": "number",
                            "gender": "female/male",
                            "occupation": "string",
                            "skin_concern": "string"
                        },
                        "service_received": "string",
                        "rating": "1-5",
                        "content": "string (100-300 chars, natural language)",
                        "pros": ["list"],
                        "cons": ["list or empty"],
                        "price_paid": "number",
                        "would_recommend": "boolean",
                        "photos_shared": "boolean",
                        "verified_purchase": "boolean"
                    }
                ]
            },
            "distribution": {"5_star": 0.65, "4_star": 0.20, "3_star": 0.10, "1_2_star": 0.05}
        },
        
        DataCategory.CONVERSATIONS: {
            "system": "Generate multi-turn LINE chat conversations",
            "schema": {
                "conversations": [
                    {
                        "id": "string",
                        "scenario": "price_inquiry/safety_concern/comparison/urgent_booking/follow_up/objection_handling",
                        "customer_intent": "string",
                        "messages": [
                            {"role": "customer/staff", "text": "string", "timestamp_offset_minutes": "number"}
                        ],
                        "turns": "number",
                        "outcome": "booked/need_time/price_objection/needs_consultation/unresolved",
                        "satisfaction_score": "1-5"
                    }
                ]
            }
        }
    }
    
    @classmethod
    def build_prompt(cls, category: DataCategory, batch_num: int, variation_seed: int) -> str:
        """Build optimized prompt for specific category"""
        template = cls.TEMPLATES[category]
        
        prompt = f"""{cls.BRAND_CONTEXT}

TASK: {template['system']}
TARGET: Generate {50} items for batch #{batch_num}
VARIATION_SEED: {variation_seed} (ensure diversity from previous batches)

OUTPUT_SCHEMA:
{json.dumps(template['schema'], indent=2, ensure_ascii=False)}

REQUIREMENTS:
1. Output MUST be valid JSON matching the schema exactly
2. All content in Thai language (natural, conversational)
3. Include realistic prices in THB
4. Vary tone based on customer persona when applicable
5. No markdown formatting, pure JSON only
6. Ensure each item has unique characteristics
7. Include specific details (numbers, timeframes, locations)

Generate now:"""
        
        return prompt


# ============================================================================
# GENERATION ENGINE
# ============================================================================

class AsyncDataGenerator:
    """High-performance async data generator with rate limiting"""
    
    def __init__(self, provider: LLMProvider, config: GenerationConfig):
        self.provider = provider
        self.config = config
        self.semaphore = asyncio.Semaphore(5)  # Max concurrent requests
        self.rate_limit_delay = 60.0 / config.rate_limit_rpm
        
    async def generate_batch(self, category: DataCategory, batch_num: int) -> List[GeneratedItem]:
        """Generate single batch with retry logic"""
        prompt = PromptEngine.build_prompt(category, batch_num, random.randint(1, 10000))
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.semaphore:
                    result = await self.provider.generate(prompt, self.config)
                    
                    # Parse and validate
                    raw_data = result["content"]
                    items = self._extract_items(raw_data, category)
                    
                    # Enrich metadata
                    generated_items = []
                    for idx, item in enumerate(items):
                        gen_item = GeneratedItem(
                            id=f"{category.value}_{batch_num:03d}_{idx:03d}",
                            category=category.value,
                            content=item,
                            metadata={
                                "batch": batch_num,
                                "variation_seed": random.randint(1, 10000),
                                "validation_status": "pending"
                            },
                            generated_at=datetime.utcnow().isoformat(),
                            model_used=result["model"],
                            token_usage=result.get("tokens")
                        )
                        generated_items.append(gen_item)
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                    
                    return generated_items
                    
            except Exception as e:
                logger.warning(f"Batch {batch_num} attempt {attempt+1} failed: {e}")
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        
        logger.error(f"Batch {batch_num} failed after all retries")
        return []
    
    def _extract_items(self, raw_data: Dict, category: DataCategory) -> List[Dict]:
        """Extract item list from various response formats"""
        if isinstance(raw_data, list):
            return raw_data
        
        # Try common keys
        keys = ["posts", "qa_pairs", "services", "reviews", "conversations", "items", "data"]
        for key in keys:
            if key in raw_data:
                return raw_data[key]
        
        # Fallback: return values of first key if it's a list
        first_val = list(raw_data.values())[0] if raw_data else []
        return first_val if isinstance(first_val, list) else [raw_data]
    
    async def generate_category(self, category: DataCategory, target: int) -> List[GeneratedItem]:
        """Generate full category with progress tracking"""
        num_batches = (target // self.config.batch_size) + 1
        all_items = []
        
        logger.info(f"Starting {category.value}: {target} items in {num_batches} batches")
        
        tasks = [
            self.generate_batch(category, i+1) 
            for i in range(num_batches)
        ]
        
        # Execute with progress bar
        if TQDM_AVAILABLE:
            results = await tqdm_asyncio.gather(*tasks, desc=category.value[:20])
        else:
            results = await asyncio.gather(*tasks)
        
        for batch_items in results:
            all_items.extend(batch_items)
            if len(all_items) >= target:
                break
        
        # Trim and validate
        final_items = all_items[:target]
        logger.info(f"Completed {category.value}: {len(final_items)} items")
        
        return final_items


# ============================================================================
# DATA VALIDATION & EXPORT
# ============================================================================

class DataValidator:
    """Validate and clean generated data"""
    
    @staticmethod
    def validate_item(item: GeneratedItem, category: DataCategory) -> bool:
        """Validate single item structure"""
        try:
            content = item.content
            
            if category == DataCategory.IG_POSTS:
                return all(k in content for k in ["caption", "hashtags", "service_type"])
            elif category == DataCategory.CUSTOMER_QA:
                return all(k in content for k in ["question", "answer", "category"])
            elif category == DataCategory.SERVICE_DESCRIPTIONS:
                return all(k in content for k in ["name", "price_thb", "description"])
            elif category == DataCategory.REVIEWS:
                return all(k in content for k in ["content", "rating", "service_received"])
            elif category == DataCategory.CONVERSATIONS:
                return all(k in content for k in ["messages", "scenario", "outcome"])
            
            return True
        except:
            return False
    
    @staticmethod
    def deduplicate(items: List[GeneratedItem]) -> List[GeneratedItem]:
        """Remove duplicates based on content hash"""
        seen_hashes = set()
        unique = []
        
        for item in items:
            content_str = json.dumps(item.content, sort_keys=True, ensure_ascii=False)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()[:12]
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                item.metadata["content_hash"] = content_hash
                unique.append(item)
        
        return unique


class DataExporter:
    """Export data in multiple formats"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_json(self, items: List[GeneratedItem], filename: str):
        """Export to JSON"""
        data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "count": len(items),
                "categories": list(set(i.category for i in items))
            },
            "data": [asdict(item) for item in items]
        }
        
        path = self.output_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported JSON: {path}")
        return path
    
    def export_training_corpus(self, items: List[GeneratedItem], filename: str):
        """Export plain text for fine-tuning"""
        lines = []
        
        for item in items:
            cat = DataCategory(item.category)
            
            if cat == DataCategory.CUSTOMER_QA:
                qa = item.content
                lines.append(f"Human: {qa.get('question', '')}")
                lines.append(f"Assistant: {qa.get('answer', '')}")
                lines.append("---")
            elif cat == DataCategory.CONVERSATIONS:
                conv = item.content
                for msg in conv.get("messages", []):
                    role = "Human" if msg["role"] == "customer" else "Assistant"
                    lines.append(f"{role}: {msg['text']}")
                lines.append("---")
            elif cat == DataCategory.IG_POSTS:
                cap = item.content.get("caption", "")
                lines.append(f"Caption: {cap}")
                lines.append("---")
        
        path = self.output_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        logger.info(f"Exported corpus: {path}")
        return path
    
    def export_statistics(self, items: List[GeneratedItem]):
        """Generate and export statistics"""
        stats = {
            "total_items": len(items),
            "by_category": {},
            "by_model": {},
            "avg_token_usage": 0,
            "generation_time": datetime.utcnow().isoformat()
        }
        
        token_sum = 0
        token_count = 0
        
        for item in items:
            stats["by_category"][item.category] = stats["by_category"].get(item.category, 0) + 1
            stats["by_model"][item.model_used] = stats["by_model"].get(item.model_used, 0) + 1
            
            if item.token_usage:
                token_sum += item.token_usage
                token_count += 1
        
        if token_count > 0:
            stats["avg_token_usage"] = token_sum / token_count
        
        path = self.output_dir / "statistics.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        return stats


# ============================================================================
# MAIN PIPELINE
# ============================================================================

class SeoulholicPipeline:
    """End-to-end generation pipeline"""
    
    DISTRIBUTION = {
        DataCategory.IG_POSTS: 2000,
        DataCategory.CUSTOMER_QA: 4000,
        DataCategory.SERVICE_DESCRIPTIONS: 2000,
        DataCategory.REVIEWS: 1500,
        DataCategory.CONVERSATIONS: 500
    }
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.provider = self._initialize_provider()
        self.generator = AsyncDataGenerator(self.provider, config)
        self.exporter = DataExporter(config.output_dir)
        self.validator = DataValidator()
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize selected provider"""
        if self.config.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise RuntimeError("OpenAI not available. Install: pip install openai")
            return OpenAIProvider()
        else:
            if not GEMINI_AVAILABLE:
                raise RuntimeError("Gemini not available. Install: pip install google-generativeai")
            return GeminiProvider()
    
    async def run(self):
        """Execute full pipeline"""
        logger.info("=" * 60)
        logger.info("SEOULHOLIC SYNTHETIC DATA PIPELINE v3.0")
        logger.info(f"Provider: {self.config.provider} | Model: {self.config.model or 'default'}")
        logger.info(f"Target: {self.config.target_total} items")
        logger.info("=" * 60)
        
        all_items = []
        
        # Generate each category
        for category, target in self.DISTRIBUTION.items():
            if len(all_items) >= self.config.target_total:
                break
            
            actual_target = min(target, self.config.target_total - len(all_items))
            items = await self.generator.generate_category(category, actual_target)
            all_items.extend(items)
        
        # Validation
        logger.info("Validating data...")
        valid_items = [
            item for item in all_items 
            if self.validator.validate_item(item, DataCategory(item.category))
        ]
        logger.info(f"Valid: {len(valid_items)}/{len(all_items)}")
        
        # Deduplication
        unique_items = self.validator.deduplicate(valid_items)
        logger.info(f"Unique: {len(unique_items)} (removed {len(valid_items) - len(unique_items)} duplicates)")
        
        # Export
        logger.info("Exporting data...")
        
        # By category
        for cat in DataCategory:
            cat_items = [i for i in unique_items if i.category == cat.value]
            if cat_items:
                self.exporter.export_json(cat_items, f"{cat.value}_final.json")
        
        # Master file
        self.exporter.export_json(unique_items, "seoulholic_10k_master.json")
        
        # Training corpus
        self.exporter.export_training_corpus(unique_items, "training_corpus.txt")
        
        # Statistics
        stats = self.exporter.export_statistics(unique_items)
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Total generated: {len(unique_items)}")
        logger.info(f"Output directory: {self.config.output_dir}")
        logger.info("=" * 60)
        
        return unique_items


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Seoulholic Synthetic Data Generator")
    parser.add_argument("--provider", choices=["openai", "gemini"], default="gemini",
                       help="LLM provider to use")
    parser.add_argument("--model", type=str, default=None,
                       help="Specific model (e.g., gpt-4o, gemini-1.5-pro)")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Generation temperature")
    parser.add_argument("--target", type=int, default=10000,
                       help="Total items to generate")
    parser.add_argument("--output", type=str, default="./seoulholic_data",
                       help="Output directory")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Items per API call")
    
    args = parser.parse_args()
    
    # Build config
    config = GenerationConfig(
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        max_tokens=4096,
        target_total=args.target,
        batch_size=args.batch_size,
        output_dir=args.output
    )
    config.validate()
    
    # Run pipeline
    pipeline = SeoulholicPipeline(config)
    
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()