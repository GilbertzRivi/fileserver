import os
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready, worker_shutdown
import redis

info = redis.Redis(host="redis", port=6379, decode_responses=True)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fileserver.settings")
app = Celery("fileserver")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "remove_old_files": {
        "task": "fileserver.tasks.remove_old_files",
        "schedule": crontab(minute="*/5"),
        "args": None,
    },
    "remove_thumbnails": {
        "task": "fileserver.tasks.remove_thumbnails",
        "schedule": crontab(minute="*/5"),
        "args": None,
    },
}


@worker_ready.connect
def startup(sender, **k):
    info.set("RemoveOldFilesLock", 0)
    info.set("RemoveThumbnailsLock", 0)
