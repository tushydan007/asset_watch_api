import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asset_watch.settings")

app = Celery("asset_watch")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    "schedule-monitoring-jobs": {
        "task": "monitoring.tasks.schedule_monitoring_jobs",
        "schedule": crontab(minute=0),  # Every hour
    },
    "fetch-satellite-images": {
        "task": "monitoring.tasks.fetch_satellite_images",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-old-data": {
        "task": "monitoring.tasks.cleanup_old_data",
        "schedule": crontab(
            hour=2, minute=0, day_of_week=1
        ),  # Weekly on Monday at 2 AM
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
