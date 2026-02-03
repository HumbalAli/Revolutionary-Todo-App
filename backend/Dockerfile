FROM python:3.12-slim

WORKDIR /src

COPY /requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /src/ ./src/

EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]