import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class CoreModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class MovieSubtitle(CoreModel):
    full_path = models.CharField(max_length=255)
    relative_path = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    suffix = models.CharField(max_length=7)
    lang_three = models.CharField(max_length=3, default="eng")
    updated_at = models.DateTimeField(auto_now=True)


class MovieDBCategory(CoreModel):
    moviedb_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class MovieContent(CoreModel):
    torrent_source = models.TextField(null=True, blank=False)
    full_path = models.CharField(max_length=255, null=True, blank=True)
    relative_path = models.CharField(max_length=255, null=True, blank=True)
    main_folder = models.CharField(max_length=255, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_extension = models.CharField(max_length=255, null=True, blank=True)
    source_file_name = models.CharField(max_length=255, null=True, blank=True)
    source_file_extension = models.CharField(max_length=255, null=True, blank=True)
    movie_subtitle = models.ManyToManyField("stream.MovieSubtitle", blank=True)
    resolution_width = models.IntegerField(default=0)
    resolution_height = models.IntegerField(default=0)
    raw_info = models.TextField(blank=True, null=True)
    is_ready = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if not self.movie_set.exists():
            return f"{self.id} ERROR! No Connected movie is found!"

        return f"{self.id}: {self.movie_set.first().title} - {self.resolution_width}/{self.resolution_height}"

    @classmethod
    def create_with_torrent(cls, torrent_source: str) -> "MovieContent":
        return MovieContent.objects.create(torrent_source=torrent_source)


class Movie(CoreModel):
    imdb_id = models.CharField(max_length=10)
    title = models.CharField(max_length=120, null=False, blank=True)
    description = models.TextField(null=True, blank=True)
    movie_content = models.ManyToManyField("stream.MovieContent")
    moviedb_category = models.ManyToManyField("stream.MovieDBCategory", blank=True)
    moviedb_popularity = models.FloatField(null=True, blank=True)
    poster_path_big = models.CharField(max_length=255, null=True, blank=True)
    poster_path_small = models.CharField(max_length=255, null=True, blank=True)
    backdrop_path_big = models.CharField(max_length=255, null=True, blank=True)
    backdrop_path_small = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(default=0)
    media_info_raw = models.JSONField(default=dict, blank=True)
    imdb_score = models.FloatField(default=0.0)
    original_language = models.CharField(max_length=2, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_adult = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.id}: {self.title}"


class MyList(CoreModel):
    movie = models.ForeignKey(
        "stream.Movie", on_delete=models.CASCADE, related_name="my_list"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.id} - {self.user.username} - {self.movie.title}"


class UserMovieHistory(CoreModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        "stream.Movie", on_delete=models.CASCADE, related_name="history"
    )
    current_second = models.IntegerField(default=0)
    remaining_seconds = models.IntegerField(default=0)
    is_watched = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.user.username} - {self.movie.title}"
