import json
from typing import Union, Dict, Any

import pytest
from _pytest.monkeypatch import MonkeyPatch
from django.conf import settings
from pytest_mock import MockerFixture

import panel
from panel.tasks.moviedb import (
    _get_moviedb_api_key,
    _get_response_from_moviedb_api,
    download_movie_info,
)
from panel.tasks.tests.mocks import MockRequest
from panel.tasks.tests.test_utils import MOVIEDB
from stream.models import Movie
from stream.tests.factories import MovieFactory


class TestGetMovieDBApiKey:
    def test_raises_when_no_setting(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.delattr(settings, "MOVIEDB_API", raising=True)

        with pytest.raises(Exception) as exc:
            _get_moviedb_api_key()

        assert str(exc.value) == "MOVIEDB_API could not be found or empty."

    @pytest.mark.parametrize("moviedb_api", [None, ""])
    def test_raises_when_setting_is_empty(
        self, moviedb_api: Union[str, None], mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "MOVIEDB_API", moviedb_api)

        with pytest.raises(Exception) as exc:
            _get_moviedb_api_key()

        assert str(exc.value) == "MOVIEDB_API could not be found or empty."

    def test_retuns_moviedb_api(self, mocker: MockerFixture) -> None:
        mockerdb_api: str = "abcdef"
        mocker.patch.object(settings, "MOVIEDB_API", mockerdb_api)

        assert _get_moviedb_api_key() == mockerdb_api


class TestGetResponseFromMovieDBApi:
    def test_raises_when_response_not_200(self, mocker: MonkeyPatch) -> None:
        mocker.patch("panel.tasks.moviedb.requests", MockRequest)
        mocker.patch("panel.tasks.tests.mocks.MockRequest.status_code", 404)

        with pytest.raises(Exception) as exc:
            _get_response_from_moviedb_api("http://test")

        assert str(exc.value) == "Moviedb API returned the status code 404"

    def test_raises_when_response_has_only_empty_lists(
        self, mocker: MonkeyPatch
    ) -> None:
        result: Dict[str, Any] = {
            "movie_results": [],
            "person_results": [],
            "tv_results": [],
            "tv_episode_results": [],
            "tv_season_results": [],
        }
        mocker.patch("panel.tasks.moviedb.requests", MockRequest)
        mocker.patch.object(
            panel.tasks.tests.mocks.MockRequest, "json", lambda x: result
        )

        with pytest.raises(Exception) as exc:
            _get_response_from_moviedb_api("http://test")

        assert (
            str(exc.value) == "Moviedb API returned no results. Possible wrong IMDB ID"
        )

    def test_returns_result(self, mocker: MonkeyPatch) -> None:
        mocker.patch("panel.tasks.moviedb.requests", MockRequest)
        mocker.patch(
            "panel.tasks.tests.mocks.MockRequest.text",
            json.dumps(MOVIEDB).encode("UTF-8"),
        )
        mocker.patch.object(
            panel.tasks.tests.mocks.MockRequest, "json", lambda x: {"dummy": "response"}
        )

        assert _get_response_from_moviedb_api("http://test") == MOVIEDB


@pytest.mark.usefixtures("db")
def test_download_movie_info(mocker: MockerFixture) -> None:
    mocker.patch.object(settings, "MOVIEDB_API", "lalala")
    mocker.patch.object(
        panel.tasks.moviedb, "_get_response_from_moviedb_api", lambda x: MOVIEDB
    )
    movie: Movie = MovieFactory()
    expected = MOVIEDB["movie_results"][0]

    assert download_movie_info(movie.id) is None

    movie.refresh_from_db()

    assert movie.title == expected.get("original_title")
    assert movie.description == expected.get("overview")
    assert str(movie.release_date) == expected.get("release_date")
    assert movie.moviedb_category.count() == 1
    assert movie.original_language == expected.get("original_language")
    assert isinstance(movie.moviedb_popularity, float)
    assert movie.media_info_raw == MOVIEDB["movie_results"]
    assert expected.get("poster_path") in movie.poster_path_big
    assert expected.get("poster_path") in movie.poster_path_small
    assert expected.get("backdrop_path") in movie.backdrop_path_big
    assert expected.get("backdrop_path") in movie.backdrop_path_small
    assert movie.imdb_score == expected.get("vote_average")
    assert movie.is_ready is True
