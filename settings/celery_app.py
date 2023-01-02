import os
from decouple import config

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

celery_app = Celery(config("DATABASE_NAME"))
celery_app.conf.timezone = "Asia/Tehran"
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
