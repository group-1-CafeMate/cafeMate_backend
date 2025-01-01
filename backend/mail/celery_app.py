import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Create the Celery app instance.
app = Celery("mail")

# Configure Celery using Django settings with a 'CELERY_' namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in all registered Django app configs.
app.autodiscover_tasks()

# 定时任务调度配置
app.conf.beat_schedule = {
    "process_verification_email": {
        "task": "mail.tasks.process_verification_email_from_sqs",
        "schedule": crontab(minute="*"),  # 每分钟执行
    },
    "process_forgot_email": {
        "task": "mail.tasks.process_forgot_email_from_sqs",
        "schedule": crontab(minute="*"),  # 每分钟执行
    },
}
app.conf.CELERYBEAT_SCHEDULE_FILENAME = "mail/celery_beat_schedule"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
