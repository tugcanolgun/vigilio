import gzip
import io
import json
import logging
import os
import shutil
import urllib
from pathlib import Path, PosixPath
from typing import Dict, Any, Optional, List, Set

import requests
from requests import Response

from panel.tasks.inmemory import get_setting
from panel.tasks.opensubtitles_hasher import get_hash
from stream.models import MovieContent, Movie, MovieSubtitle
from watch.celery import app
from watch.settings.base import BASE_DIR

logger = logging.getLogger(__name__)

OS_URL: str = "https://rest.opensubtitles.org/search"


def download_and_extract_subtitle(url: str, root_path: str, subtitle_name: str) -> None:
    response: Response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Subtitle could not be downloaded for {url}")

    assert Path(root_path).is_dir() is True, f"{root_path} is not a folder"

    with gzip.open(io.BytesIO(response.content), "rb") as f_in:
        with open(str(Path(root_path) / subtitle_name), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def _request_from_api(url: str) -> Optional[List[Dict[str, Any]]]:
    response: Response = requests.get(url, headers={"User-Agent": "TemporaryUserAgent"})

    if response.status_code != 200:
        raise Exception(f"Opensubtitles.org API returned {response.status_code}")

    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        logger.warning("Opensubtitles.org API response could not be loaded as json")
        return None
    except Exception as exc:
        logger.warning(f"Error occured: {exc}")
        return None


def _get_response_from_api(
    file_hash: str,
    file_byte_size: int,
    imdb_id: str,
    file_name: str,
    language: str = "eng",
) -> Optional[List[Dict[str, Any]]]:
    _movie_byte_size: str = f"/moviebytesize-{file_byte_size}"
    _movie_hash: str = f"/moviehash-{file_hash}"
    _imdb = f"/imdbid-{imdb_id[2:]}"
    _encoded_file_name: str = urllib.parse.quote(file_name)
    _file_name = f"/query-{_encoded_file_name}"
    _language = f"/sublanguageid-{language}"

    request_list: List[str] = [
        OS_URL + _movie_byte_size + _movie_hash + _imdb + _language,
        OS_URL + _file_name + _imdb + _language,
        OS_URL + _imdb + _language,
    ]

    for _url in request_list:
        response: Optional[List[Dict[str, Any]]] = _request_from_api(_url)
        if response:
            return response


def _convert_srt_to_vtt(srt_file: str) -> None:
    _input: PosixPath = Path(srt_file)
    output_file: str = f"{_input.parent / _input.stem}.vtt"
    os.system(f"{BASE_DIR}/panel/tasks/srt2vtt.sh {srt_file} > {output_file}")


def _convert_srts_to_vtts_in_folder(subtitles_folder: PosixPath) -> None:
    for item in subtitles_folder.iterdir():
        if item.is_file() and item.suffix.lower() == ".srt":
            _convert_srt_to_vtt(str(item))


def _get_vtt_files_in_folder(folder: PosixPath) -> List[PosixPath]:
    vtt_files: List[PosixPath] = []
    for _file in folder.iterdir():
        if _file.is_file() and _file.suffix.lower() == ".vtt":
            vtt_files.append(_file)

    vtt_files.sort()

    return vtt_files


def _add_vtt_files_to_movie_content(
    movie_content: MovieContent, subtitles_folder: PosixPath
) -> None:
    vtt_files: List[PosixPath] = _get_vtt_files_in_folder(subtitles_folder)
    existing: Set[str] = {sub.full_path for sub in movie_content.movie_subtitle.all()}

    for vtt_file in vtt_files:
        if str(vtt_file) in existing:
            continue

        movie_subtitle = MovieSubtitle.objects.create(
            full_path=str(vtt_file),
            relative_path=str(vtt_file.relative_to(vtt_file.parent.parent.parent)),
            file_name=str(vtt_file.name),
            suffix=str(vtt_file.suffix.lower()),
        )
        movie_content.movie_subtitle.add(movie_subtitle)


def _change_permissions(subtitles_folder: PosixPath) -> None:
    def _iterate_folder(folder: PosixPath) -> None:
        for _item in folder.iterdir():
            if _item.is_dir():
                os.chmod(str(_item), 0o745)
                _iterate_folder(_item)

            if _item.is_file():
                os.chmod(str(_item), 0o644)

    os.chmod(str(subtitles_folder), 0o745)
    _iterate_folder(subtitles_folder)


def get_subtitle_language() -> List[str]:
    result: Optional[List[str]] = get_setting("SUBTITLE_LANGS", suppress_errors=True)
    if result and "-" not in result:
        return result.split(",")

    return []


def _process_api_response_and_download_subtitles(
    api_responses: List[List[Dict[str, Any]]],
    subtitles_folder: PosixPath,
    limit: int,
) -> None:
    for response in api_responses:
        count: int = 1
        for _obj in response:
            if count >= limit + 1:
                break
            if _obj.get("SubFormat") != "srt" or _obj.get("SubDownloadLink", "") == "":
                continue

            logger.info(f"Downloading and extracting subtitle number {count + 1}")
            download_and_extract_subtitle(
                _obj.get("SubDownloadLink"),
                str(subtitles_folder),
                f"{_obj.get('SubLanguageID', 'unk')}{count}.srt",
            )
            count += 1


def _get_subtitles_from_path(
    root: PosixPath, subtitles_folder: Optional[PosixPath] = None
) -> Set[PosixPath]:
    suffixes: Set[str] = {".srt"}
    subtitles: Set[PosixPath] = set()

    def _check_folder(path: PosixPath) -> None:
        for _content in path.iterdir():
            if _content.is_dir() and _content != subtitles_folder:
                _check_folder(_content)

            if _content.is_file() and _content.suffix.lower() in suffixes:
                subtitles.add(_content)

    _check_folder(root)

    return subtitles


def _search_existing_subtitles_and_move(
    main_folder: PosixPath, subtitles_folder: PosixPath, limit: int = 5
) -> None:
    subtitles: Set[PosixPath] = _get_subtitles_from_path(
        root=main_folder, subtitles_folder=subtitles_folder
    )
    for index, subtitle in enumerate(subtitles):
        if index >= limit:
            break

        shutil.copy2(
            str(subtitle), str(subtitles_folder / f"org{index + 1}{subtitle.suffix}")
        )


def _create_and_write_to_meta_file(file_path: PosixPath) -> None:
    meta = file_path.parent / "meta.txt"
    meta.touch()
    with open(str(meta), "a") as f:
        f.write(file_path.name)
        f.write("\n")


def _delete_original_subtitles(subtitles_folder: PosixPath) -> None:
    for item in subtitles_folder.iterdir():
        if item.is_file() and item.suffix.lower() == ".srt":
            _create_and_write_to_meta_file(file_path=item)
            os.remove(str(item))


@app.task
def fetch_subtitles(
    movie_content_id: int, limit: int = 5, delete_original: bool = False
) -> None:
    try:
        movie_content: MovieContent = MovieContent.objects.get(id=movie_content_id)
    except MovieContent.DoesNotExist:
        logger.critical(f"MovieContent with {movie_content_id} id does not exist.")
        raise

    if not movie_content.full_path or not Path(movie_content.full_path).exists():
        raise FileNotFoundError(
            f"{movie_content.full_path} does not exist for MovieContent {movie_content_id}"
        )

    movie: Movie = movie_content.movie_set.first()
    file_hash: str = get_hash(movie_content.full_path)
    file_byte_size: int = os.path.getsize(movie_content.full_path)
    imdb_id: str = movie.imdb_id
    file_name: str = movie.title

    logger.info(f"Requesting subtitles from opensubtitles for {movie_content_id}")
    results: List[List[Dict[str, Any]]] = []
    for language in get_subtitle_language():
        _response: Optional[List[Dict[str, Any]]] = _get_response_from_api(
            file_hash=file_hash,
            file_byte_size=file_byte_size,
            imdb_id=imdb_id,
            file_name=file_name,
            language=language,
        )
        if _response:
            results.append(_response)

        logger.info(
            "subtitle request returned %s results",
            "None" if not _response else str(len(_response)),
        )

    full_path: PosixPath = Path(movie_content.full_path)
    if full_path.is_file():
        full_path = full_path.parent

    subtitles_folder: PosixPath = full_path / "vtt_subtitles"
    subtitles_folder.mkdir(exist_ok=True)

    _search_existing_subtitles_and_move(
        main_folder=full_path, subtitles_folder=subtitles_folder
    )

    _process_api_response_and_download_subtitles(
        api_responses=results,
        subtitles_folder=subtitles_folder,
        limit=limit,
    )

    _convert_srts_to_vtts_in_folder(subtitles_folder=subtitles_folder)

    if delete_original:
        _delete_original_subtitles(subtitles_folder=subtitles_folder)

    logger.info(f"srts are converted to vtts for {movie_content_id}")
    _add_vtt_files_to_movie_content(
        movie_content=movie_content, subtitles_folder=subtitles_folder
    )
    _change_permissions(subtitles_folder=subtitles_folder)
    logger.info(f"Subtitles are added to movie content {movie_content_id}")
