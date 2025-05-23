from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import sys
import os
import time
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models import CodeRequest, CompletionResponse, ErrorResponse, FileRequest
from models.llm_client import LLMClient
from services.analytics import AnalyticsService
import asyncio

router = APIRouter()
analytics = AnalyticsService()

@router.post("/complete", response_model=CompletionResponse)
async def complete_code(request: CodeRequest):
    """
    Complete code using AI
    
    - **code**: The code to complete
    - **context**: Optional context to help with completion
    - **model**: OpenAI model to use (default: gpt-3.5-turbo)
    """
    start_time = time.time()
    
    try:
        # Check if API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            analytics.track_request("completion", False)
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        # Create LLM client
        llm = LLMClient(model=request.model)
        
        # Build completion prompt
        prompt = f"Complete this Python code:\n\n```python\n{request.code}\n```\n\n"
        
        if request.code.strip().endswith(':'):
            prompt += "Complete the code block that follows this statement."
        elif 'def ' in request.code:
            prompt += "Complete the function implementation with proper logic."
        else:
            prompt += "Continue the code naturally based on the context."
        
        if request.context:
            prompt += f"\n\nAdditional context: {request.context}"
        
        prompt += "\n\nProvide only the completion code, properly formatted and indented."
        
        # Generate completion
        messages = [
            {
                "role": "system",
                "content": "You are an expert Python programmer. Complete the code naturally and efficiently. Only return the completion, not the original code."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        completion = await llm.generate(messages, temperature=0.3, max_tokens=500)
        
        # Track successful request
        response_time = time.time() - start_time
        analytics.track_request("completion", True, response_time)
        
        return CompletionResponse(
            original_code=request.code,
            completion=completion,
            model_used=request.model,
            success=True
        )
        
    except ValueError as e:
        analytics.track_request("completion", False)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        analytics.track_request("completion", False)
        raise HTTPException(status_code=500, detail=f"Completion failed: {str(e)}")

@router.post("/complete/file", response_model=CompletionResponse)
async def complete_file(request: FileRequest):
    """
    Complete code from file content
    
    - **file_content**: The content of the file to complete
    - **filename**: Optional filename for context
    - **context**: Optional additional context
    - **model**: OpenAI model to use
    """
    start_time = time.time()
    
    try:
        # Convert FileRequest to CodeRequest
        code_request = CodeRequest(
            code=request.file_content,
            context=f"File: {request.filename}. {request.context or ''}".strip(),
            model=request.model
        )
        
        # Use the existing complete_code function
        result = await complete_code(code_request)
        
        # Note: Analytics already tracked in complete_code function
        return result
        
    except Exception as e:
        analytics.track_request("completion", False)
        raise HTTPException(status_code=500, detail=f"File completion failed: {str(e)}")

@router.get("/complete/examples")
async def get_completion_examples():
    """Get example requests for code completion"""
    return {
        "examples": [
            {
                "name": "Function Definition",
                "request": {
                    "code": "def fibonacci(n):",
                    "context": "Calculate fibonacci numbers recursively"
                }
            },
            {
                "name": "For Loop",
                "request": {
                    "code": "for i in range(10):",
                    "context": "Print numbers"
                }
            },
            {
                "name": "Class Definition", 
                "request": {
                    "code": "class Calculator:",
                    "context": "Simple calculator with basic operations"
                }
            }
        ]
    }

@router.get("/complete/stats")
async def get_completion_analytics():
    """Get completion-specific analytics"""
    stats = analytics.get_stats()
    return {
        "completion_requests": stats.get("completion_requests", 0),
        "total_requests": stats.get("total_requests", 0),
        "success_rate": stats.get("success_rate", 0),
        "average_response_time": stats.get("average_response_time", 0),
        "requests_per_day": stats.get("requests_per_day", 0)
    }