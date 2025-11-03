#!/usr/bin/env python3
"""
Start the BrickByByte FastAPI server
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting BrickByByte API Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📖 API documentation at: http://127.0.0.1:8000/docs")
    print("🔄 Press Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "brickbybyte_api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )