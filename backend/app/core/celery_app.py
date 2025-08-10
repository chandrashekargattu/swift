"""Celery configuration and initialization."""
import os
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "rideswift",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email",
        "app.tasks.sms",
        "app.tasks.notifications",
        "app.tasks.bookings",
        "app.tasks.analytics",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.sms.*": {"queue": "sms"},
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.bookings.*": {"queue": "bookings"},
        "app.tasks.analytics.*": {"queue": "analytics"},
    },
    
    # Task priorities
    task_annotations={
        "app.tasks.email.send_email": {"priority": 5},
        "app.tasks.sms.send_sms": {"priority": 7},
        "app.tasks.notifications.send_push": {"priority": 3},
    },
    
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule configuration
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.tasks.maintenance.cleanup_expired_sessions",
            "schedule": 3600.0,  # Every hour
        },
        "send-daily-reports": {
            "task": "app.tasks.analytics.send_daily_reports",
            "schedule": 86400.0,  # Every day
        },
        "check-pending-bookings": {
            "task": "app.tasks.bookings.check_pending_bookings",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)

# Set up periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks."""
    # Example: sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
    pass


def get_celery_app():
    """Get Celery app instance."""
    return celery_app
