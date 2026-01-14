# Entry point for Railway deployment
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path so we can import from src
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Import and expose the FastAPI app
from src.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=1
    )