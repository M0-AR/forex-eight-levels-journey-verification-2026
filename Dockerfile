FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY experiments/ ./experiments/
COPY tests/ ./tests/
COPY data/ ./data/
CMD ["python", "experiments/run_all.py"]
