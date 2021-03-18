import os

from django.conf import settings


def _get_relative_path(full_path: str) -> str:
    if not hasattr(settings, "MEDIA_FOLDER"):
        return full_path

    return full_path.replace(settings.MEDIA_FOLDER, "")


def _get_url(full_path: str, relative_path: str = "") -> str:
    if not full_path:
        return full_path

    if full_path.startswith("http"):
        return full_path

    if relative_path:
        return os.environ.get("DOWNLOAD_URI", "") + relative_path
    else:
        return os.environ.get("DOWNLOAD_URI", "") + _get_relative_path(
            full_path=full_path
        )


def _get_quality_string(resolution_width: int) -> str:
    if resolution_width > 2000:
        return "4K"
    elif 2000 >= resolution_width > 1500:
        return "HD"
    elif 1500 >= resolution_width > 0:
        return "HDTV"
    else:
        return "UNK"
