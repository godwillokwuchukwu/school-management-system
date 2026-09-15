import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("school_management_system")

# Use django-celery-results and DB broker for local dev
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


from celery.schedules import crontab

app.conf.beat_schedule = {
    "run-etl-nightly": {
        "task": "warehouse.tasks.run_etl_pipeline",
        "schedule": crontab(hour=2, minute=0),
    },
}
