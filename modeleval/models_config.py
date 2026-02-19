"""
Model Configuration for Benchmark Testing
Supports OpenAI API compatible models
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a single model"""
    name: str
    provider: str
    api_key_env: str
    base_url: str
    model_id: str
    max_tokens: int
    temperature: float
    cost_per_1m_input: float  # USD
    cost_per_1m_output: float  # USD
    description: str
    thai_optimized: bool = False


# Model configurations
MODELS_TO_BENCHMARK: List[ModelConfig] = [
    ModelConfig(
        name="GPT-4o-mini",
        provider="OpenAI",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        model_id="gpt-4o-mini",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1m_input=0.15,
        cost_per_1m_output=0.60,
        description="Fast and cost-effective model for production use",
        thai_optimized=False
    ),
    
    ModelConfig(
        name="GPT-4o",
        provider="OpenAI",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        model_id="gpt-4o",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1m_input=2.50,
        cost_per_1m_output=10.00,
        description="Most capable OpenAI model with best reasoning",
        thai_optimized=False
    ),
    
    ModelConfig(
        name="Typhoon-v2.5-30B",
        provider="Typhoon",
        api_key_env="TYPHOON_API_KEY",
        base_url="https://api.opentyphoon.ai/v1",
        model_id="typhoon-v2.5-30b-a3b-instruct",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1m_input=0.30,
        cost_per_1m_output=0.30,
        description="Thai language specialist model with local context",
        thai_optimized=True
    ),
    
    ModelConfig(
        name="DeepSeek-v3",
        provider="DeepSeek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com/v1",
        model_id="deepseek-chat",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1m_input=0.27,
        cost_per_1m_output=1.10,
        description="Cost-effective model with GPT-4o-level performance",
        thai_optimized=False
    ),
    
    # Note: Gemini requires Google's SDK, not OpenAI-compatible
    # Uncomment and use google-generativeai package if needed
    # ModelConfig(
    #     name="Gemini-1.5-Flash",
    #     provider="Google",
    #     api_key_env="GOOGLE_API_KEY",
    #     base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    #     model_id="gemini-1.5-flash",
    #     max_tokens=4096,
    #     temperature=0.7,
    #     cost_per_1m_input=0.075,
    #     cost_per_1m_output=0.30,
    #     description="Extremely cost-effective and fast model with excellent Thai support",
    #     thai_optimized=True
    # ),
    
    ModelConfig(
        name="Groq-Llama-3.3-70B",
        provider="Groq",
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        model_id="llama-3.3-70b-versatile",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1m_input=0.59,
        cost_per_1m_output=0.79,
        description="Ultra-fast inference for real-time applications (500+ tokens/sec)",
        thai_optimized=False
    ),
]


def get_model_by_name(name: str) -> ModelConfig:
    """Get model configuration by name"""
    for model in MODELS_TO_BENCHMARK:
        if model.name == name:
            return model
    raise ValueError(f"Model {name} not found in configuration")


def get_all_models() -> List[ModelConfig]:
    """Get all model configurations"""
    return MODELS_TO_BENCHMARK


def get_thai_optimized_models() -> List[ModelConfig]:
    """Get only Thai-optimized models"""
    return [m for m in MODELS_TO_BENCHMARK if m.thai_optimized]


def print_models_summary():
    """Print a summary of all models"""
    print("\n" + "="*80)
    print("MODEL BENCHMARK CONFIGURATION")
    print("="*80)
    
    for i, model in enumerate(MODELS_TO_BENCHMARK, 1):
        thai_flag = "🇹🇭" if model.thai_optimized else ""
        print(f"\n{i}. {model.name} {thai_flag}")
        print(f"   Provider: {model.provider}")
        print(f"   Model ID: {model.model_id}")
        print(f"   Cost: ${model.cost_per_1m_input:.2f}/$" + 
              f"{model.cost_per_1m_output:.2f} per 1M tokens (input/output)")
        print(f"   Description: {model.description}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print_models_summary()
