# Stage 1: Base build stage
FROM python:3.13-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

# Create necessary directories and user
RUN useradd -m -r appuser && \
    mkdir -p /app/static/img && \
    mkdir -p /app/staticfiles && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy the entire application code first
COPY --chown=appuser:appuser . .

# Create the SVG file directly in the container
RUN echo '<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><path d="M100 10 L180 50 L180 120 Q100 190 100 190 Q100 190 20 120 L20 50 Z" fill="#2563eb" stroke="#1e40af" stroke-width="4"/><g fill="white"><rect x="60" y="45" width="12" height="90" rx="2"/><rect x="85" y="45" width="55" height="12" rx="2"/><rect x="106" y="45" width="12" height="90" rx="2"/></g><g stroke="rgba(255,255,255,0.5)" stroke-width="2" fill="none"><path d="M40 100 L55 100"/><path d="M145 100 L160 100"/><path d="M100 155 L100 170"/><circle cx="55" cy="100" r="3" fill="rgba(255,255,255,0.5)"/><circle cx="145" cy="100" r="3" fill="rgba(255,255,255,0.5)"/><circle cx="100" cy="155" r="3" fill="rgba(255,255,255,0.5)"/></g><path d="M95 30 L105 30 L110 38 L105 46 L95 46 L90 38 Z" fill="rgba(255,255,255,0.2)"/></svg>' > /app/static/img/infotitans-logo.svg

# Ensure proper ownership
RUN chown -R appuser:appuser /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "TitansManager.wsgi:application"]