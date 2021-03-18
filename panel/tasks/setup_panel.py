import shutil


def is_command_installed(command: str) -> bool:
    return True if shutil.which(command) else False


def is_panel_ready() -> bool:
    return is_command_installed("ffmpeg") and is_command_installed("ffprobe")
