import os
from typing import Optional, Dict, Any, List
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv


load_dotenv()


class LLMClient:
    """LCient for interacting with the OPENAI Language Models"""


    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key or self.api_key == "your_openai_api_key_here":
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY in your .env file."
            )
        
        self.client = AsyncOpenAI(api_key=self.api_key)

    
    async def generate(
            self, 
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            **kwargs
    ) ->str:
        """Generate response from the language model"""

        try:
            response = await self.client.chat.completions.create(
                model = self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choice[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM generation faile: {str(e)}")