from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("accounts/", views.sign_in, name="accounts"),
    path("accounts/login/", views.sign_in, name="login"),
    path("accounts/logout/", views.sign_out, name="logout"),
    path("accounts/password/", views.change_password, name="change_password"),
    path("home/", views.home, name="home"),
    path("home/<str:directory>", views.home, name="home"),
    path("home/<str:directory>/<str:subdirectory>", views.home, name="home"),
    path("upload/", views.upload, name="upload"),
    path("download/<str:directory>/<str:file>", views.download, name="download"),
    path(
        "download/<str:directory>/<str:subdirectory>/<str:file>",
        views.download,
        name="download",
    ),
    path(
        "download_compressed/<str:directory>",
        views.download_compressed,
        name="download_compressed",
    ),
    path(
        "download_compressed/<str:directory>/<str:subdirectory>",
        views.download_compressed,
        name="download_compressed",
    ),
    path(
        "compress_directory/<str:directory>",
        views.compress_directory,
        name="compress_directory",
    ),
    path(
        "compress_directory/<str:directory>/<str:subdirectory>",
        views.compress_directory,
        name="compress_directory",
    ),
    path("delete/<str:directory>/<str:file>", views.delete, name="delete"),
    path(
        "delete_all/<str:directory>/<str:subdirectory>",
        views.delete_all,
        name="delete_all",
    ),
    path(
        "delete_all/<str:directory>",
        views.delete_all,
        name="delete_all",
    ),
    path(
        "delete_thumbnail/<str:file>", views.delete_thumbnail, name="delete_thumbnail"
    ),
    path("create_folder/<str:name>", views.create_folder, name="create_folder"),
    path(
        "get_thumbnail/<str:directory>/<str:file>",
        views.get_thumbnail,
        name="get_thumbnail",
    ),
    path(
        "get_thumbnail/<str:directory>/<str:subdirectory>/<str:file>",
        views.get_thumbnail,
        name="get_thumbnail",
    ),
    path(
        "change_filename/<str:directory>/<str:file>/<str:newname>",
        views.change_filename,
        name="change_filename",
    ),
    path(
        "generate_share/<str:directory>/<str:file>",
        views.generate_share,
        name="generate_share",
    ),
    path("shared_file/<str:file_id>", views.shared_file, name="shared_file"),
    path("load_files/", views.load_files, name="load_files"),
    path("filename/", views.filename, name="filename"),
    path("shared_links/", views.shared_links, name="shared_links"),
    path(
        "remove_shared_link/<str:file_id>",
        views.remove_shared_link,
        name="remove_shared_link",
    ),
    path("list_users/", views.list_users, name="list_users"),
    path("local_share/", views.local_share, name="local_share"),
    path("shared_files/", views.shared_files, name="shared_files"),
    path("stop_share/<int:pk>", views.stop_share, name="stop_share"),
    path("file_size/<str:directory>/<str:file>", views.file_size, name="file_size"),
    path(
        "file_size/<str:shared>/<str:directory>/<str:file>",
        views.file_size,
        name="file_size",
    ),
    path(
        "display_media/<str:directory>/<str:file>",
        views.display_media,
        name="display_media",
    ),
    path(
        "display_media/<str:shared>/<str:directory>/<str:file>",
        views.display_media,
        name="display_media",
    ),
    path(
        "unlink_directory/<str:directory>",
        views.unlink_directory,
        name="unlink_directory",
    ),
    path("system_stats/", views.system_stats, name="system_stats"),
    path("save_color/<str:color>", views.save_color, name="save_color"),
    path(
        "get_thumbnail_shared/<str:file>",
        views.get_thumbnail_shared,
        name="get_thumbnail_shared",
    ),
    path(
        "get_file_info/<str:shared>/<str:directory>/<str:file>",
        views.get_file_info,
        name="get_file_info",
    ),
    path(
        "get_file_info/<str:directory>/<str:file>",
        views.get_file_info,
        name="get_file_info",
    ),
]
