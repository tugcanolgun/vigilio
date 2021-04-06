import factory
from django.contrib.auth.models import User

from stream import models
from stream.models import UserMovieHistory


class MovieSubtitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MovieSubtitle


class MovieContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MovieContent

    torrent_source = "magnet:?xt=urn:btih:f3b003ca7e41e1b78e488a1448926a1f90adc4fc&dn=Sintel-ThirdOpenMovieByBlender"

    @factory.post_generation
    def movie_subtitle(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.movie_subtitle.set(extracted)


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Movie

    title = "Sintel"
    description = "The film follows a girl named Sintel who is searching for a baby dragon she calls Scales."
    imdb_id = "tt1727587"

    @factory.post_generation
    def movie_content(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of movie_contents were passed in, use them
            self.movie_content.set(extracted)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "test_user"
    password = "5q4rq4%WByk"


class UserMovieHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserMovieHistory
