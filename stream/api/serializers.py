from dataclasses import dataclass
from enum import Enum

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
    my_list = MyListSerializer()

    class Meta:
        model = Movie
        exclude = ("media_info_raw",)


class CategoriesWithMoviesSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField(source="get_movies")

    class Meta:
        model = MovieDBCategory
        exclude = ()

    def get_movies(self, obj):
        return MovieSerializer(
            Movie.objects.filter(moviedb_category__moviedb_id=obj.moviedb_id)
            .filter(is_ready=True)
            .filter(movie_content__is_ready=True)
            .distinct(),
            many=True,
        ).data


class UserMovieHistorySerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserMovieHistory
        exclude = ("id",)


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
