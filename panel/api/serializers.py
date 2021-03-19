from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Set

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from panel.api.utils import DotenvFilter
from panel.models import MudSource
from stream.models import Movie

TORRENT_COMMANDS: List[str] = [
    "pause",
    "force_start",
    "resume",
    "delete",
    "delete_permanent",
]


class MovieCommands(Enum):
    delete_continue = "deleteContinue"
    delete_everything = "deleteEverything"


class FileCommands(Enum):
    delete_files = "deleteFiles"


@dataclass
class FilesData:
    movie_id: int
    command: str
    files: List[Dict[str, Any]]


@dataclass
class TorrentProcess:
    info_hashes: List[str]
    command: str


@dataclass
class CeleryProcess:
    process_id: str


@dataclass
class MovieManagement:
    id: int
    command: str


@dataclass
class MovieAdd:
    imdb_id: str
    source: str


@dataclass
class GlobalSettingsData:
    dotenv: Dict[str, str]


class TorrentSerializer(serializers.Serializer):
    infoHashes = serializers.ListField(
        child=serializers.CharField(max_length=100, required=True)
    )
    command = serializers.ChoiceField(choices=TORRENT_COMMANDS, required=True)

    @property
    def object(self) -> TorrentProcess:
        return TorrentProcess(
            info_hashes=self.validated_data["infoHashes"],
            command=self.validated_data["command"],
        )


class CelerySerializer(serializers.Serializer):
    processId = serializers.CharField(max_length=100, required=True)

    @property
    def object(self) -> CeleryProcess:
        return CeleryProcess(
            process_id=self.validated_data["processId"],
        )


class FilesSerializer(serializers.Serializer):
    movieId = serializers.IntegerField(required=True)
    command = serializers.ChoiceField(
        choices=[en.value for en in FileCommands], required=False
    )
    files = serializers.ListField(
        child=serializers.DictField(required=True), required=False
    )

    @property
    def object(self) -> FilesData:
        return FilesData(
            movie_id=self.validated_data["movieId"],
            command=self.validated_data.get("command"),
            files=self.validated_data.get("files", []),
        )


class MovieManagementSerializer(serializers.Serializer):
    movieId = serializers.IntegerField(required=True)
    command = serializers.ChoiceField(
        choices=[en.value for en in MovieCommands], required=False
    )

    @property
    def object(self) -> MovieManagement:
        return MovieManagement(
            id=self.validated_data["movieId"],
            command=self.validated_data.get("command"),
        )


class MovieAddSerializer(serializers.Serializer):
    imdbId = serializers.CharField(required=True, min_length=9, max_length=255)
    source = serializers.CharField(required=True, allow_blank=False, min_length=10)

    @property
    def object(self) -> MovieAdd:
        return MovieAdd(
            imdb_id=self.validated_data["imdbId"],
            source=self.validated_data.get("source"),
        )


class GlobalSettingsSerializer(serializers.Serializer):
    dotenv = serializers.DictField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    @property
    def object(self) -> GlobalSettingsData:
        return GlobalSettingsData(
            dotenv=self.validated_data["dotenv"],
        )

    def validate_dotenv(self, value) -> Dict[str, str]:
        if not isinstance(value, dict):
            raise serializers.ValidationError("dotenv has to be a dictionary.")

        dotenv_values: Set[str] = DotenvFilter.get_filter(user=self.user)
        for key, val in value.items():
            if key not in dotenv_values:
                raise serializers.ValidationError(f"{key} not in dotenv keys")
            if val == "" or val is None:
                raise serializers.ValidationError(f"{key} is empty.")

        return value


class MudSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MudSource
        exclude = []


class RedownloadSubtitlesSerializer(serializers.Serializer):
    movieIds = serializers.ListField(
        required=True, child=serializers.IntegerField(required=True)
    )

    @property
    def object(self) -> List[str]:
        return self.validated_data["movieIds"]

    def validate_movieIds(self, ids: List[str]) -> List[str]:
        for _id in ids:
            try:
                Movie.objects.get(id=_id)
            except Movie.DoesNotExist:
                raise ValidationError(f"Movie {_id} could not be found.")

        return ids
