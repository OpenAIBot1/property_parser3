"""LLM processor for extracting structured information from property listings."""
import json
from typing import Optional

import openai
from openai.error import OpenAIError

from .config import LLMConfig
from .schemas import PropertyDetails


class LLMProcessor:
    """Processor that uses OpenAI to extract structured information from listings."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the processor with configuration."""
        self.config = config
        openai.api_key = config.openai_api_key
        
    async def process_listing(self, text: str) -> Optional[PropertyDetails]:
        """Process a listing text and extract structured information.
        
        Args:
            text: Raw listing text to process
            
        Returns:
            PropertyDetails object with extracted information or None if processing failed
        """
        try:
            messages = [
                {"role": "system", "content": (
                    "You are a helpful assistant that extracts structured information "
                    "from property listings. Extract all relevant details and return "
                    "them in a valid JSON format matching the PropertyDetails schema."
                )},
                {"role": "user", "content": text}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return PropertyDetails(**data)
            
        except (OpenAIError, json.JSONDecodeError, ValueError) as e:
            # Log error here
            return None
