# Stage 1: Base build stage
FROM python:3.13.1-slim-bookworm AS builder

# Add metadata
LABEL maintainer="InfoTitans <femioladele@infotitans.com>" \
      version="1.0" \
      description="InfoTitans Project Management System"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create the app directory
WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# Stage 2: Production stage
FROM python:3.13.1-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PATH="/home/appuser/.local/bin:$PATH"

# Create necessary directories
RUN mkdir -p /app/static/img /app/staticfiles \
    && groupadd -r appgroup \
    && useradd -r -g appgroup -d /home/appuser -m -s /sbin/nologin appuser \
    && chown -R appuser:appgroup /app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Create the SVG logo
RUN echo '<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><path d="M100 10 L180 50 L180 120 Q100 190 100 190 Q100 190 20 120 L20 50 Z" fill="#2563eb" stroke="#1e40af" stroke-width="4"/><g fill="white"><rect x="60" y="45" width="12" height="90" rx="2"/><rect x="85" y="45" width="55" height="12" rx="2"/><rect x="106" y="45" width="12" height="90" rx="2"/></g><g stroke="rgba(255,255,255,0.5)" stroke-width="2" fill="none"><path d="M40 100 L55 100"/><path d="M145 100 L160 100"/><path d="M100 155 L100 170"/><circle cx="55" cy="100" r="3" fill="rgba(255,255,255,0.5)"/><circle cx="145" cy="100" r="3" fill="rgba(255,255,255,0.5)"/><circle cx="100" cy="155" r="3" fill="rgba(255,255,255,0.5)"/></g><path d="M95 30 L105 30 L110 38 L105 46 L95 46 L90 38 Z" fill="rgba(255,255,255,0.2)"/></svg>' > /app/static/img/infotitans-logo.svg

# Collect static files
RUN python manage.py collectstatic --noinput

# Set proper permissions
RUN chown -R appuser:appgroup /app \
    && chmod -R 750 /app \
    && chmod -R 740 /app/static /app/staticfiles

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "TitansManager.wsgi:application"]