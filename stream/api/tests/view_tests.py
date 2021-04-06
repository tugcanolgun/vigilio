from typing import Any, Dict

import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework.response import Response
from rest_framework.reverse import reverse

from stream.models import Movie, MovieContent, UserMovieHistory
from stream.tests.factories import (
    MovieFactory,
    MovieContentFactory,
    UserFactory,
    UserMovieHistoryFactory,
)


@pytest.fixture
def movie_content() -> MovieContent:
    return MovieContentFactory.create(is_ready=True, full_path="/path")


@pytest.fixture
def movie(movie_content: MovieContent) -> Movie:
    return MovieFactory.create(movie_content=[movie_content], is_ready=True)


@pytest.fixture
def user_history(movie: Movie, user: User) -> UserMovieHistory:
    return UserMovieHistoryFactory(user=user, movie=movie, is_watched=False)


@pytest.mark.usefixtures("db")
class TestMovies:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response: Response = client.get(reverse("stream:movies_api"))

        assert response.status_code == 403
        assert (
            response.content.decode("utf-8")
            == '{"detail":"Authentication credentials were not provided."}'
        )

    def test_returns_all_movies(
        self, movie: Movie, movie_content: MovieContent, user_client: Client
    ) -> None:
        response: Response = user_client.get(reverse("stream:movies_api"))

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

    def test_returns_empty_when_id_not_found(
        self, movie: Movie, user_client: Client
    ) -> None:
        response: Response = user_client.get(f"{reverse('stream:movies_api')}?id=-1")

        assert response.status_code == 200
        assert response.json() == {"movies": [], "relative_watch_path": "/watch/"}

    def test_returns_movie_with_id(self, movie: Movie, user_client: Client) -> None:
        response: Response = user_client.get(
            f"{reverse('stream:movies_api')}?id={movie.id}"
        )

        assert response.status_code == 200
        assert len(response.json()["movies"]) == 1
        assert response.json()["movies"][0]["id"] == movie.id

    def test_returns_empty_when_no_query_matches(
        self, movie: Movie, user_client: Client
    ) -> None:
        response: Response = user_client.get(
            f"{reverse('stream:movies_api')}?query=test"
        )

        assert response.status_code == 200
        assert response.json() == {"movies": [], "relative_watch_path": "/watch/"}

    def test_returns_movie_when_query_matches(
        self, movie: Movie, user_client: Client
    ) -> None:
        response: Response = user_client.get(
            f"{reverse('stream:movies_api')}?query=sint"
        )

        assert response.status_code == 200
        assert len(response.json()["movies"]) == 1
        assert response.json()["movies"][0]["id"] == movie.id


@pytest.mark.usefixtures("db")
class TestContinueMovies:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response: Response = client.get(reverse("stream:continue_movie_list"))

        assert response.status_code == 403
        assert (
            response.content.decode("utf-8")
            == '{"detail":"Authentication credentials were not provided."}'
        )

    def test_returns_no_movies_when_user_has_no_history(
        self, movie: Movie, user_client: Client
    ) -> None:
        another_user: User = UserFactory(
            username="another_user", password="someotherp@assw0rd"
        )
        UserMovieHistoryFactory(user=another_user, movie=movie, is_watched=False)

        response: Response = user_client.get(reverse("stream:continue_movie_list"))

        assert response.status_code == 200
        assert response.json() == {"continue": [], "relative_watch_path": "/watch/"}

    def test_returns_movies_user_watching(
        self, user_history: UserMovieHistory, user_client: Client
    ) -> None:
        response: Response = user_client.get(reverse("stream:continue_movie_list"))

        assert response.status_code == 200
        assert len(response.json()["continue"]) == 1
        assert response.json()["continue"][0]["movie"]["id"] == user_history.movie.id

    def test_returns_movie_with_id(
        self, user_history: UserMovieHistory, user_client: Client
    ) -> None:
        response: Response = user_client.get(
            f'{reverse("stream:continue_movie_list")}?id={user_history.movie.id}'
        )

        assert response.status_code == 200
        assert len(response.json()["continue"]) == 1
        assert response.json()["continue"][0]["movie"]["id"] == user_history.movie.id

    def test_returns_no_movie_when_id_is_wrong(
        self, user_history: UserMovieHistory, user_client: Client
    ) -> None:
        response: Response = user_client.get(
            f'{reverse("stream:continue_movie_list")}?id=-1'
        )

        assert response.status_code == 200
        assert len(response.json()["continue"]) == 0
