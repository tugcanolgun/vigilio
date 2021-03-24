import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path, PosixPath
from typing import Any, Dict, List, Set, Optional

import requests
from django.conf import settings
from qbittorrent import Client

from panel.models import MovieTorrent
from panel.tasks.inmemory import get_setting, get_setting_or_environment
from panel.tasks.moviedb import download_movie_info
from panel.tasks.subtitles import fetch_subtitles
from stream.models import Movie, MovieContent
from watch.celery import app

logger = logging.getLogger(__name__)


@dataclass
class VideoDetail:
    full_path: str
    file_name: str
    file_extension: str
    source_file_name: str
    source_file_extension: str
    duration: int
    width: int
    height: int
    raw: Dict[str, List[Dict[str, Any]]]


def _get_qbittorrent_url() -> str:
    url: Optional[str] = get_setting("QBITTORRENT_URL")
    if not url:
        raise Exception("QBITTORRENT_URL could not be found or empty.")

    return url


def get_qbittorrent_client() -> Client:
    _url: str = _get_qbittorrent_url()
    try:
        client = Client(_url, verify=False)
    except requests.exceptions.ConnectionError:
        raise Exception("Qbittorrent is not running.")

    _login: Optional[str] = client.login(
        get_setting_or_environment("QBITTORRENT_USERNAME"),
        get_setting_or_environment("QBITTORRENT_PASSWORD"),
    )
    if _login is None:
        return client

    raise Exception("Could not login to qbittorrent.")


def get_file_content_from_url(source: str) -> bytes:
    # TODO: Check errors
    return requests.get(source).content


def is_torrent_complete(movie_torrent_id: int) -> bool:
    client: Client = get_qbittorrent_client()
    torrent: List[Dict[str, Any]] = client.torrents(category=str(movie_torrent_id))

    if len(torrent) == 0:
        raise Exception(
            f"Movie torrent {movie_torrent_id} does not have any torrent associated with"
        )

    # TODO: What happens if the torrent is deleted? Handle it gracefully.
    if torrent[0]["progress"] != 1:
        return False

    return True


def _get_videos_from_path(root: PosixPath) -> Set[PosixPath]:
    suffixes: Set[str] = {".mp4", ".mkv"}
    videos_raw: Set[PosixPath] = set()

    def _check_folder(path: PosixPath) -> None:
        for _content in path.iterdir():
            if _content.is_dir():
                _check_folder(_content)

            if _content.suffix.lower() in suffixes:
                videos_raw.add(_content)

    _check_folder(root)

    return videos_raw


def get_videos_from_folder(root_path: str) -> Set[PosixPath]:
    videos_raw: Set[PosixPath] = set()
    root: PosixPath = Path(root_path)
    if root.is_file():
        if root.suffix.lower() not in {".mp4", ".mkv"}:
            raise Exception(f"Given single file is not a video: {root_path}")
        videos_raw.add(root)
    else:
        videos_raw.update(_get_videos_from_path(root))

    return videos_raw


def _get_video_raw_detail(video: Path) -> Dict[str, List[Dict[str, Any]]]:
    if not video.is_file():
        return {}

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            str(video),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        return json.loads(result.stdout)
    except json.decoder.JSONDecodeError:
        logger.critical(f"Could not get media info from {str(video)}")
        return {}


def _hash(input: str) -> str:
    return hex(abs(hash(input)))[2:]


def _convert_video_to_mp4(video: Path) -> None:
    new_video_name: str = _hash(video.name) + ".mp4"
    new_video_path: Path = video.parent / new_video_name

    subprocess.run(
        ["ffmpeg", "-i", str(video), "-c", "copy", str(new_video_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _get_video_detail(video: PosixPath) -> VideoDetail:
    raw_info: Dict[str, List[Dict[str, Any]]] = _get_video_raw_detail(video)
    new_file_extension: str = ".mp4"
    new_file_name: str = _hash(video.name)
    new_file_path: PosixPath = video.parent / (new_file_name + new_file_extension)

    return VideoDetail(
        full_path=str(new_file_path),
        file_name=new_file_name,
        file_extension=new_file_extension,
        source_file_name=video.name,
        source_file_extension=video.suffix.lower(),
        width=int(raw_info.get("streams", [{}])[0].get("width", "0")),
        height=int(raw_info.get("streams", [{}])[0].get("height", "0")),
        duration=int(float(raw_info.get("streams", [{}])[0].get("duration", "0"))),
        raw=raw_info,
    )


def _copy_mp4_to_new_hash_mp4(video: Path) -> None:
    new_video_name: str = _hash(video.name) + ".mp4"
    new_video_path: Path = video.parent / new_video_name

    shutil.copy2(str(video), str(new_video_path))


def _create_and_write_to_meta_file(file_path: PosixPath) -> None:
    meta = file_path.parent / "meta.txt"
    meta.touch()
    with open(str(meta), "a") as f:
        f.write(file_path.name)
        f.write("\n")


def _process_videos(
    videos: Set[PosixPath], delete_original: bool = False
) -> List[VideoDetail]:
    video_details: List[VideoDetail] = []
    for video in videos:
        if video.suffix.lower() == ".mkv":
            _convert_video_to_mp4(video)
        elif video.suffix.lower() == ".mp4":
            _copy_mp4_to_new_hash_mp4(video)

        video_detail: VideoDetail = _get_video_detail(video)

        if delete_original:
            _create_and_write_to_meta_file(file_path=video)
            if video.is_file():
                os.remove(str(video))

        video_details.append(video_detail)

    return video_details


def _is_delete_original_files() -> bool:
    setting: Optional[bool] = get_setting("DELETE_ORIGINAL_FILES")
    if setting:
        return setting

    return False


def _get_media_folder() -> str:
    if not hasattr(settings, "MEDIA_FOLDER"):
        raise Exception("MEDIA_FOLDER is not set in the settings.")

    if settings.MEDIA_FOLDER == "" or settings.MEDIA_FOLDER is None:
        raise Exception("MEDIA_FOLDER is empty. Set a media folder in the settings.")

    if not Path(settings.MEDIA_FOLDER).is_dir():
        raise Exception(
            f"{settings.MEDIA_FOLDER} is not a folder. Set MEDIA_FOLDER in the settings."
        )

    return settings.MEDIA_FOLDER


def _get_root_folder(root_folder: PosixPath) -> Optional[PosixPath]:
    folders: List[PosixPath] = [
        root_folder,
        Path(str(settings.BASE_DIR) + str(root_folder)),
    ]
    for folder in folders:
        if folder.is_dir():
            return folder
        if root_folder.is_file():
            logger.error(f"{root_folder} is a file.")

    return None


def _change_and_move_parent_folder(root_folder: str) -> str:
    root: Optional[PosixPath] = _get_root_folder(root_folder=Path(root_folder))
    if not root:
        return root_folder

    media_folder: str = _get_media_folder()

    name: str = root.name
    new_folder_name: str = _hash(name)
    new_folder_path: str = str(Path(media_folder) / new_folder_name)

    shutil.move(str(root), new_folder_path)

    return new_folder_path


def _get_relative_path(full_path: str) -> str:
    if not full_path:
        return full_path

    media_folder: str = _get_media_folder()
    if not full_path.startswith(media_folder):
        return full_path

    path: PosixPath = Path(full_path)

    return str(path.relative_to(Path(media_folder)))


@app.task(bind=True, max_retries=10000, time_limit=1800)
def check_and_process_torrent(self, movie_torrent_id: int) -> None:
    logger.info(f"Checking download process for {movie_torrent_id}")
    try:
        torrent_obj: MovieTorrent = MovieTorrent.objects.get(id=movie_torrent_id)
    except MovieTorrent.DoesNotExist:
        logger.critical(f"MovieTorrent {movie_torrent_id} does not exists")
        raise Exception(f"MovieTorrent {movie_torrent_id} does not exists")

    if torrent_obj.is_complete:
        logger.info(f"Download is complete for {movie_torrent_id}")
        return

    if not is_torrent_complete(movie_torrent_id=movie_torrent_id):
        self.retry(countdown=15)

    torrent_obj.is_complete = True
    torrent_obj.save()

    client: Client = get_qbittorrent_client()
    torrent: Dict[str, Any] = client.torrents(category=str(movie_torrent_id))[0]
    root_path: str = _change_and_move_parent_folder(torrent["content_path"])

    torrent_obj.movie_content.full_path = root_path
    torrent_obj.movie_content.main_folder = _get_relative_path(root_path)
    torrent_obj.movie_content.save()

    process_videos_in_folder.delay(
        movie_content_id=torrent_obj.movie_content.id,
        delete_original=_is_delete_original_files(),
    )


def _get_root_path(movie_content_id: int) -> str:
    movie_content: MovieContent = MovieContent.objects.get(id=movie_content_id)
    if movie_content.full_path and Path(movie_content.full_path).is_dir():
        return movie_content.full_path

    if movie_content.main_folder:
        folder: PosixPath = Path(_get_media_folder()) / Path(movie_content.main_folder)
        if folder.is_dir():
            return str(folder)

    if movie_content.full_path and Path(movie_content.full_path).is_file():
        return str(Path(movie_content.full_path).parent)

    torrent_obj: MovieTorrent = MovieTorrent.objects.filter(
        movie_content_id=movie_content_id
    ).last()
    if not torrent_obj:
        raise Exception(f"MovieTorrent could not be found for {movie_content_id}")

    client: Client = get_qbittorrent_client()
    torrent: List[Dict[str, Any]] = client.torrents(category=str(torrent_obj.id))
    if not torrent:
        raise Exception(
            f"Torrent could not be found for movie content: {movie_content_id}"
        )

    folder: PosixPath = Path(torrent[0]["content_path"])
    if folder.is_dir():
        return str(folder)

    if folder.is_file():
        folder = folder.parent

    if (Path(_get_media_folder()) / _hash(folder.name)).is_dir():
        return str(Path(_get_media_folder()) / _hash(folder.name))


@app.task
def process_videos_in_folder(
    movie_content_id: int, delete_original: bool = False
) -> None:
    root_path: str = _get_root_path(movie_content_id=movie_content_id)

    videos: Set[PosixPath] = get_videos_from_folder(root_path=root_path)
    processed_videos: List[VideoDetail] = _process_videos(
        videos=videos, delete_original=delete_original
    )

    video_detail: Optional[VideoDetail] = None

    if not processed_videos:
        logger.critical(
            f"No videos are returned to be processed for movie content {movie_content_id}"
        )
        raise Exception(
            f"No videos are returned to be processed for movie content {movie_content_id}"
        )
    elif len(processed_videos) > 1:
        duration: int = -1

        for _video in processed_videos:
            if _video.duration > duration:
                duration = _video.duration
                video_detail = _video

    if not video_detail:
        video_detail = processed_videos[0]

    movie_content: MovieContent = MovieContent.objects.get(id=movie_content_id)
    movie: Movie = movie_content.movie_set.first()

    movie_content.full_path = video_detail.full_path
    movie_content.relative_path = _get_relative_path(video_detail.full_path)
    movie_content.file_name = video_detail.file_name
    movie_content.file_extension = video_detail.file_extension
    movie_content.source_file_name = video_detail.source_file_name
    movie_content.source_file_extension = video_detail.source_file_extension
    movie_content.resolution_width = video_detail.width
    movie_content.resolution_height = video_detail.height
    movie_content.is_ready = True
    movie_content.raw_info = video_detail.raw
    movie.duration = video_detail.duration

    movie_content.save()
    movie.save()

    os.chmod(video_detail.full_path, 0o644)

    fetch_subtitles.delay(
        movie_content_id=movie_content.id,
        limit=5,
        delete_original=_is_delete_original_files(),
    )


@app.task
def download_torrent(movie_content_id: int) -> None:
    logger.info("Torrent download process has started")
    try:
        content: MovieContent = MovieContent.objects.get(id=movie_content_id)
    except MovieContent.DoesNotExist:
        logger.critical(f"MovieContent {movie_content_id} does not exist.")
        raise

    client: Client = get_qbittorrent_client()
    torrent_obj: MovieTorrent = MovieTorrent.objects.create(
        movie_content_id=movie_content_id,
    )
    client.remove_category(str(torrent_obj.id))
    client.create_category(str(torrent_obj.id))
    source: str = content.torrent_source

    if source.startswith("magnet"):
        client.download_from_link(source, category=str(torrent_obj.id))
        torrent_obj.source = source
    else:
        _content: bytes = get_file_content_from_url(source)
        client.download_from_file(_content, category=str(torrent_obj.id))
        torrent_obj.source = str(_content)

    torrent: List[Dict[str, Any]] = client.torrents(category=str(torrent_obj.id))
    if torrent:
        torrent_obj.name = torrent[0]["name"]
        torrent_obj.save()

    logger.info("Torrent downloading process successfully initiated.")
    check_and_process_torrent.delay(torrent_obj.id)
    download_movie_info.delay(movie_id=content.movie_set.first().id)
