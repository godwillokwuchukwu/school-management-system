import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\celery.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_config = """
from celery.schedules import crontab

app.conf.beat_schedule = {
    'run-etl-nightly': {
        'task': 'warehouse.tasks.run_etl_pipeline',
        'schedule': crontab(hour=2, minute=0),
    },
}
"""

with open(file_path, "a", encoding="utf-8") as f:
    f.write(new_config)
