from pydantic import BaseModel, Field
from typing import Optional, List

class CodeRequest(BaseModel):
    """Request model for code operations"""
    code: str = Field(..., description="The code to process", example="def fibonacci(n):")
    context: Optional[str] = Field(None, description="Additional context for the code", example="This function should calculate fibonacci numbers")
    model: Optional[str] = Field("gpt-3.5-turbo", description="LLM model to use")

class CompletionResponse(BaseModel):
    """Response model for code completion"""
    original_code: str = Field(..., description="The original code provided")
    completion: str = Field(..., description="The AI-generated completion")
    model_used: str = Field(..., description="The LLM model used for completion")
    success: bool = Field(..., description="Whether the completion was successful")

class ReviewResponse(BaseModel):
    """Response model for code review"""
    original_code: str = Field(..., description="The original code provided")
    review: str = Field(..., description="The AI-generated code review")
    model_used: str = Field(..., description="The LLM model used for review")
    success: bool = Field(..., description="Whether the review was successful")

class ExplanationResponse(BaseModel):
    """Response model for code explanation"""
    original_code: str = Field(..., description="The original code provided")
    explanation: str = Field(..., description="The AI-generated explanation")
    model_used: str = Field(..., description="The LLM model used for explanation")
    success: bool = Field(..., description="Whether the explanation was successful")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    success: bool = Field(False, description="Always false for errors")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    api_key_configured: bool = Field(..., description="Whether OpenAI API key is configured")
    features: List[str] = Field(..., description="Available features")

class FileRequest(BaseModel):
    """Request model for file-based operations"""
    file_content: str = Field(..., description="Content of the file to process")
    filename: Optional[str] = Field(None, description="Name of the file")
    context: Optional[str] = Field(None, description="Additional context")
    model: Optional[str] = Field("gpt-3.5-turbo", description="LLM model to use")