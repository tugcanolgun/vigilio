import logging
from typing import Dict, List

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from panel.api.utils import is_qbittorrent_running, is_redis_online, is_celery_running
from panel.decorators import (
    setup_required,
    check_background,
    check_settings,
    demo_or_login_required,
)
from panel.handlers import get_installation_status
from stream.models import Movie

logger = logging.getLogger(__name__)


@demo_or_login_required
@check_settings
def setup_panel(request: WSGIRequest) -> HttpResponse:
    commands: Dict[str, List[str]] = get_installation_status()

    return render(request, "panel/setup.html", context={"commands": commands})


@demo_or_login_required
@setup_required
@check_settings
def index(request: WSGIRequest) -> HttpResponse:
    movies: QuerySet[Movie] = Movie.objects.order_by("-created_at").all()

    return render(request, "panel/index.html", context={"movies": movies})


@demo_or_login_required
@setup_required
@check_background
@check_settings
def add_movie(request: WSGIRequest) -> HttpResponse:
    return render(request, "panel/add_movie.html")


@demo_or_login_required
@setup_required
@check_settings
def background_management(request: WSGIRequest) -> HttpResponse:
    return render(request, "panel/background_management.html")


@demo_or_login_required
@setup_required
@check_settings
def background_processes(request: WSGIRequest) -> HttpResponse:
    redis_status: bool = is_redis_online()
    celery: bool = False
    if redis_status and is_celery_running():
        celery = True

    qbittorrent: bool = is_qbittorrent_running()

    if redis_status and celery and qbittorrent and request.GET.get("next"):
        return HttpResponseRedirect(request.GET.get("next"))

    return render(
        request,
        "panel/background_process.html",
        context={
            "qbittorrent": qbittorrent,
            "redis": redis_status,
            "celery": celery,
        },
    )


@demo_or_login_required
@setup_required
@check_settings
def movie_detail(request: WSGIRequest, movie_id: int) -> HttpResponse:
    return render(request, "panel/movie_detail.html", context={"movie_id": movie_id})


@demo_or_login_required
@check_settings
def user_history(request: WSGIRequest) -> HttpResponse:
    return render(request, "panel/user_history.html")


@demo_or_login_required
def settings(request: WSGIRequest) -> HttpResponse:
    return render(request, "panel/settings.html")


@demo_or_login_required
def initial_setup(request: WSGIRequest) -> HttpResponse:
    return render(request, "panel/initial_setup.html")
