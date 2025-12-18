# Build Stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final Stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# Environment Defaults
ENV PORT=8000
ENV DATABASE_URL=postgresql://user:pass@db:5432/eduparty

# Run Command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
