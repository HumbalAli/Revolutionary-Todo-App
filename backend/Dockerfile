FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for psycopg2)
# RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY __init__.py . 

# Expose port (default 8000)
EXPOSE 8000

# Run the application
# We use the src.main module which we fixed to use relative imports
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]