import logging
from pathlib import Path, PosixPath
from typing import List, Any, Dict

from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError

from panel.api.serializers import (
    MovieManagement,
    MovieCommands,
    FilesData,
    FileCommands,
)
from panel.tasks.torrent import _get_media_folder
from stream.models import Movie, UserMovieHistory

logger = logging.getLogger(__name__)


class MovieManagementValidation:
    def __init__(self, management: MovieManagement, user: User) -> None:
        self.management: MovieManagement = management
        self.user: User = user

    def is_valid(self) -> None:
        _raise_movie_not_found(movie_id=self.management.id)
        self._check_commands()

    def _check_commands(self) -> None:
        command: str = self.management.command
        if command == MovieCommands.delete_continue.value:
            self._check_delete_continue()

    def _check_delete_continue(self) -> None:
        if not UserMovieHistory.objects.filter(
            user=self.user, movie__pk=self.management.id
        ).exists():
            raise NotFound("User has no history record for this movie.")


class FilesValidation:
    def __init__(self, files_data: FilesData) -> None:
        self.files_data: FilesData = files_data

    def is_valid(self) -> None:
        _raise_movie_not_found(movie_id=self.files_data.movie_id)
        self._check_commands()

    def _check_commands(self) -> None:
        command: str = self.files_data.command
        if command == FileCommands.delete_files.value:
            self._check_delete_files()

    def _check_delete_files(self) -> None:
        files: List[Dict[str, Any]] = self.files_data.files
        if not files:
            raise ValidationError(
                "A file list is necessary if the operation is deleting files"
            )
        media_folder: str = _get_media_folder()
        media_folder_posix: PosixPath = Path(media_folder)
        for _file in files:
            if _file.get("full_path") == media_folder:
                raise ValidationError("Deleting the MEDIA folder is not allowed.")
            full_path: PosixPath = Path(_file.get("full_path"))

            if not full_path.exists():
                raise NotFound(f"{full_path} could not be found.")

            if full_path in media_folder_posix.parents:
                raise ValidationError(
                    "Delete operation above MEDIA folder is not allowed"
                )


def _raise_movie_not_found(movie_id: int) -> None:
    try:
        Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        raise NotFound(f"Movie ID: {movie_id} does not exist.")
    except Movie.MultipleObjectsReturned:
        raise NotFound(
            f"Movie ID: {movie_id} returned multiple movies! Possible DB problem."
        )
