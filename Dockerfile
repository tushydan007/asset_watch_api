FROM python:3.11-slim

# Install system dependencies for PostGIS, GDAL, GEOS, PROJ
RUN apt-get update && apt-get install -y \
    binutils \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialite-dev \
    postgresql-client \
    libpq-dev \
    python3-gdal \
    build-essential \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge
    

# Create scripts directory
RUN mkdir -p /usr/local/bin/scripts

# Copy entrypoint scripts into that directory
COPY scripts/docker-entrypoint-backend.sh /usr/local/bin/scripts/
COPY scripts/docker-entrypoint-celery.sh /usr/local/bin/scripts/
COPY scripts/docker-entrypoint-migrate.sh /usr/local/bin/scripts/


# Make them executable
RUN chmod +x /usr/local/bin/scripts/docker-entrypoint-backend.sh \
    && chmod +x /usr/local/bin/scripts/docker-entrypoint-celery.sh \
    && chmod +x /usr/local/bin/scripts/docker-entrypoint-migrate.sh 


# Copy project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/admin/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "asset_watch.wsgi:application"]

