import logging
from pathlib import Path
from typing import List, Dict, Optional

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse

from panel.decorators import check_settings, demo_or_login_required
from panel.tasks.tests.iso_639 import iso_639_2_to_1
from stream.handlers import _get_url, _get_quality_string
from stream.models import MovieContent, Movie, UserMovieHistory

logger = logging.getLogger(__name__)


@demo_or_login_required
@check_settings
def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "stream/index.html")


@demo_or_login_required
@check_settings
def categories(request: WSGIRequest) -> HttpResponse:
    return render(request, "stream/categories.html")


@demo_or_login_required
@check_settings
def watch(request: WSGIRequest, movie_id: int) -> HttpResponse:
    movie: Movie = Movie.objects.get(id=movie_id)
    movie_contents: QuerySet[MovieContent] = movie.movie_content.filter(
        is_ready=True
    ).all()
    if not movie_contents:
        return HttpResponseNotFound("Movie could not be found.")

    user_history: Optional[UserMovieHistory] = UserMovieHistory.objects.filter(
        user=request.user, movie=movie
    ).last()

    video_details: List[Dict[str, str]] = [
        {
            "url": _get_url(
                full_path=movie_content.full_path,
                relative_path=movie_content.relative_path,
            ),
            "is_ready": movie_content.is_ready,
            "quality": _get_quality_string(movie_content.resolution_width),
            "suffix": movie_content.file_extension.replace(".", "")
            if movie_content.file_extension is not None
            else "",
        }
        for movie_content in movie_contents
    ]
    subtitles: List[Dict[str, str]] = [
        {
            "url": _get_url(full_path=sub.full_path, relative_path=sub.relative_path),
            "name": Path(sub.file_name).stem,
            "language": iso_639_2_to_1.get(sub.lang_three, "en"),
        }
        for movie_content in movie_contents
        for sub in movie_content.movie_subtitle.all()
    ]
    context = {
        "video_details": video_details,
        "subtitles": subtitles,
        "poster": movie_contents[0].movie_set.first().backdrop_path_big,
        "save_current_second_api_path": reverse("stream:save_current_second"),
        "movie": movie,
        "start_from": 0
        if user_history is None or user_history.is_watched
        else user_history.current_second,
        "HTTP_REFERER": request.META.get("HTTP_REFERER", ""),
    }

    return render(request, "stream/watch.html", context)


@demo_or_login_required
@check_settings
def search(request: WSGIRequest) -> HttpResponse:
    return render(request, "stream/search.html")
