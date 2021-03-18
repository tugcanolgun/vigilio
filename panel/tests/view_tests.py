from typing import Dict, List

import pytest
from django.test import Client
from django.urls import reverse
from pytest_mock import MockerFixture

from stream.models import Movie
from stream.tests.factories import MovieFactory


@pytest.fixture
def ignore_setup(mocker: MockerFixture) -> None:
    mocker.patch("panel.decorators.is_panel_ready")


@pytest.fixture
def bad_setup(mocker: MockerFixture) -> None:
    _setup = mocker.patch("panel.decorators.is_panel_ready")
    _setup.return_value = False


@pytest.fixture
def ignore_settings(mocker: MockerFixture) -> None:
    mocker.patch("panel.decorators.are_settings_filled")


@pytest.fixture
def bad_settings(mocker: MockerFixture) -> None:
    _settings = mocker.patch("panel.decorators.are_settings_filled")
    _settings.return_value = False


@pytest.mark.usefixtures("db")
class TestSetupPanel:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:setup_panel"))

        assert response.status_code == 302
        assert response.url == f"{reverse('login')}?next={reverse('panel:setup_panel')}"

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        response = user_client.get("/panel/setup-panel/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:setup_panel')}"
        )

    def test_renders_context_correctly(
        self, user_client: Client, mocker: MockerFixture, ignore_settings, ignore_setup
    ) -> None:
        commands: Dict[str, List[str]] = {"ffmpeg": ["test1"], "ffprobe": ["test2"]}
        status = mocker.patch("panel.views.get_installation_status")
        status.return_value = commands
        response = user_client.get("/panel/setup-panel/", HTTP_REFERER="/categories")

        assert response.status_code == 200

        context: str = response.content.decode("UTF-8")

        for key, value in commands.items():
            assert key in context
            assert value[0] in context


@pytest.mark.usefixtures("db")
class TestIndex:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:index"))

        assert response.status_code == 302
        assert response.url == f"{reverse('login')}?next={reverse('panel:index')}"

    def test_redirects_to_setup(self, user_client: Client, bad_setup) -> None:
        response = user_client.get(reverse("panel:index"))

        assert response.status_code == 302
        assert response.url == "/panel/setup-panel/"

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        response = user_client.get("/panel/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:index')}"
        )

    def test_responds_correctly(
        self, user_client: Client, ignore_settings, ignore_setup
    ) -> None:
        movie: Movie = MovieFactory()
        response = user_client.get("/panel/")

        assert response.status_code == 200
        assert movie.title in response.content.decode("UTF-8")


@pytest.mark.usefixtures("db")
class TestAddMovie:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:add_movie"))

        assert response.status_code == 302
        assert response.url == f"{reverse('login')}?next={reverse('panel:add_movie')}"

    def test_redirects_to_setup(self, user_client: Client, bad_setup) -> None:
        response = user_client.get("/panel/add-movie/")

        assert response.status_code == 302
        assert response.url == "/panel/setup-panel/"

    def test_redirects_when_daemons_are_not_running(
        self, user_client: Client, mocker: MockerFixture, ignore_setup
    ) -> None:
        background = mocker.patch("panel.decorators.is_background_running")
        background.return_value = False
        response = user_client.get("/panel/add-movie/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:background_processes')}?next={reverse('panel:add_movie')}"
        )

    def test_redirects_to_initial_setup(
        self, user_client: Client, mocker: MockerFixture, ignore_setup, bad_settings
    ) -> None:
        mocker.patch("panel.decorators.is_background_running")
        response = user_client.get("/panel/add-movie/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:add_movie')}"
        )

    def test_responds_correctly(
        self, user_client: Client, mocker: MockerFixture, ignore_settings, ignore_setup
    ) -> None:
        mocker.patch("panel.decorators.is_background_running")
        response = user_client.get("/panel/add-movie/")

        assert response.status_code == 200
        assert response.context[-1].template_name == "panel/add_movie.html"


@pytest.mark.usefixtures("db")
class TestBackgroundManagement:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:background_management"))

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('login')}?next={reverse('panel:background_management')}"
        )

    def test_redirects_to_setup(self, user_client: Client, bad_setup) -> None:
        response = user_client.get("/panel/background-management/")

        assert response.status_code == 302
        assert response.url == "/panel/setup-panel/"

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        response = user_client.get("/panel/background-management/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:background_management')}"
        )

    def test_responds_correctly(
        self, user_client: Client, ignore_settings, ignore_setup
    ) -> None:
        response = user_client.get("/panel/background-management/")

        assert response.status_code == 200
        assert response.context[-1].template_name == "panel/background_management.html"


@pytest.mark.usefixtures("db")
class TestBackgroundProcess:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:background_processes"))

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('login')}?next={reverse('panel:background_processes')}"
        )

    def test_redirects_to_setup(self, user_client: Client, bad_setup) -> None:
        response = user_client.get("/panel/background-processes/")

        assert response.status_code == 302
        assert response.url == "/panel/setup-panel/"

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        response = user_client.get("/panel/background-processes/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:background_processes')}"
        )

    def test_responds_correctly(
        self, user_client: Client, mocker: MockerFixture, ignore_settings, ignore_setup
    ) -> None:
        mocker.patch("panel.views.is_redis_online")
        mocker.patch("panel.views.is_celery_running")
        mocker.patch("panel.views.is_qbittorrent_running")
        response = user_client.get("/panel/background-processes/")

        assert response.status_code == 200
        assert response.context[-1].template_name == "panel/background_process.html"


@pytest.mark.usefixtures("db")
class TestMovieDetail:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:movie_detail", kwargs={"movie_id": 1}))

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('login')}?next={reverse('panel:movie_detail', kwargs={'movie_id': 1})}"
        )

    def test_redirects_to_setup(self, user_client: Client, bad_setup) -> None:
        movie: Movie = MovieFactory()
        response = user_client.get(f"/panel/movie-detail/{movie.id}")

        assert response.status_code == 302
        assert response.url == "/panel/setup-panel/"

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        movie: Movie = MovieFactory()
        response = user_client.get(f"/panel/movie-detail/{movie.id}")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:movie_detail', kwargs={'movie_id': 1})}"
        )

    def test_renders_movies(
        self, user_client: Client, ignore_settings, ignore_setup
    ) -> None:
        movie: Movie = MovieFactory()
        response = user_client.get(f"/panel/movie-detail/{movie.id}")

        assert response.status_code == 200
        assert response.context[-1].template_name == "panel/movie_detail.html"
        assert f'mid="{movie.id}"' in response.content.decode("UTF-8")


@pytest.mark.usefixtures("db")
class TestUserHistory:
    def test_blocks_unauthorized(self, client: Client) -> None:
        response = client.get(reverse("panel:user_history"))

        assert response.status_code == 302
        assert (
            response.url == f"{reverse('login')}?next={reverse('panel:user_history')}"
        )

    def test_redirects_to_initial_setup(
        self, user_client: Client, ignore_setup, bad_settings
    ) -> None:
        response = user_client.get("/panel/history/")

        assert response.status_code == 302
        assert (
            response.url
            == f"{reverse('panel:initial_setup')}?next={reverse('panel:user_history')}"
        )

    def test_responds_correctly(self, user_client: Client, ignore_settings) -> None:
        response = user_client.get("/panel/history/")

        assert response.status_code == 200
        assert response.context[-1].template_name == "panel/user_history.html"
