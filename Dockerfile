FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg espeak-ng fonts-dejavu-core fonts-inter \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[claude]"

COPY brands /app/brands
ENV FACTORY_HOME=/app \
    FACTORY_DB=/data/factory.db \
    FACTORY_OUTPUT=/data/output \
    PYTHONUNBUFFERED=1
VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5).status == 200 else 1)"
CMD ["factory", "serve", "--host", "0.0.0.0", "--port", "8000"]
