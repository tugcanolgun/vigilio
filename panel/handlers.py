import logging
from typing import Dict, List

from panel.api.utils import get_dotenv_values
from panel.tasks.inmemory import get_setting
from panel.tasks.setup_panel import is_command_installed

logger = logging.getLogger(__name__)


def get_installation_status() -> Dict[str, List[str]]:
    commands: Dict[str, List[str]] = {}

    if is_command_installed("ffmpeg"):
        commands["ffmpeg"] = ["INSTALLED"]
    else:
        commands["ffmpeg"] = [
            "ffmpeg is not installed. Cannot add new media without this tool.",
            "sudo apt install ffmpeg / brew install ffmpeg",
        ]

    if is_command_installed("ffprobe"):
        commands["ffprobe"] = ["INSTALLED"]
    else:
        commands["ffprobe"] = [
            "ffprobe is not installed. Cannot gather media information without this tool.",
            "This tool is a part of ffmpeg.",
            "sudo apt install ffmpeg / brew install ffmpeg",
        ]

    return commands


def is_demo() -> bool:
    demo: bool = get_setting("DEMO")
    if demo:
        return demo

    return False


def are_settings_filled() -> bool:
    _envs: Dict[str, str] = get_dotenv_values()
    if _envs.get("MOVIEDB_API", "") == "":
        return False

    return True
