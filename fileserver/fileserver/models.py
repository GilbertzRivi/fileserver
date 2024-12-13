from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class SharedFile(models.Model):
    created = models.DateTimeField()
    path = models.CharField(max_length=500)
    file_id = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def expired(self):
        expiration_date = self.created + timezone.timedelta(weeks=1)
        return expiration_date < timezone.now()

    @property
    def time_left(self):
        expiration_time = self.created + timezone.timedelta(weeks=1)
        time_diff = expiration_time - timezone.now()
        days, hours, minutes, seconds = 0, 0, 0, 0
        if not self.expired:
            days = time_diff.days
            _, remainder = divmod(time_diff.seconds, 60 * 60 * 24)
            hours, remainder = divmod(remainder, 60 * 60)
            minutes, seconds = divmod(remainder, 60)
        return f"{days} days {hours} hours {minutes} minutes and {seconds} seconds left"


class LocalShare(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, related_name="receiver", on_delete=models.CASCADE
    )
    path_org = models.CharField(max_length=500)
    path_remote = models.CharField(max_length=500)


class CssColor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=6)
