import factory

from panel import models
from stream.tests.factories import MovieContentFactory


class MovieTorrentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MovieTorrent

    source = MovieContentFactory.torrent_source
    name = "Sintel"
    movie_content = factory.SubFactory(MovieContentFactory)
    is_complete = False
