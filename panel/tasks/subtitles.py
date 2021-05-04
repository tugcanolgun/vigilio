import gzip
import io
import json
import logging
import os
import shutil
import urllib
from dataclasses import dataclass
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


@dataclass
class ApiResponse:
    language: str
    download_link: str
    sub_filename: str
    sub_encoding: str
    sub_hidden_name: str = ""
    full_path: Optional[str] = None


def _get_encoding(encoding: str) -> str:
    if not encoding:
        return "utf-8"

    if encoding.lower().startswith("cp"):
        return encoding[2:]

    return encoding


def extract_subtitle(content: io.BytesIO, encoding: str, file_path: str) -> None:
    with gzip.open(content, mode="rt", encoding=encoding) as f_in:
        with open(file_path, "w") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_and_extract_subtitle(
    url: str, root_path: str, subtitle_name: str, encoding: str = ""
) -> None:
    try:
        response: Response = requests.get(url)
    except requests.exceptions.RequestException:
        return

    if response.status_code != 200:
        logger.error(f"Subtitle could not be downloaded for {url}")
        return

    assert Path(root_path).is_dir() is True, f"{root_path} is not a folder"

    try:
        extract_subtitle(
            content=io.BytesIO(response.content),
            encoding=_get_encoding(encoding),
            file_path=str(Path(root_path) / subtitle_name),
        )
    except LookupError:
        extract_subtitle(
            content=io.BytesIO(response.content),
            encoding="utf-8",
            file_path=str(Path(root_path) / subtitle_name),
        )


def _extract_api_response(response: List[Dict[str, Any]]) -> List[ApiResponse]:
    api_responses: List[ApiResponse] = []
    for res in response:
        if res.get("SubFormat") != "srt" or res.get("SubDownloadLink", "") == "":
            continue

        api_responses.append(
            ApiResponse(
                language=res.get("SubLanguageID", "eng"),
                download_link=res.get("SubDownloadLink"),
                sub_filename=res.get("SubFileName"),
                sub_encoding=res.get("SubEncoding", "utf-8"),
            )
        )

    return api_responses


def _request_from_api(url: str) -> List[ApiResponse]:
    response: Response = requests.get(url, headers={"User-Agent": "TemporaryUserAgent"})

    if response.status_code != 200:
        raise Exception(f"Opensubtitles.org API returned {response.status_code}")

    try:
        return _extract_api_response(json.loads(response.text))
    except json.decoder.JSONDecodeError:
        logger.warning("Opensubtitles.org API response could not be loaded as json")
        return []
    except Exception as exc:
        logger.warning(f"Error occured: {exc}")
        return []


def _get_response_from_api(
    file_hash: str,
    file_byte_size: int,
    imdb_id: str,
    file_name: str,
    limit: int,
    language: str = "eng",
) -> List[ApiResponse]:
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

    api_response: List[ApiResponse] = []
    for _url in request_list:
        response: List[ApiResponse] = _request_from_api(_url)
        api_response.extend(response)

        if len(api_response) >= limit:
            for index, res in enumerate(api_response):
                if index > limit:
                    break

                res.sub_hidden_name = f"{res.language}{index + 1}.srt"

            return api_response[:limit]

    return []


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
    movie_content: MovieContent,
    subtitles_folder: PosixPath,
    file_to_lang: Dict[str, str],
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
            lang_three=file_to_lang.get(vtt_file.name, "eng"),
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
    api_responses: List[List[ApiResponse]],
    subtitles_folder: PosixPath,
) -> None:
    for sub_langs in api_responses:
        for index, sub in enumerate(sub_langs):
            logger.info(
                f"Downloading and extracting subtitle {sub.language} - {index + 1}"
            )
            download_and_extract_subtitle(
                sub.download_link,
                str(subtitles_folder),
                sub.sub_hidden_name,
                sub.sub_encoding,
            )


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


def _get_file_to_lang_map(results: List[List[ApiResponse]]) -> Dict[str, str]:
    _temp: Dict[str, str] = {}
    for sub_langs in results:
        for sub in sub_langs:
            _temp[sub.sub_hidden_name.replace(".srt", ".vtt")] = sub.language
            _temp[sub.sub_filename.replace(".srt", ".vtt")] = sub.language

    return _temp


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
    results: List[List[ApiResponse]] = []
    for language in get_subtitle_language():
        _response: List[ApiResponse] = _get_response_from_api(
            file_hash=file_hash,
            file_byte_size=file_byte_size,
            imdb_id=imdb_id,
            file_name=file_name,
            limit=limit,
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
    )

    _convert_srts_to_vtts_in_folder(subtitles_folder=subtitles_folder)

    if delete_original:
        _delete_original_subtitles(subtitles_folder=subtitles_folder)

    logger.info(f"srts are converted to vtts for {movie_content_id}")

    file_to_lang: Dict[str, str] = _get_file_to_lang_map(results)
    _add_vtt_files_to_movie_content(
        movie_content=movie_content,
        subtitles_folder=subtitles_folder,
        file_to_lang=file_to_lang,
    )
    _change_permissions(subtitles_folder=subtitles_folder)
    logger.info(f"Subtitles are added to movie content {movie_content_id}")
