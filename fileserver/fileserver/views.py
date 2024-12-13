from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse, StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

import os
import base64
import shutil
import uuid
import subprocess
import zipfile
from .forms import LoginForm
from PIL import Image
from io import BytesIO
from urllib.parse import unquote
from .models import SharedFile, LocalShare, CssColor
import psutil

VIDEO_FORMATS = ["mp4", "webm"]
IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "webp"]
SUPPORTED_FORMATS = VIDEO_FORMATS + IMAGE_FORMATS

CHUNK_DEFAULT = 1024 * 1024


def handle_uploaded_file(f, destination, directory, filename):
    decoded_data = base64.b64decode(f)
    filename = "-".join(filename.split("-")[:-1])
    if directory == "":
        path = f"/raid/{destination}/{filename}"
    else:
        path = f"/raid/{destination}/{directory}/{filename}"
    path = unquote(path)
    with open(path, "ab+") as destination:
        destination.write(decoded_data)


def index(request):
    logout(request)
    return render(request, "index.html")


def sign_in(request):
    logout(request)

    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    elif request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                entry = CssColor.objects.filter(user=user)
                if not entry.exists():
                    entry = CssColor()
                    entry.user = user
                    entry.color = "00cdee"
                    entry.save()
                if not os.path.isdir(f"/raid/{user.username}"):
                    os.mkdir(f"/raid/{user.username}")
                if not os.path.isdir(f"/raid/{user.username}/shared"):
                    os.mkdir(f"/raid/{user.username}/shared")
                messages.success(request, f"Hi {username.title()}, welcome back!")
                return redirect("home")

        messages.error(request, f"Invalid username or password")

        return render(request, "login.html", {"form": form})


@login_required
def sign_out(request):
    logout(request)
    messages.success(request, f"You have been logged out.")
    return redirect("login")


@login_required
def get_thumbnail_shared(request, file=""):
    path = f"/raid/shared"
    thumbnailed = False
    extension = file.split(".")[-1].lower()
    if extension in SUPPORTED_FORMATS:
        if extension in VIDEO_FORMATS:
            thumbnailed = True
            thumbnail = f"{uuid.uuid4()}.png"
            cmd = [
                "ffmpeg",
                "-i",
                f"{path}/{file}",
                "-ss",
                "00:00:00.000",
                "-vframes",
                "1",
                f"/raid/{thumbnail}",
            ]
            process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            process.wait()
            path = "/raid"
            file = thumbnail
            extension = "png"
        with Image.open(f"{path}/{file}") as img:
            with BytesIO() as buffered:
                if thumbnailed:
                    icon = Image.open("/raid/video_icon.png")
                    img.paste(icon, (0, 0), icon)
                img = img.resize(
                    (
                        150,
                        int((float(img.size[1]) * float((150 / float(img.size[0]))))),
                    ),
                    Image.Resampling.LANCZOS,
                )
                if extension == "jpg":
                    extension = "jpeg"
                img.save(buffered, extension)
                image_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        response = {"data": image_data}
        if thumbnailed:
            response["file"] = thumbnail
        else:
            response["file"] = ""
    else:
        response = {}
        response["file"] = ""
    return JsonResponse(response)


@login_required
def get_thumbnail(request, directory="", subdirectory="", file=""):
    if directory == "-":
        path = f"/raid/{request.user.username}"
    else:
        if subdirectory:
            path = f"/raid/{request.user.username}/{directory}/{subdirectory}"
        else:
            path = f"/raid/{request.user.username}/{directory}"
    thumbnailed = False
    extension = file.split(".")[-1].lower()
    if extension in SUPPORTED_FORMATS:
        if extension in VIDEO_FORMATS:
            thumbnailed = True
            thumbnail = f"{uuid.uuid4()}.png"
            cmd = [
                "ffmpeg",
                "-i",
                f"{path}/{file}",
                "-ss",
                "00:00:00.000",
                "-vframes",
                "1",
                f"/raid/{thumbnail}",
            ]
            process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            process.wait()
            path = "/raid"
            file = thumbnail
            extension = "png"
        with Image.open(f"{path}/{file}") as img:
            with BytesIO() as buffered:
                if thumbnailed:
                    icon = Image.open("/raid/video_icon.png")
                    img.paste(icon, (0, 0), icon)
                img = img.resize(
                    (
                        150,
                        int((float(img.size[1]) * float((150 / float(img.size[0]))))),
                    ),
                    Image.Resampling.LANCZOS,
                )
                if extension == "jpg":
                    extension = "jpeg"
                img.save(buffered, extension)
                image_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        response = {"data": image_data}
        if thumbnailed:
            response["file"] = thumbnail
        else:
            response["file"] = ""
    else:
        response = {}
        response["file"] = ""
    return JsonResponse(response)


@login_required
def home(request, directory="", subdirectory=""):
    color = CssColor.objects.get(user=request.user)
    return render(request, "home.html", context={"preferred_color": color.color})


@login_required
def download(request, directory="", subdirectory="", file=""):
    if directory == "-":
        path = f"/raid/{request.user.username}/{file}"
    else:
        if subdirectory:
            path = f"/raid/{request.user.username}/{directory}/{subdirectory}/{file}"
        else:
            path = f"/raid/{request.user.username}/{directory}/{file}"
    return FileResponse(open(path, "rb"), as_attachment=True)


@login_required
def delete(request, directory, file):
    if directory == "-":
        path = f"/raid/{request.user.username}/{file}"
    else:
        path = f"/raid/{request.user.username}/{directory}/{file}"
    if not os.path.isdir(path):
        os.remove(path)
    else:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
        else:
            return JsonResponse({"data": "Folder contains files, cannot remove"})

    return JsonResponse({"data": "ok"})


@login_required
def delete_thumbnail(request, file):
    path = f"/raid/{file}"
    os.remove(path)
    return JsonResponse({"data": "ok"})


@login_required
def delete_all(request, directory, subdirectory=""):
    if subdirectory:
        path = f"/raid/{request.user.username}/{directory}/{subdirectory}"
    else:
        path = f"/raid/{request.user.username}/{directory}"
    for file in os.listdir(path):
        os.remove(path + "/" + file)
    messages.success(request, "Deletion Successful")
    return JsonResponse({"data": "ok"})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    color = CssColor.objects.get(user=request.user)
    return render(
        request, "change_password.html", {"form": form, "preferred_color": color.color}
    )


@login_required
def create_folder(request, name):
    if not os.path.isdir(f"/raid/{request.user.username}/{name}"):
        os.mkdir(f"/raid/{request.user.username}/{name}")
        messages.success(request, "Folder created")
    else:
        messages.success(request, "Folder already exists")
    return redirect("/home")


@login_required
def download_compressed(request, directory="", subdirectory=""):
    if subdirectory:
        path = f"/raid/{request.user.username}/{directory}/{subdirectory}.zip"
        filename = f"{subdirectory}.zip"
    else:
        path = f"/raid/{request.user.username}/{directory}.zip"
        filename = f"{directory}.zip"

    def generator(file_path, chunk_size=CHUNK_DEFAULT):
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    file_size = os.stat(path).st_size
    gen = generator(path)
    response = StreamingHttpResponse(gen)
    response["Content-Length"] = str(file_size)
    response["Content-Disposition"] = filename
    response["Content-Type"] = "application/zip"
    return response


@login_required
def compress_directory(request, directory="", subdirectory=""):
    if subdirectory:
        filename = f"/raid/{request.user.username}/{directory}/{subdirectory}"
    else:
        filename = f"/raid/{request.user.username}/{directory}"

    broken = False
    with zipfile.ZipFile(filename + ".zip", "w", zipfile.ZIP_STORED) as zipf:
        for root, dirs, files in os.walk(filename):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file), os.path.join(filename, "..")
                    ),
                )

    if broken:
        return JsonResponse({"data": "timeout"})
    else:
        return JsonResponse({"data": "ok"})


@login_required
def change_filename(request, directory, file, newname):
    if directory == "-":
        path = f"/raid/{request.user.username}"
    else:
        path = f"/raid/{request.user.username}/{directory}"
    os.rename(f"{path}/{file}", f"{path}/{newname}")
    return JsonResponse({"data": "ok"})


@login_required
def generate_share(request, directory, file):
    if directory == "-":
        path = f"/raid/{request.user.username}"
    else:
        path = f"/raid/{request.user.username}/{directory}"
    if os.path.isdir(os.path.join(path, file)):
        dir = os.path.join(path, file).encode()
        file += ".zip"
        zip = os.path.join(path, file).encode()
        cmd = ["zip", "-0", "-r", zip, dir]
        process = subprocess.Popen(cmd)
        process.wait()
    file_id = str(uuid.uuid4())
    shutil.copy(os.path.join(path, file), f"/raid/shared/{file}")
    os.remove(os.path.join(path, file))
    record = SharedFile(
        path=f"/raid/shared/{file}",
        file_id=file_id,
        created=timezone.now(),
        user=request.user,
    )
    record.save()
    return HttpResponse(f"/shared_file/{file_id}")


def shared_file(request, file_id):
    entry = SharedFile.objects.get(file_id=file_id)
    return FileResponse(open(entry.path, "rb"), as_attachment=True)


@login_required
def upload(request):
    if request.method == "POST":
        user = request.user
        directory = request.POST.get("directory")
        if directory == "-":
            directory = ""
        filename = request.POST.get("filename")
        filedata = request.POST.get("file")
        handle_uploaded_file(filedata, user.username, directory, filename)
        return JsonResponse({"status": "uploaded"})
    else:
        raise PermissionDenied


@login_required
def load_files(request):
    if request.method != "POST":
        raise PermissionDenied

    directory = request.POST.get("directory")

    files = {}
    directories = {}
    if directory == "-":
        path = f"/raid/{request.user.username}"
    else:
        path = f"/raid/{request.user.username}/{directory}"
    path = unquote(path)
    for file in os.listdir(path):
        if os.path.isdir(f"{path}/{file}"):
            dir_size = 0
            unit = "MB"
            for file2 in os.listdir(f"{path}/{file}"):
                if os.path.isdir(f"{path}/{file}/{file2}"):
                    dir_size2 = 0
                    for file3 in os.listdir(f"{path}/{file}/{file2}"):
                        dir_size2 += os.path.getsize(
                            f"{path}/{file}/{file2}/{file3}"
                        ) / (1024 * 1024)
                    dir_size += dir_size2
                else:
                    dir_size += os.path.getsize(f"{path}/{file}/{file2}") / (
                        1024 * 1024
                    )
            if dir_size > 1024:
                dir_size = dir_size / 1024
                unit = "GB"
            entry = LocalShare.objects.filter(path_org=f"{path}/{file}")
            if entry.exists():
                directories[file] = (
                    "directory",
                    f"{round(dir_size, 2)}{unit}",
                    "shared",
                )
            else:
                directories[file] = ("directory", f"{round(dir_size, 2)}{unit}", "")
        else:
            size = os.path.getsize(f"{path}/{file}") / (1024 * 1024)
            unit = "MB"
            if size > 1024:
                size = size / 1024
                unit = "GB"
            files[file] = ("", f"{round(size, 2)}{unit}")

    directories = {
        k: v for k, v in sorted(directories.items(), key=lambda item: item[0].lower())
    }
    files = {k: v for k, v in sorted(files.items(), key=lambda item: item[0])}
    if directory == "-":
        temp = directories["shared"]
        first = {"shared": temp}
        del directories["shared"]
    else:
        first = {}
    first.update(directories)
    first.update(files)
    context = {"files": first}
    return JsonResponse(context)


@login_required
def filename(request):
    if request.method == "POST":
        user = request.user
        directory = request.POST.get("directory")
        filename = request.POST.get("filename")
        if directory == "-":
            present = os.path.isfile(f"/raid/{user.username}/{filename}")
        else:
            present = os.path.isfile(f"/raid/{user.username}/{directory}/{filename}")
        return JsonResponse({"present": present})
    else:
        raise PermissionDenied


@login_required
def shared_links(request):
    links = SharedFile.objects.filter(user=request.user).all()
    data = {}
    for i, link in enumerate(links):
        data[i] = {"file_id": link.file_id, "path": link.path, "created": link.created}
    return JsonResponse(data)


@login_required
def remove_shared_link(request, file_id):
    entry = SharedFile.objects.get(file_id=file_id, user=request.user)
    os.remove(entry.path)
    entry.delete()
    return JsonResponse({"data": "ok"})


@login_required
def list_users(request):
    users = list(User.objects.all())
    users.remove(request.user)
    users.remove(User.objects.get(username="root"))
    users = [user.username for user in users]
    return JsonResponse({"data": users})


@login_required
def local_share(request):
    if request.method != "POST":
        raise PermissionDenied

    user = request.user
    directory = unquote(request.POST.get("directory"))
    reciever = User.objects.get(username=request.POST.get("reciever"))

    src = f"/raid/{user.username}/{directory}"
    dst = f"/raid/{reciever.username}/shared/{directory}"

    if LocalShare.objects.filter(path_remote=dst).exists():
        return JsonResponse({"data": "folder is already shared"})

    os.symlink(src, dst)

    entry = LocalShare()
    entry.sender = user
    entry.receiver = reciever
    entry.path_org = src
    entry.path_remote = dst
    entry.save()
    return JsonResponse({"data": "ok"})


@login_required
def shared_files(request):
    if request.method == "POST":
        raise PermissionDenied
    shares = LocalShare.objects.filter(sender=request.user)
    data = {}
    for i, share in enumerate(shares):
        data[i] = {
            "sender": share.sender.username,
            "receiver": share.receiver.username,
            "path_org": share.path_org,
            "path_remote": share.path_remote,
            "pk": share.pk,
            "path_toshow": share.path_org.replace(
                f"/raid/{request.user.username}/", ""
            ),
        }
    return JsonResponse(data=data)


@login_required
def stop_share(request, pk):
    share = LocalShare.objects.get(pk=pk)
    os.unlink(share.path_remote)
    share.delete()
    return HttpResponse("")


@login_required
def file_size(request, shared="", directory="", file=""):
    if directory == "-":
        if shared:
            path = f"/raid/{request.user.username}/shared/{file}"
        else:
            path = f"/raid/{request.user.username}/{file}"
    else:
        if shared:
            path = f"/raid/{request.user.username}/shared/{directory}/{file}"
        else:
            path = f"/raid/{request.user.username}/{directory}/{file}"

    data = {"data": os.stat(path).st_size}
    return JsonResponse(data)


@login_required
def display_media(request, shared="", directory="", file=""):
    if directory == "-":
        if shared:
            path = f"/raid/{request.user.username}/shared"
        else:
            path = f"/raid/{request.user.username}"
    else:
        if shared:
            path = f"/raid/{request.user.username}/shared/{directory}"
        else:
            path = f"/raid/{request.user.username}/{directory}"

    path_full = f"{path}/{file}"
    extension = file.split(".")[-1].lower()
    file_size = os.stat(path_full).st_size
    if file_size <= CHUNK_DEFAULT:
        with open(path_full, "rb") as f:
            encoded_data = base64.b64encode(f.read()).decode("utf-8")
        content_type = "text/html"
        if extension in SUPPORTED_FORMATS:
            if extension in VIDEO_FORMATS:
                content_type = f"video/{extension}"
            elif extension in IMAGE_FORMATS:
                content_type = f"image/{extension}"
        return JsonResponse({"data": encoded_data, "content_type": content_type})
    else:

        def generator(file_path, chunk_size=CHUNK_DEFAULT):
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        file_size = os.stat(path_full).st_size
        gen = generator(path_full)
        response = StreamingHttpResponse(gen)
        response["content-length"] = str(file_size)
        content_type = "text/html"
        if extension in SUPPORTED_FORMATS:
            if extension in VIDEO_FORMATS:
                content_type = f"video/{extension}"
            elif extension in IMAGE_FORMATS:
                content_type = f"image/{extension}"
        response["content-type"] = content_type
        return response


@login_required
def unlink_directory(request, directory=""):
    path = f"/raid/{request.user.username}/shared/{directory}"
    os.unlink(path)
    entry = LocalShare.objects.get(path_remote=path)
    entry.delete()
    return JsonResponse({"data": "ok"})


@staff_member_required
def system_stats(request):

    def get_system_metrics():

        disk_usage = psutil.disk_usage("/raid")
        disk_total = disk_usage.total / 1024 / 1024 / 1024
        disk_used = disk_usage.used / 1024 / 1024 / 1024

        photo_count = sum([len(files) for _, _, files in os.walk("/raid")])

        return {
            "disk_total": disk_total,
            "disk_used": disk_used,
            "photo_count": photo_count,
        }

    def get_object_metrics():
        local_share_count = 0
        for local_share in LocalShare.objects.all():
            try:
                local_share_count += len(os.listdir(local_share.path_org))
            except:
                pass
        shared_file_count = SharedFile.objects.all().count()

        return {
            "local_share_count": local_share_count,
            "shared_file_count": shared_file_count,
        }

    def get_directory_size(directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

    def get_user_metrics(user):
        local_shares_count = 0
        for local_share in LocalShare.objects.filter(sender=user):
            try:
                local_shares_count += len(os.listdir(local_share.path_org))
            except:
                pass
        disk_usage = get_directory_size(f"/raid/{user.username}") / 1024 / 1024 / 1024
        files_num = sum(
            [len(files) for _, _, files in os.walk(f"/raid/{user.username}")]
        )

        return {
            "files": files_num,
            "disk": disk_usage,
            "shares": local_shares_count,
            "username": user.username,
        }

    user_metrics = []
    for user in User.objects.all():
        um = get_user_metrics(user)
        if um["files"] > 0:
            user_metrics.append(um)

    color = CssColor.objects.get(user=request.user)
    return render(
        request,
        "system_stats.html",
        context={
            **get_object_metrics(),
            **get_system_metrics(),
            "user_metrics": user_metrics,
            "preffered_color": color,
        },
    )


@login_required
def save_color(request, color):
    entry = CssColor.objects.filter(user=request.user)
    if entry.exists():
        entry = entry.first()
        entry.color = color
        entry.save()
    else:
        entry = CssColor()
        entry.user = request.user
        entry.color = color
        entry.save()
    return JsonResponse({"data": "ok"})


@login_required
def get_file_info(request, shared="", directory="", file=""):
    if directory == "-":
        if shared:
            path = f"/raid/{request.user.username}/shared/{file}"
        else:
            path = f"/raid/{request.user.username}/{file}"
    else:
        if shared:
            path = f"/raid/{request.user.username}/shared/{directory}/{file}"
        else:
            path = f"/raid/{request.user.username}/{directory}/{file}"

    data = {"filesize": os.stat(path).st_size, "lastmodified": os.stat(path).st_mtime}
    return JsonResponse(data)
