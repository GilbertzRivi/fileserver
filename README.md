# Project Overview
This project is a file management web application built using Django. It provides features for file uploads, sharing, and management.

## Features
- **Authentication**: Login, logout, and password change functionality.
- **File Management**: Upload, download, delete, and rename files.
- **Folder Management**: Create, delete, and compress folders.
- **File Sharing**: Share files and folders with other users, including local and remote shares.
- **Thumbnail Generation**: Generate thumbnails for supported media formats.
- **System Stats**: Monitor disk usage, shared file count, and user-specific metrics.

## Supported Formats
- **Video**: `mp4`, `webm`
- **Image**: `png`, `jpg`, `jpeg`, `gif`, `webp`
- other formats wont be displayed in the web

## Usage
### Key Endpoints
- **Home**: `/home/` - Displays user files and folders.
- **Sign In**: `/login/` - User authentication.
- **Sign Out**: `/logout/` - End user session.
- **File Upload**: `/upload/` - Handles file uploads.
- **Download**: `/download/<directory>/<file>/` - Download files.
- **Generate Thumbnail**: `/get_thumbnail/<directory>/<file>/` - Generate media thumbnails.
- **System Stats**: `/system_stats/` - View admin system metrics.

## Contributing
Contributions are welcome! Please submit a pull request with a detailed description of the changes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
