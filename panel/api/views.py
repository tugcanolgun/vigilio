import logging
from dataclasses import asdict
from typing import List, Dict, Any

import dotenv
from celery.app.control import Inspect
from django.conf import settings
from django.contrib.auth.models import User
from qbittorrent import Client
from rest_framework import status, generics
from rest_framework.exceptions import APIException, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from panel.api.handlers import (
    TorrentProcessHandler,
    FilesHandler,
    MovieManagementHandler,
    FilesResult,
)
from panel.api.serializers import (
    TorrentSerializer,
    CelerySerializer,
    FilesSerializer,
    MovieManagementSerializer,
    MovieAddSerializer,
    GlobalSettingsSerializer,
    MudSourceSerializer,
    RedownloadSubtitlesSerializer,
)
from panel.api.utils import (
    get_celery_nodes,
    is_redis_online,
    AddMovieHandler,
    is_qbittorrent_running,
    get_dotenv_location,
    get_dotenv_values,
    DotenvFilter,
)
from panel.api.validators import MovieManagementValidation, FilesValidation
from panel.decorators import check_demo, DemoOrIsAuthenticated
from panel.management.commands import superuser
from panel.models import MudSource
from panel.tasks import redownload_subtitles
from panel.tasks.inmemory import set_redis
from panel.tasks.torrent import get_qbittorrent_client
from watch.celery import app

logger = logging.getLogger(__name__)


class TorrentEndpoint(GenericAPIView):
    serializer_class = TorrentSerializer
    handler_class = TorrentProcessHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        try:
            client: Client = get_qbittorrent_client()
        except Exception:
            raise APIException("Qbittorrent connection failed.")

        return Response(
            {"torrents": client.torrents()},
            status=status.HTTP_200_OK,
        )

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not is_qbittorrent_running():
            raise APIException(
                "Qbittorrent is not running. Cannot process the request."
            )

        handler = self.handler_class().handle(torrent_process=serializer.object)

        return Response(handler)


class CeleryEndpoint(GenericAPIView):
    serializer_class = CelerySerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        if not is_redis_online():
            raise APIException("Redis is offline.")

        nodes: List[str] = get_celery_nodes()
        logger.info(f"Celery nodes: {nodes}")

        inspect: Inspect = app.control.inspect(nodes)

        return Response(
            {
                "active": self._concatenate(inspect.active()),
                "reserved": self._concatenate(inspect.reserved()),
                "scheduled": self._concatenate(inspect.scheduled()),
            },
            status=status.HTTP_200_OK,
        )

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not is_redis_online():
            raise APIException("RabbitMQ is not running. Cannot process the request.")

        app.control.revoke(serializer.object.process_id)

        return Response({"status": "success"})

    @staticmethod
    def _concatenate(
        node_result: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        if not node_result:
            return []

        _result: List[Dict[str, Any]] = []
        for value in node_result.values():
            _result += value

        return _result


class FilesEndpoint(GenericAPIView):
    serializer_class = FilesSerializer
    validator_class = FilesValidation
    handler_class = FilesHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validation = self.validator_class(files_data=serializer.object)
        validation.is_valid()

        result: FilesResult = self.handler_class().handle(files_data=serializer.object)

        return Response(asdict(result))

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validation = self.validator_class(files_data=serializer.object)
        validation.is_valid()

        result = self.handler_class().handle(files_data=serializer.object, is_get=False)

        return Response({"operation": result})


class MovieManagementEndpoint(GenericAPIView):
    serializer_class = MovieManagementSerializer
    validator_class = MovieManagementValidation
    handler_class = MovieManagementHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validation = self.validator_class(
            management=serializer.object, user=request.user
        )
        validation.is_valid()

        result = self.handler_class().handle(
            management=serializer.object, user=request.user
        )

        return Response({"operation": result})


class MovieAddEndpoint(GenericAPIView):
    serializer_class = MovieAddSerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result: str = AddMovieHandler(
            source=serializer.object.source, imdb_id=serializer.object.imdb_id
        ).handle()

        return Response({"operation": result})


class GlobalSettingsEndpoint(GenericAPIView):
    serializer_class = GlobalSettingsSerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        result: Dict[str, Any] = {}
        _dotenv: Dict[str, str] = get_dotenv_values(
            filters=DotenvFilter.get_filter(user=request.user)
        )
        result["dotenv"] = _dotenv
        result["forcePasswordChange"] = False
        admin: User = User.objects.first()

        if admin.check_password(superuser.PASSWORD):
            result["forcePasswordChange"] = True

        return Response(result)

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)

        for key, value in serializer.object.dotenv.items():
            dotenv.set_key(get_dotenv_location(), key, value)
            set_redis(key, str(value))

        dotenv.load_dotenv(settings.DOTENV)

        return Response({"dotenv": "success"})


class MudSourcesList(generics.ListCreateAPIView):
    queryset = MudSource.objects.all()
    serializer_class = MudSourceSerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def perform_create(self, serializer: MudSourceSerializer) -> None:
        serializer.save()


class MudSourceEndpoint(APIView):
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def delete(self, request: Request, mud_id: int) -> Response:
        try:
            mud_source: MudSource = MudSource.objects.get(pk=mud_id)
        except MudSource.DoesNotExist:
            raise NotFound(f"Mud Source ID: {mud_id} not found.")
        else:
            mud_source.delete()

        return Response(None, status=HTTP_204_NO_CONTENT)


class RedownloadSubtitlesEndpoint(GenericAPIView):
    serializer_class = RedownloadSubtitlesSerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for _id in serializer.object:
            redownload_subtitles.delay(movie_id=_id)

        return Response({"operation": "started"})
