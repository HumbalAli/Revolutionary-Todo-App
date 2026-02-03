import os
import sys
import uvicorn

# Add the backend directory to Python path to import the minimal app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the full application instead of minimal_app
from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )