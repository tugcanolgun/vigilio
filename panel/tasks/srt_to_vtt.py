import logging
import re
from pathlib import Path, PosixPath
from typing import Optional


logger = logging.getLogger(__name__)


def convert_srt_cue(caption: str) -> str:
    cue: str = ""
    lines: list = caption.split("\n")

    if len(caption) <= 1:
        return ""

    line: int = 0

    if not re.match(r"\d+:\d+:\d+", lines[0]) and re.match(r"\d+:\d+:\d+", lines[1]):
        cue += re.match(r"\w+", lines[0]).group() + "\n"
        line += 1

    while True:
        if re.match(r"\d+:\d+:\d+", lines[line]):
            match = re.match(
                r"(\d+):(\d+):(\d+)(?:,(\d+))?\s*--?>\s*(\d+):(\d+):(\d+)(?:,(\d+))?",
                lines[line],
            )
            if match:
                m = match.groups()
                cue += f"{m[0]}:{m[1]}:{m[2]}.{m[3]} --> {m[4]}:{m[5]}:{m[6]}.{m[7]}{lines[line][match.end():]}\n"
                line += 1
            else:
                return ""
        else:
            break

    if len(lines[line:]) > 1:
        for content in lines[line + 1 :]:
            lines[line] += f"\n{content}"

        lines = lines[: line + 1]

    if lines[line]:
        if "-->" in lines[line]:
            lines[line] = lines[line].replace("-->", " ->")
        cue += lines[line] + "\n\n"

    return cue


def string_to_vtt(data: str) -> str:
    data = re.sub(r"\r+/g", "", data)
    data = re.sub(r"^\s+|\s+$/g", "", data)

    cue_list: list = data.split("\n\n")
    result: str = ""

    if len(cue_list) > 1:
        result += "WEBVTT\n\n"
        for cue in cue_list:
            result += convert_srt_cue(cue)

    return result


def convert_srt_to_vtt(
    input_file: str, output_file: Optional[str] = None, ignore_errors: bool = False
) -> None:
    try:
        _input: PosixPath = Path(input_file)
        if not _input.is_file():
            raise FileNotFoundError(f"{input_file} could not be found.")

        if not output_file:
            output_file = f"{_input.parent / _input.stem}.vtt"

        with open(input_file, "r", encoding="utf-8-sig", errors="ignore") as f:
            result: str = string_to_vtt(f.read())

        with open(output_file, "w") as f:
            f.write(result)
    except Exception:
        logger.exception(f"Failed to convert {input_file}")
        if not ignore_errors:
            raise
