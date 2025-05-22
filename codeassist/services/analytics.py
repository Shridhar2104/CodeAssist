import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class AnalyticsService:
    """Simple analytics tracking service"""
    
    def __init__(self):
        self.analytics_file = Path("analytics.json")
        self._ensure_analytics_file()
    
    def _ensure_analytics_file(self):
        """Create analytics file if it doesn't exist"""
        if not self.analytics_file.exists():
            initial_data = {
                "total_requests": 0,
                "completion_requests": 0,
                "review_requests": 0,
                "explanation_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "first_request": None,
                "last_request": None,
                "requests_by_day": {},
                "response_times": []
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load analytics data"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save analytics data"""
        with open(self.analytics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_request(self, request_type: str, success: bool, response_time: float = 0.0):
        """Track a request"""
        data = self._load_data()
        now = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update counters
        data["total_requests"] += 1
        data[f"{request_type}_requests"] = data.get(f"{request_type}_requests", 0) + 1
        
        if success:
            data["successful_requests"] += 1
        else:
            data["failed_requests"] += 1
        
        # Track response times
        if response_time > 0:
            data["response_times"].append(response_time)
            # Keep only last 1000 response times to prevent file from growing too large
            if len(data["response_times"]) > 1000:
                data["response_times"] = data["response_times"][-1000:]
            data["average_response_time"] = sum(data["response_times"]) / len(data["response_times"])
        
        # Track by day
        if today not in data["requests_by_day"]:
            data["requests_by_day"][today] = 0
        data["requests_by_day"][today] += 1
        
        # Update timestamps
        if not data["first_request"]:
            data["first_request"] = now
        data["last_request"] = now
        
        self._save_data(data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current analytics stats"""
        data = self._load_data()
        
        # Calculate uptime
        if data.get("first_request"):
            first = datetime.fromisoformat(data["first_request"])
            days_running = (datetime.now() - first).days + 1
        else:
            days_running = 0
        
        # Calculate success rate
        total = data["total_requests"]
        success_rate = (data["successful_requests"] / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "success_rate": round(success_rate, 1),
            "average_response_time": round(data["average_response_time"], 2),
            "days_running": days_running,
            "requests_per_day": round(total / days_running, 1) if days_running > 0 else 0,
            "completion_requests": data.get("completion_requests", 0),
            "review_requests": data.get("review_requests", 0),
            "explanation_requests": data.get("explanation_requests", 0)
        }