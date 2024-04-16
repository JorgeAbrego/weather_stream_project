FROM python:3.10-slim

WORKDIR /app

COPY ["stream_app.py", "producer_requirements.txt", "./"]

RUN pip install --no-cache-dir -r producer_requirements.txt

EXPOSE 8000

CMD ["uvicorn", "stream_app:app", "--host", "0.0.0.0", "--port", "8000"]
