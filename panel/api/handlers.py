import json
import logging
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import PosixPath, Path
from typing import Dict, Optional, Set, List, Any, Union

from celery.app.control import Inspect
from django.contrib.auth.models import User
from django.db.models import QuerySet
from qbittorrent import Client
from requests.exceptions import ConnectionError
from rest_framework.exceptions import NotFound, APIException

from panel.api.serializers import (
    TorrentProcess,
    MovieManagement,
    MovieCommands,
    FilesData,
    FileCommands,
)
from panel.api.utils import get_celery_nodes, is_qbittorrent_running, is_redis_online
from panel.models import MovieTorrent
from panel.tasks.torrent import get_qbittorrent_client, _get_media_folder
from stream.api.serializers import MoviesEndpointData, MoviesEndpointCommands
from stream.models import Movie, MovieContent, UserMovieHistory, MovieSubtitle, MyList
from watch.celery import app

logger = logging.getLogger(__name__)


@dataclass
class FilesResult:
    files: List[Dict[str, Any]]
    missing_files: Set[str]
    used_files: List[str]


class TorrentProcessHandler:
    def __init__(self):
        self._client: Optional[Client] = None

    def handle(self, torrent_process: TorrentProcess) -> Dict[str, str]:
        self._check_hashes(info_hashes=torrent_process.info_hashes)

        if torrent_process.command == "pause":
            self.client.pause_multiple(infohash_list=torrent_process.info_hashes)
        elif torrent_process.command == "resume":
            self.client.resume_multiple(infohash_list=torrent_process.info_hashes)
        elif torrent_process.command == "force_start":
            self.client.force_start(
                infohash_list=torrent_process.info_hashes, value=True
            )
        elif torrent_process.command == "delete":
            self.client.delete(infohash_list=torrent_process.info_hashes)
        elif torrent_process.command == "delete_permanent":
            self.client.delete_permanently(infohash_list=torrent_process.info_hashes)

        return {"status": "success"}

    def _check_hashes(self, info_hashes: List[str]) -> None:
        _hashes: Set[str] = set(info_hashes)
        _torrents: Set[str] = {
            torrent.get("hash") for torrent in self.client.torrents()
        }
        if not _torrents.issuperset(_hashes):
            raise NotFound("Given hash list could not be found.")

    @property
    def client(self) -> Client:
        if not self._client:
            try:
                self._client = get_qbittorrent_client()
            except ConnectionError:
                raise APIException("Qbittorrent connection failed.")

        return self._client


class FilesHandler:
    def __init__(self) -> None:
        self.db_files: Set[str] = set()
        self.found_files: Set[str] = set()

    def handle(
        self, files_data: FilesData, is_get: bool = True
    ) -> Union[FilesResult, str]:
        if is_get:
            return self.get(files_data=files_data)
        else:
            return self.post(files_data=files_data)

    def get(self, files_data: FilesData) -> FilesResult:
        movie: Movie = Movie.objects.get(id=files_data.movie_id)

        media_folder: PosixPath = Path(_get_media_folder())
        files: Dict[str, Any] = self.get_item_dict(
            item=media_folder, relative=media_folder.parent
        )
        self.db_files = self._get_db_files(movie=movie)

        for movie_content in movie.movie_content.all():
            _files: Dict[str, Any] = self.get_files(
                movie_content=movie_content, media_folder=media_folder
            )
            if _files:
                files.get("files").append(_files)

        if not files.get("files", []):
            files = []

        return FilesResult(
            files=[files],
            missing_files=self.db_files.difference(self.found_files),
            used_files=list(self.db_files),
        )

    def post(self, files_data: FilesData) -> str:
        if files_data.command == FileCommands.delete_files.value:
            return self._remove_files(files=files_data.files)

    def _remove_files(self, files: List[Dict[str, Any]]) -> str:
        for _f in files:
            path: PosixPath = Path(_f.get("full_path"))
            if not path.exists():
                raise NotFound(f"{str(path)} could not be found.")

            if path.is_dir():
                logger.info(f"{str(path)} removing the directory.")
                shutil.rmtree(str(path), ignore_errors=True)
            elif path.is_file():
                logger.info(f"{str(path)} removing the file.")
                os.remove(str(path))

        return "Files have been removed."

    def get_files(
        self, movie_content: MovieContent, media_folder: PosixPath
    ) -> Dict[str, Any]:
        try:
            main_folder: PosixPath = self._get_main_folder(
                movie_content=movie_content, media_folder=media_folder
            )
        except APIException:
            logger.critical(
                f"Could not get main folder for Movie Content {movie_content.id}"
            )
            return {}

        return self.get_hierarchy_of_folder(
            main_folder=main_folder, relative_folder=media_folder
        )

    def _get_main_folder(
        self, movie_content: MovieContent, media_folder: PosixPath
    ) -> PosixPath:
        if (
            movie_content.main_folder
            and (media_folder / movie_content.main_folder).is_dir()
        ):
            return media_folder / movie_content.main_folder
        elif movie_content.full_path and movie_content.full_path.startswith("/"):
            full_path: PosixPath = Path(movie_content.full_path)
            if not full_path.exists():
                raise APIException(f"{str(full_path)} could not be located.")

            if full_path.is_file():
                return full_path.parent
            else:
                return full_path

        raise APIException(
            f"Could not find a folder associated with movie content {movie_content.id}"
        )

    def get_item_dict(
        self, item: PosixPath, relative: Optional[PosixPath] = None
    ) -> Dict[str, Any]:
        is_file: bool = item.is_file()
        _dict: Dict[str, Any] = {
            "name": item.name,
            "full_path": str(item),
            "type": "file" if is_file else "folder",
            "size": item.stat().st_size,
            "date": datetime.fromtimestamp(item.stat().st_ctime).date(),
        }
        if is_file:
            _dict["suffix"] = item.suffix
            _dict["used"] = str(item) in self.db_files
        else:
            _dict["files"] = []

        if relative:
            _dict["relative_path"] = str(item.relative_to(Path(relative.parent)))

        self.found_files.add(str(item))

        return _dict

    def get_hierarchy_of_folder(
        self, main_folder: PosixPath, relative_folder: PosixPath
    ) -> Dict[str, Any]:
        files: Dict[str, Any] = self.get_item_dict(
            item=main_folder, relative=relative_folder
        )

        self.iter_dir(folder=main_folder, parent=files, relative=relative_folder)

        return files

    def iter_dir(
        self, folder: PosixPath, parent: Dict[str, Any], relative: PosixPath
    ) -> None:
        _folders: Set = set()
        for _f in folder.iterdir():
            if _f.is_dir():
                _folders.add(_f)
                continue

            if _f.is_file():
                parent["files"].append(self.get_item_dict(item=_f, relative=relative))

        for _f in _folders:
            _folder = self.get_item_dict(item=_f, relative=relative)
            parent["files"].append(_folder)
            self.iter_dir(folder=_f, parent=_folder, relative=relative)

    def _get_db_files(self, movie: Movie) -> Set[str]:
        db_files: Set = set()
        for content in movie.movie_content.all():
            if content.full_path:
                db_files.add(content.full_path)
            for subtitle in content.movie_subtitle.all():
                if subtitle.full_path:
                    db_files.add(subtitle.full_path)

        return db_files


class MovieManagementHandler:
    def handle(self, management: MovieManagement, user: User) -> str:
        if management.command == MovieCommands.delete_continue.value:
            return self._delete_continue(movie_id=management.id, user=user)
        elif management.command == MovieCommands.delete_everything.value:
            return self._delete_everything(movie_id=management.id)

        raise APIException(
            f"Failed for following args: {json.dumps(asdict(management))}"
        )

    def _delete_continue(self, movie_id: int, user: User) -> str:
        history: UserMovieHistory = UserMovieHistory.objects.filter(
            user=user, movie_id=movie_id
        )
        history.delete()

        return "Movie has been deleted from the user's history."

    def _delete_everything(self, movie_id: int) -> str:
        movie: Movie = Movie.objects.get(id=movie_id)
        movie_contents: "QuerySet[MovieContent]" = movie.movie_content.all()
        torrent_objs: "QuerySet[MovieTorrent]" = MovieTorrent.objects.filter(
            movie_content__in=movie_contents
        ).all()
        subtitles: List[MovieSubtitle] = self._get_subtitles(
            movie_contents=movie_contents
        )

        self._remove_torrents_and_files(torrent_objs=torrent_objs)
        try:
            self._cancel_celery_processes(torrents=torrent_objs)
        except Exception:
            logger.exception(f"Could not stop celery processes for movie id {movie_id}")

        for content in movie_contents:
            if content.main_folder:
                shutil.rmtree(content.main_folder, ignore_errors=True)

        for obj in [*subtitles, *torrent_objs, *movie_contents, movie]:
            obj.delete()

        return "Everything has been deleted."

    def _remove_torrents_and_files(
        self, torrent_objs: "QuerySet[MovieTorrent]"
    ) -> None:
        if not is_qbittorrent_running():
            return

        client: Client = get_qbittorrent_client()
        for torrent in torrent_objs:
            _res: List[Dict[str, Any]] = client.torrents(category=str(torrent.id))
            client.delete_permanently(
                infohash_list=self._get_hash_from_client_result(torrent=_res)
            )

    def _get_hash_from_client_result(self, torrent: List[Dict[str, Any]]) -> List[str]:
        hashes: List[str] = []
        for _t in torrent:
            if _t.get("hash", False):
                hashes.append(_t.get("hash"))

        return hashes

    def _cancel_celery_processes(self, torrents: "QuerySet[MovieTorrent]") -> None:
        torrents = [torrent.id for torrent in torrents]
        if not torrents:
            return

        if not is_redis_online():
            return

        processes: List[Any] = []
        try:
            nodes: List[str] = get_celery_nodes()
        except Exception:
            return

        inspect: Inspect = app.control.inspect(nodes)
        [processes.extend(process) for process in inspect.active().values()]
        [processes.extend(process) for process in inspect.reserved().values()]
        [processes.extend(process) for process in inspect.scheduled().values()]

        for process in processes:
            if process.get("id"):
                app.control.revoke(process.get("id"))

            if process.get("request") and process.get("request", {}).get("id"):
                app.control.revoke(process.get("request", {}).get("id"))

    def _get_subtitles(
        self, movie_contents: "QuerySet[MovieContent]"
    ) -> List[MovieSubtitle]:
        subtitles: List[MovieSubtitle] = []
        for content in movie_contents:
            subs: List[MovieSubtitle] = list(content.movie_subtitle.all())
            subtitles.extend(subs)

        return subtitles


class MoviesEndpointHandler:
    def handle(self, movies_data: MoviesEndpointData, user: User) -> str:
        try:
            movie: Movie = Movie.objects.get(id=movies_data.movie_id)
        except Movie.DoesNotExist:
            raise NotFound(f"Movie {movies_data.movie_id} could not be found.")

        existing: QuerySet[MyList] = MyList.objects.filter(
            movie=movies_data.movie_id
        ).filter(user=user)

        if movies_data.command == MoviesEndpointCommands.add_to_my_list.value:
            if existing.exists():
                if len(existing) == 1:
                    return f"{movie.title} is already on your list."
                else:
                    existing.delete()

            MyList.objects.create(movie=movie, user=user)

            return f"{movie.title} has been added to your list."

        elif movies_data.command == MoviesEndpointCommands.remove_from_my_list.value:
            if existing.exists():
                existing.delete()
                return f"{movie.title} has been removed form your list."

            return f"{movie.title} could not be found on your list."
