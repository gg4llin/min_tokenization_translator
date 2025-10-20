FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./ 
COPY src ./src
COPY scripts ./scripts

RUN pip install --upgrade pip && \
    pip install -e .[server]

EXPOSE 8080

CMD ["uvicorn", "min_tokenization_translator.server:create_app", "--host", "0.0.0.0", "--port", "8080"]
