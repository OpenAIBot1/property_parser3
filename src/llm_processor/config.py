"""Configuration for the LLM processor service."""
from typing import Optional
from pydantic import BaseSettings


class LLMConfig(BaseSettings):
    """OpenAI API configuration."""
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 1000
    
    class Config:
        env_prefix = "OPENAI_"
        case_sensitive = False
