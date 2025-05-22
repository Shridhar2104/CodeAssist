from fastapi import APIRouter, HTTPException
import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models import CodeRequest, ReviewResponse, FileRequest
from models.llm_client import LLMClient

router = APIRouter()

@router.post("/review", response_model=ReviewResponse)
async def review_code(request: CodeRequest):
    """
    Review code and provide improvement suggestions
    
    - **code**: The code to review
    - **context**: Optional context about the code
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
        
        # Build review prompt
        prompt = f"Please review this Python code:\n\n```python\n{request.code}\n```"
        
        if request.context:
            prompt += f"\n\nContext: {request.context}"
        
        # Generate review
        messages = [
            {
                "role": "system",
                "content": """You are an expert code reviewer. Analyze the code for:
                1. Code quality and best practices
                2. Performance issues
                3. Security vulnerabilities
                4. Readability and maintainability
                5. Potential bugs or edge cases
                
                Provide constructive feedback with specific suggestions for improvement.
                Format your response clearly with sections and actionable advice."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        review = await llm.generate(messages, temperature=0.3, max_tokens=800)
        
        return ReviewResponse(
            original_code=request.code,
            review=review,
            model_used=request.model,
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")

@router.post("/review/file", response_model=ReviewResponse)
async def review_file(request: FileRequest):
    """
    Review code from file content
    
    - **file_content**: The content of the file to review
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
        
        # Use the existing review_code function
        return await review_code(code_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File review failed: {str(e)}")

@router.get("/review/examples")
async def get_review_examples():
    """Get example requests for code review"""
    return {
        "examples": [
            {
                "name": "Loop Performance",
                "request": {
                    "code": "for i in range(len(data)):\n    result.append(data[i] * 2)",
                    "context": "Processing large datasets"
                }
            },
            {
                "name": "Error Handling",
                "request": {
                    "code": "def divide(a, b):\n    return a / b",
                    "context": "Mathematical operations"
                }
            },
            {
                "name": "Security Check",
                "request": {
                    "code": "import subprocess\nsubprocess.call(user_input, shell=True)",
                    "context": "Running user commands"
                }
            }
        ]
    }