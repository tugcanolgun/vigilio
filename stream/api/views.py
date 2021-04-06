import logging
from typing import Dict

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from panel.api.handlers import MoviesEndpointHandler
from panel.decorators import DemoOrIsAuthenticated
from stream.api.handlers import (
    SaveCurrentSecondHandler,
    UserMovieHistoryHandler,
    MoviesHandler,
)
from stream.api.serializers import (
    MovieSerializer,
    SaveCurrentSecondSerializer,
    UserMovieHistorySerializer,
    CategoriesWithMoviesSerializer,
    MoviesEndpointSerializer,
)
from stream.api.utils import _get_relative_path_to_watch
from stream.api.validators import SaveCurrentSecondValidator
from stream.models import Movie, UserMovieHistory, MovieDBCategory

logger = logging.getLogger(__name__)


class ContinueMoviesEndpoint(GenericAPIView):
    serializer_class = UserMovieHistorySerializer
    handler_class = UserMovieHistoryHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        user_history: QuerySet[UserMovieHistory] = self.handler_class().handle(
            history_id=request.query_params.get("id", None), user=request.user
        )

        serialized_locations = self.get_serializer(
            user_history, user=request.user, many=True
        )

        return Response(
            {
                "continue": serialized_locations.data,
                "relative_watch_path": _get_relative_path_to_watch(),
            },
            status=status.HTTP_200_OK,
        )


class MoviesEndpoint(GenericAPIView):
    serializer_class = MoviesEndpointSerializer
    handler_class = MoviesHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        movies: QuerySet[Movie] = self.handler_class().handle(
            movie_id=request.query_params.get("id", None),
            query=request.query_params.get("query", None),
        )

        serialized_movies = MovieSerializer(movies, user=request.user, many=True)

        return Response(
            {
                "movies": serialized_movies.data,
                "relative_watch_path": _get_relative_path_to_watch(),
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result: str = MoviesEndpointHandler().handle(
            movies_data=serializer.object, user=request.user
        )

        return Response(
            {"status": result},
            status=status.HTTP_200_OK,
        )


class SaveCurrentSecondEndpoint(GenericAPIView):
    serializer_class = SaveCurrentSecondSerializer
    validator_class = SaveCurrentSecondValidator
    handler_class = SaveCurrentSecondHandler
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validator = self.validator_class()
        validator.validate(serializer.object)

        handler = self.handler_class()
        response: Dict[str, bool] = handler.handle(
            save_current_second=serializer.object, user=request.user
        )

        return Response(
            response,
            status=status.HTTP_200_OK,
        )


class CategoriesEndpoint(GenericAPIView):
    serializer_class = CategoriesWithMoviesSerializer
    permission_classes = [DemoOrIsAuthenticated]
    verbose_request_logging = True

    def get(self, request: Request) -> Response:
        if request.query_params.get("id", None) is None:
            categories: QuerySet[MovieDBCategory] = MovieDBCategory.objects.all()
        else:
            categories: QuerySet[MovieDBCategory] = MovieDBCategory.objects.filter(
                moviedb_id=request.query_params.get("id")
            ).all()

        serialized_locations = self.get_serializer(
            categories, user=request.user, many=True
        )

        return Response(
            {
                "categories": serialized_locations.data,
                "relative_watch_path": _get_relative_path_to_watch(),
            },
            status=status.HTTP_200_OK,
        )
