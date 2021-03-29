from typing import Any, Dict

import pytest
from django.test import Client
from rest_framework.reverse import reverse

from stream.models import Movie, MovieContent
from stream.tests.factories import MovieFactory, MovieContentFactory


@pytest.mark.usefixtures("db")
class TestMovies:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("stream:movies_api"))

        assert response.status_code == 403
        assert (
            response.content.decode("utf-8")
            == '{"detail":"Authentication credentials were not provided."}'
        )

    def test_returns_all_movies(self, user_client: Client) -> None:
        movie_content: MovieContent = MovieContentFactory.create(
            is_ready=True, full_path="/path"
        )
        movie: Movie = MovieFactory.create(movie_content=[movie_content], is_ready=True)
        response = user_client.get(reverse("stream:movies_api"))

        assert response.status_code == 200

        result: Dict[str, Any] = response.json()

        assert len(result["movies"]) == 1
        assert result["relative_watch_path"] == "/watch/"
        assert result["movies"][0]["title"] == movie.title
        assert result["movies"][0]["description"] == movie.description
        assert len(result["movies"][0]["movie_content"]) == 1
        assert (
            result["movies"][0]["movie_content"][0]["is_ready"]
            is movie_content.is_ready
        )
        assert (
            result["movies"][0]["movie_content"][0]["resolution_height"]
            == movie_content.resolution_height
        )
        assert (
            result["movies"][0]["movie_content"][0]["resolution_width"]
            == movie_content.resolution_width
        )

    def test_returns_empty_when_id_not_found(self, user_client: Client) -> None:
        movie_content: MovieContent = MovieContentFactory.create(
            is_ready=True, full_path="/path"
        )
        MovieFactory.create(movie_content=[movie_content], is_ready=True)
        response = user_client.get(f"{reverse('stream:movies_api')}?id=-1")

        assert response.status_code == 200
        assert response.json() == {"movies": [], "relative_watch_path": "/watch/"}

    def test_returns_movie_with_id(self, user_client: Client) -> None:
        movie_content: MovieContent = MovieContentFactory.create(
            is_ready=True, full_path="/path"
        )
        movie: Movie = MovieFactory.create(movie_content=[movie_content], is_ready=True)
        response = user_client.get(f"{reverse('stream:movies_api')}?id={movie.id}")

        assert response.status_code == 200
        assert len(response.json()["movies"]) == 1
        assert response.json()["movies"][0]["id"] == movie.id

    def test_returns_empty_when_no_query_matches(self, user_client: Client) -> None:
        movie_content: MovieContent = MovieContentFactory.create(
            is_ready=True, full_path="/path"
        )
        MovieFactory.create(movie_content=[movie_content], is_ready=True)
        response = user_client.get(f"{reverse('stream:movies_api')}?query=test")

        assert response.status_code == 200
        assert response.json() == {"movies": [], "relative_watch_path": "/watch/"}

    def test_returns_movie_when_query_matches(self, user_client: Client) -> None:
        movie_content: MovieContent = MovieContentFactory.create(
            is_ready=True, full_path="/path"
        )
        movie: Movie = MovieFactory.create(movie_content=[movie_content], is_ready=True)
        response = user_client.get(f"{reverse('stream:movies_api')}?query=sint")

        assert response.status_code == 200
        assert len(response.json()["movies"]) == 1
        assert response.json()["movies"][0]["id"] == movie.id
