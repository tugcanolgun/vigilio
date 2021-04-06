import logging
import shutil
from pathlib import PosixPath, Path

from panel.tasks import fetch_subtitles
from panel.tasks.torrent import _is_delete_original_files
from stream.models import Movie, MovieContent
from watch.celery import app

logger = logging.getLogger(__name__)


def remove_vtt_subtitles_folder(movie_content: MovieContent) -> None:
    full_path: str = movie_content.full_path
    main: str = movie_content.main_folder
    try:
        folder_path: PosixPath = (
            Path(full_path[: full_path.index(main) + len(main)]) / "vtt_subtitles"
        )
    except TypeError:
        return

    if folder_path.is_dir():
        try:
            shutil.rmtree(str(folder_path))
        except FileNotFoundError:
            logger.error(
                f"vtt_subtitles folder could not be found for movie content {movie_content.id}"
            )
        except NotADirectoryError:
            logger.critical(
                f"vtt_subtitles is not a directory for movie content {movie_content.id}"
            )
            try:
                folder_path.unlink()
            except Exception:
                pass


@app.task
def redownload_subtitles(movie_id: int) -> None:
    try:
        movie: Movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        raise Exception(f"Redownload subtitles. Movie {movie_id} could not be found.")

    for movie_content in movie.movie_content.all():
        remove_vtt_subtitles_folder(movie_content=movie_content)
        movie_content.movie_subtitle.all().delete()
        fetch_subtitles.delay(
            movie_content_id=movie_content.id,
            limit=5,
            delete_original=_is_delete_original_files(),
        )
