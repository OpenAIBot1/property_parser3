"""LLM processor for extracting structured information from property listings."""
import json
from typing import Optional

from openai import OpenAI
from openai.error import OpenAIError

from .config import LLMConfig
from .schemas import Property


class LLMProcessor:
    """Processor that uses OpenAI to extract structured information from listings."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the processor with configuration."""
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        
    async def process_listing(self, text: str) -> Optional[Property]:
        """Process a listing text and extract structured information.
        
        Args:
            text: Raw listing text to process
            
        Returns:
            Property object with extracted information or None if processing failed
        """
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
Extract all relevant details from the property listing.
For layout, use one of: "studio", "1+1", "2+1", "3+1", "other"
For heating_type, use one of: "central", "individual", "none", "other"
For pet_policy, use one of: "allowed", "not_allowed", "negotiable", "other"
Convert all prices to USD using approximate rate: 1 USD = 3 GEL"""
                    },
                    {"role": "user", "content": text}
                ],
                response_format=Property,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            # Log error here
            return None
