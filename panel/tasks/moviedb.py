import datetime
import json
import logging
from typing import Dict, Any, Optional

import requests

from panel.tasks.inmemory import get_setting
from stream.models import Movie, MovieDBCategory
from watch.celery import app

logger = logging.getLogger(__name__)


def _get_moviedb_api_key() -> str:
    moviedb: Optional[str] = get_setting("MOVIEDB_API")
    if not moviedb:
        raise Exception("MOVIEDB_API could not be found or empty.")

    return moviedb


def _get_response_from_moviedb_api(url: str) -> Dict[str, Any]:
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Moviedb API returned the status code {response.status_code}")

    if not any([value for value in response.json().values() if value]):
        raise Exception("Moviedb API returned no results. Possible wrong IMDB ID")

    return json.loads(response.text)


@app.task
def download_movie_info(movie_id: int) -> None:
    logger.info(f"Movie info fetching process started for {movie_id}")
    movie: Movie = Movie.objects.get(id=movie_id)
    imdb_id: str = movie.imdb_id
    moviedb_key: str = _get_moviedb_api_key()
    url: str = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={moviedb_key}&language=en-US&external_source=imdb_id"
    response: Dict[str, Any] = _get_response_from_moviedb_api(url)

    raw = response["movie_results"]

    movie.title = raw[0]["original_title"]
    movie.description = raw[0]["overview"]
    movie.release_date = datetime.datetime.strptime(raw[0]["release_date"], "%Y-%m-%d")
    movie.moviedb_category.add(
        *MovieDBCategory.objects.filter(moviedb_id__in=raw[0]["genre_ids"])
    )
    movie.original_language = raw[0]["original_language"]
    movie.moviedb_popularity = float(raw[0]["popularity"])
    movie.poster_path_big = (
        f"https://image.tmdb.org/t/p/original{raw[0]['poster_path']}"
    )
    movie.poster_path_small = f"https://image.tmdb.org/t/p/w500{raw[0]['poster_path']}"
    movie.backdrop_path_big = (
        f"https://image.tmdb.org/t/p/original{raw[0]['backdrop_path']}"
    )
    movie.backdrop_path_small = (
        f"https://image.tmdb.org/t/p/w500{raw[0]['backdrop_path']}"
    )
    movie.imdb_score = raw[0]["vote_average"]
    movie.media_info_raw = raw
    movie.is_ready = True
    movie.save()

    logger.info(f"Movie info fetching process ended for {movie}")
