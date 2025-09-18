import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, with up to 50% jitter
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "aoi_monitoring"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
