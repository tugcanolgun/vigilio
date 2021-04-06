from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from django.db.models import QuerySet
from rest_framework import serializers

from stream.models import (
    MovieSubtitle,
    MovieDBCategory,
    MovieContent,
    Movie,
    UserMovieHistory,
    MyList,
)


@dataclass
class SaveCurrentSecond:
    movie_id: int
    current_second: int
    remaining_seconds: int


@dataclass
class MoviesEndpointData:
    movie_id: int
    command: str


class MoviesEndpointCommands(Enum):
    add_to_my_list = "addToMyList"
    remove_from_my_list = "removeFromMyList"


class MovieDBCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieDBCategory
        exclude = ()


class MovieSubtitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSubtitle
        fields = ("full_path", "relative_path")


class MovieContentSerializer(serializers.ModelSerializer):
    # movie_subtitle = MovieSubtitleSerializer(many=True, read_only=True)

    class Meta:
        model = MovieContent
        fields = (
            "resolution_width",
            "resolution_height",
            "is_ready",
            "created_at",
            "movie_subtitle",
        )


class MyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyList
        fields = ("created_at",)


class MovieSerializer(serializers.ModelSerializer):
    movie_content = MovieContentSerializer(many=True, read_only=True)
    my_list = serializers.SerializerMethodField(source="get_my_list")

    def __init__(self, *args, **kwargs):
        if kwargs.get("user"):
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Movie
        exclude = ("media_info_raw",)

    def get_my_list(self, data) -> Dict[str, Any]:
        if hasattr(self, "user"):
            user_list: MyList = MyList.objects.filter(movie=data).filter(user=self.user)
            if not user_list:
                return None

            my_list: MyListSerializer = MyListSerializer(user_list)
        else:
            my_list: MyListSerializer = MyListSerializer(data)

        return my_list.data


class CategoriesWithMoviesSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField(source="get_movies")

    def __init__(self, *args, **kwargs):
        if kwargs.get("user"):
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = MovieDBCategory
        exclude = ()

    def get_movies(self, obj):
        movies: QuerySet[Movie] = (
            Movie.objects.filter(moviedb_category__moviedb_id=obj.moviedb_id)
            .filter(is_ready=True)
            .filter(movie_content__is_ready=True)
            .distinct()
        )
        if hasattr(self, "user"):
            return MovieSerializer(
                movies,
                user=self.user,
                many=True,
            ).data

        return MovieSerializer(
            movies,
            user=self.user,
            many=True,
        ).data


class UserMovieHistorySerializer(serializers.ModelSerializer):
    movie = serializers.SerializerMethodField(source="get_movie")

    def __init__(self, *args, **kwargs):
        if kwargs.get("user"):
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserMovieHistory
        exclude = ("id",)

    def get_movie(self, data) -> Dict[str, Any]:
        if hasattr(self, "user"):
            movie = MovieSerializer(data.movie, user=self.user, read_only=True)
        else:
            movie = MovieSerializer(data.movie, read_only=True)

        return movie.data


class SaveCurrentSecondSerializer(serializers.Serializer):
    movieId = serializers.IntegerField(required=True)
    currentSecond = serializers.FloatField(required=True)
    remainingSeconds = serializers.FloatField(required=True)

    @property
    def object(self) -> SaveCurrentSecond:
        return SaveCurrentSecond(
            movie_id=self.validated_data["movieId"],
            current_second=int(self.validated_data["currentSecond"]),
            remaining_seconds=int(self.validated_data["remainingSeconds"]),
        )


class MoviesEndpointSerializer(serializers.Serializer):
    movieId = serializers.IntegerField(required=True)
    command = serializers.ChoiceField(
        choices=[en.value for en in MoviesEndpointCommands], required=True
    )

    @property
    def object(self) -> MoviesEndpointData:
        return MoviesEndpointData(
            movie_id=self.validated_data["movieId"],
            command=self.validated_data["command"],
        )
