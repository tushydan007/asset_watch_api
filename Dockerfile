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


# Copy entrypoint script
COPY scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/admin/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "asset_watch.wsgi:application"]







# FROM python:3.11-slim

# # Install system dependencies for PostGIS, GDAL, GEOS, PROJ
# RUN apt-get update && apt-get install -y \
#     binutils \
#     gdal-bin \
#     libgdal-dev \
#     libgeos-dev \
#     libproj-dev \
#     libspatialite-dev \
#     postgresql-client \
#     libpq-dev \
#     python3-gdal \
#     build-essential \
#     netcat-openbsd \
#     curl \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# ENV PYTHONUNBUFFERED=1
    
# # Set environment variables for GDAL/GEOS
# ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
# ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# # Set work directory
# WORKDIR /app

# # Install Python dependencies
# COPY requirements.txt /app/
# RUN pip install --upgrade pip setuptools wheel
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project
# COPY . /app/

# # Create directories for static and media files
# RUN mkdir -p /app/staticfiles /app/media /app/logs

# EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/admin/ || exit 1

# CMD ["gunicorn", "--config", "gunicorn.conf.py", "asset_watch.wsgi:application"]
