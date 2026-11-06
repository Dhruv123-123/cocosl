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
CMD ["factory", "serve", "--host", "0.0.0.0", "--port", "8000"]
