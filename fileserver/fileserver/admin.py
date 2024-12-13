from django.contrib import admin
from .models import (
    SharedFile,
    LocalShare,
)


@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ("time_left", "user")


@admin.register(LocalShare)
class LocalShareAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "path_org", "path_remote")
