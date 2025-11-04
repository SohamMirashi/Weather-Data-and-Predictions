#!/usr/bin/env python3
"""
Start the FastAPI server
"""
import uvicorn

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API docs will be available at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
