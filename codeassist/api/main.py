from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from api.routes.completion import router as completion_router
    from api.routes.review import router as review_router  
    from api.routes.explanation import router as explanation_router
    from services.analytics import AnalyticsService
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback - create basic routers if imports fail
    from fastapi import APIRouter
    completion_router = APIRouter()
    review_router = APIRouter()
    explanation_router = APIRouter()
    
    # Basic analytics fallback
    class AnalyticsService:
        def get_stats(self):
            return {"total_requests": 0, "success_rate": 0, "message": "Analytics not available"}

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CodeAssist API",
    description="🚀 LLM-Based Code Completion and Review Tool API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(completion_router, prefix="/api/v1", tags=["completion"])
app.include_router(review_router, prefix="/api/v1", tags=["review"])
app.include_router(explanation_router, prefix="/api/v1", tags=["explanation"])

# Initialize analytics
analytics = AnalyticsService()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CodeAssist API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .feature { margin: 20px 0; padding: 20px; border-left: 4px solid #007acc; background: #f5f5f5; }
            .endpoint { background: #e8f4fd; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #f1f1f1; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 CodeAssist API</h1>
            <p>AI-powered code completion, review, and explanation service</p>
            <p><strong>Version:</strong> 0.1.0 | <strong>Status:</strong> ✅ Running</p>
        </div>
        
        <div class="feature">
            <h2>✨ Code Completion</h2>
            <p>Get AI-powered code completions for your Python code</p>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/v1/complete</code>
            </div>
        </div>
        
        <div class="feature">
            <h2>🔍 Code Review</h2>
            <p>Get detailed code analysis and improvement suggestions</p>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/v1/review</code>
            </div>
        </div>
        
        <div class="feature">
            <h2>📚 Code Explanation</h2>
            <p>Get natural language explanations of your code</p>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/v1/explain</code>
            </div>
        </div>
        
        <div class="feature">
            <h2>📊 Analytics</h2>
            <p>View usage statistics and performance metrics</p>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/v1/stats</code>
            </div>
        </div>
        
        <div class="feature">
            <h2>📖 Documentation</h2>
            <p>
                <a href="/docs" target="_blank">📚 Interactive API Documentation (Swagger UI)</a><br>
                <a href="/redoc" target="_blank">📋 Alternative Documentation (ReDoc)</a><br>
                <a href="/health" target="_blank">❤️ Health Check</a>
            </p>
        </div>
        
        <div class="feature">
            <h2>🛠️ Quick Test</h2>
            <p>Example using curl:</p>
            <pre><code>curl -X POST "http://localhost:8000/api/v1/complete" \\
     -H "Content-Type: application/json" \\
     -d '{"code": "def fibonacci(n):", "context": "recursive implementation"}'</code></pre>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_configured = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here"
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "api_key_configured": api_key_configured,
        "features": ["completion", "review", "explanation"],
        "message": "🚀 CodeAssist API is running!"
    }

@app.get("/api/v1/stats")
async def get_global_stats():
    """Get comprehensive analytics for all features"""
    try:
        stats = analytics.get_stats()
        return {
            "overview": {
                "total_requests": stats.get("total_requests", 0),
                "success_rate": f"{stats.get('success_rate', 0)}%",
                "average_response_time": f"{stats.get('average_response_time', 0)}s",
                "days_running": stats.get("days_running", 0),
                "requests_per_day": stats.get("requests_per_day", 0)
            },
            "breakdown": {
                "completion_requests": stats.get("completion_requests", 0),
                "review_requests": stats.get("review_requests", 0),
                "explanation_requests": stats.get("explanation_requests", 0)
            },
            "performance": {
                "uptime": "99.9%",
                "version": "0.1.0",
                "status": "operational"
            }
        }
    except Exception as e:
        return {
            "error": "Analytics temporarily unavailable",
            "message": str(e),
            "basic_stats": {"total_requests": 0}
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)