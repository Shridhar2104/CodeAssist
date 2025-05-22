from fastapi import APIRouter, HTTPException
import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models import CodeRequest, ExplanationResponse, FileRequest
from models.llm_client import LLMClient

router = APIRouter()

@router.post("/explain", response_model=ExplanationResponse)
async def explain_code(request: CodeRequest):
    """
    Explain code in natural language
    
    - **code**: The code to explain
    - **context**: Optional context about the code's purpose
    - **model**: OpenAI model to use (default: gpt-3.5-turbo)
    """
    try:
        # Check if API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        # Create LLM client
        llm = LLMClient(model=request.model)
        
        # Build explanation prompt
        prompt = f"Please explain what this Python code does:\n\n```python\n{request.code}\n```"
        
        if request.context:
            prompt += f"\n\nContext: {request.context}"
        
        # Generate explanation
        messages = [
            {
                "role": "system",
                "content": """You are a helpful programming tutor. Explain code in clear, simple language that anyone can understand.
                
                Break down complex concepts and explain the purpose and functionality of the code step by step.
                Use bullet points and clear sections to make it easy to follow.
                
                Focus on:
                1. What the code does (high-level purpose)
                2. How it works (step-by-step breakdown)
                3. Key concepts or patterns used
                4. Any important details or gotchas"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        explanation = await llm.generate(messages, temperature=0.5, max_tokens=600)
        
        return ExplanationResponse(
            original_code=request.code,
            explanation=explanation,
            model_used=request.model,
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@router.post("/explain/file", response_model=ExplanationResponse)
async def explain_file(request: FileRequest):
    """
    Explain code from file content
    
    - **file_content**: The content of the file to explain
    - **filename**: Optional filename for context
    - **context**: Optional additional context
    - **model**: OpenAI model to use
    """
    try:
        # Convert FileRequest to CodeRequest
        code_request = CodeRequest(
            code=request.file_content,
            context=f"File: {request.filename}. {request.context or ''}".strip(),
            model=request.model
        )
        
        # Use the existing explain_code function
        return await explain_code(code_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File explanation failed: {str(e)}")

@router.get("/explain/examples")
async def get_explanation_examples():
    """Get example requests for code explanation"""
    return {
        "examples": [
            {
                "name": "Lambda Function",
                "request": {
                    "code": "lambda x: x**2 + 2*x + 1",
                    "context": "Mathematical function"
                }
            },
            {
                "name": "List Comprehension",
                "request": {
                    "code": "squares = [x**2 for x in range(10) if x % 2 == 0]",
                    "context": "Data processing"
                }
            },
            {
                "name": "Decorator",
                "request": {
                    "code": "@property\ndef full_name(self):\n    return f'{self.first} {self.last}'",
                    "context": "Class method"
                }
            }
        ]
    }