from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.llm_client import LLMClient

class CodeCompleter:
    """Service for intelligent code completion"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.llm = LLMClient(model=model)
    
    async def complete(self, code: str, context: Optional[str] = None) -> str:
        """Complete the given code snippet"""
        
        prompt = self._build_completion_prompt(code, context)
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert Python programmer. Complete the code naturally and efficiently. 
                Only return the completion, not the original code. Make sure the completion is properly indented."""
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        completion = await self.llm.generate(messages, temperature=0.3, max_tokens=500)
        return completion
    
    def _build_completion_prompt(self, code: str, context: Optional[str] = None) -> str:
        """Build an effective prompt for code completion"""
        
        prompt = f"Complete this Python code:\n\n```python\n{code}\n```\n\n"
        
        if code.strip().endswith(':'):
            prompt += "Complete the code block that follows this statement."
        elif 'def ' in code and code.count('def') == code.count('\n') + 1:
            prompt += "Complete the function implementation with proper logic."
        else:
            prompt += "Continue the code naturally based on the context."
        
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        prompt += "\n\nProvide only the completion code, properly formatted and indented."
        
        return prompt