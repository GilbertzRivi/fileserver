from .models import SharedFile

import datetime
import os
from .celery import app
import redis

info = redis.Redis(host="redis", port=6379, decode_responses=True)


@app.task
def remove_old_files():
    if not int(info.get("RemoveOldFilesLock")):
        info.set("RemoveOldFilesLock", 1)
        counter = 0
        for entry in SharedFile.objects.all():
            if (
                datetime.datetime.now().timestamp() - entry.created.timestamp()
                > 60 * 60 * 24 * 7
            ):
                os.remove(entry.path)
                counter += 1
                entry.delete()
        info.set("RemoveOldFilesLock", 0)
        if counter:
            return f"Deleted {counter} externally shared files that has been older than 7 days"
        else:
            return "No externally shared files to delete"
    else:
        return "Deletion of externally shared files locked"


@app.task
def remove_thumbnails():
    if not int(info.get("RemoveThumbnailsLock")):
        info.set("RemoveThumbnailsLock", 1)
        counter = 0
        for file in os.listdir("/raid/"):
            if (
                file != "video_icon.png"
                and not os.path.isdir(f"/raid/{file}")
                and not file.split(".")[-1].lower() == "mp4"
            ):
                os.remove(f"/raid/{file}")
                counter += 1
        info.set("RemoveThumbnailsLock", 0)
        if counter:
            return f"Deleted {counter} thumbnails"
        else:
            return "No thumbnails to delete"
    else:
        return "Deletion of thumbnails locked"
