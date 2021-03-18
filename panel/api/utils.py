import logging
from typing import List, Any, Dict, Set, Optional

import dotenv
import redis
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import QuerySet
from redis import Redis
from rest_framework.exceptions import APIException

from panel.tasks.torrent import get_qbittorrent_client
from stream.models import Movie, MovieContent
from watch.celery import app
from watch.settings.base import CELERY_BROKER_URL

logger = logging.getLogger(__name__)
CELERY_NODES: List[str] = []


def _get_celery_nodes_from_inspect() -> List[str]:
    # {'worker1@user': [], 'worker2@user': []}
    result: Dict[str, List[Any]] = app.control.inspect().ping()
    if not result:
        raise APIException("Celery is not running.")

    return list(result.keys())


def is_redis_online() -> bool:
    redis_connection: Redis = redis.from_url(CELERY_BROKER_URL)
    try:
        redis_connection.ping()
    except redis.exceptions.ConnectionError:
        return False

    return True


def get_celery_nodes() -> List[str]:
    global CELERY_NODES
    if CELERY_NODES:
        logger.info("Celery nodes have already been cached. Returning cached results.")
        return CELERY_NODES

    _nodes: List[str] = _get_celery_nodes_from_inspect()
    if _nodes:
        CELERY_NODES = _nodes
        return CELERY_NODES

    return []


def is_celery_running() -> bool:
    try:
        _result: Dict[str, List[Any]] = app.control.inspect(get_celery_nodes()).ping()
        if not _result:
            return False
    except APIException:
        return False

    return True


def is_qbittorrent_running() -> bool:
    try:
        get_qbittorrent_client()
    except Exception:
        return False

    return True


class AddMovieHandler:
    def __init__(self, source: str, imdb_id: str) -> None:
        self.source: str = source
        self._imdb: str = imdb_id

    def handle(self) -> str:
        from panel.tasks.torrent import download_torrent

        logger.info(f"Add movie requested for {self.imdb_id}")

        existing_movies: "QuerySet[Movie]" = Movie.objects.filter(
            imdb_id=self.imdb_id
        ).all()

        if existing_movies:
            if len(existing_movies) > 1:
                logger.error(
                    f"There are more than one movie with this imdb id {self.imdb_id}"
                )
                raise APIException(
                    f"There are more than one movie with this imdb id {self.imdb_id}",
                    code=400,
                )

            if MovieContent.objects.filter(torrent_source=self.source).exists():
                raise APIException(
                    "This torrent is already exists in the system. Cannot proceed.",
                    code=400,
                )
            else:
                _movie_content: MovieContent = MovieContent.create_with_torrent(
                    self.source
                )
                existing_movies[0].movie_content.add(_movie_content)
                download_torrent.delay(_movie_content.id)
                return "New content is added to the already existing movie."
        else:
            _movie_content: MovieContent = self._create_new_movie_and_content()
            download_torrent.delay(_movie_content.id)
            return "Process is successfully started."

    def _create_new_movie_and_content(self) -> MovieContent:
        _movie: Movie = Movie.objects.create(imdb_id=self.imdb_id)
        _movie_content: MovieContent = MovieContent.create_with_torrent(self.source)
        _movie.movie_content.add(_movie_content)

        return _movie_content

    @property
    def imdb_id(self) -> str:
        imdb: str = self._imdb
        if len(imdb) > 9 and "title/" in imdb:
            _imdb: str = imdb.split("title/")[1].split("/")[0]
            if 9 <= len(_imdb) <= 13:
                return _imdb

        return imdb


def get_dotenv_location() -> str:
    if not hasattr(settings, "DOTENV"):
        raise Exception("DOTENV is not set in the settings.")

    if settings.MEDIA_FOLDER == "" or settings.MEDIA_FOLDER is None:
        raise Exception("DOTENV is empty.")

    return settings.DOTENV


def get_dotenv_values(filters: Optional[Set[str]] = None) -> Dict[str, str]:
    _values: Dict[str, str] = dotenv.dotenv_values(get_dotenv_location())
    if not filters:
        return _values

    _result: Dict[str, str] = {}
    for val in filters:
        if val in _values:
            _result[val] = _values.pop(val)

    return _result


class DotenvFilter:
    is_superuser: Optional[Set[str]] = get_dotenv_values()
    is_staff: Set[str] = {"MOVIEDB_API", "SUBTITLE_LANGS"}
    user: Set[str] = {"SUBTITLE_LANGS"}

    @classmethod
    def get_filter(cls, user: User) -> Optional[Set[str]]:
        if user.is_superuser:
            return cls.is_superuser
        elif user.is_staff:
            return cls.is_staff
        else:
            return cls.user
