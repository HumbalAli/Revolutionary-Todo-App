from fastapi import FastAPI

# Create a minimal app without any database dependencies
app = FastAPI(title="Minimal Todo API")

@app.get("/")
async def root():
    return {"message": "Minimal API running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Minimal API is running"}

# Only include essential routes that don't require database