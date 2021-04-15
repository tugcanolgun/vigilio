import urllib
from pathlib import PosixPath, Path
from typing import Set, List, Dict

import pytest
from _pytest.monkeypatch import MonkeyPatch
from django.conf import settings
from pytest_mock import MockerFixture

import panel
from panel.tasks.subtitles import (
    download_and_extract_subtitle,
    _request_from_api,
    _get_response_from_api,
    OS_URL,
    _get_vtt_files_in_folder,
    _add_vtt_files_to_movie_content,
    _change_permissions,
    get_subtitle_language,
    fetch_subtitles,
    _get_subtitles_from_path,
    _search_existing_subtitles_and_move,
    ApiResponse,
    _get_encoding,
)
from panel.tasks.tests.mocks import MockRequest
from panel.tasks.tests.torrent_tests import CreateFileTree
from stream.models import MovieContent, MovieSubtitle
from stream.tests.factories import (
    MovieContentFactory,
    MovieFactory,
    MovieSubtitleFactory,
)


class TestDownloadAndExtractSubtitle:
    def test_does_not_raise_when_api_returns_error(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        url: str = "tor://test"

        try:
            download_and_extract_subtitle(
                url=url, root_path=str(tmp_path), subtitle_name="subtitle.srt"
            )
        except Exception:
            pytest.fail("API errors should not raise errors.")

    def test_raises_if_root_folder_is_not_folder(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        root_path: str = "/some/folder/location"

        with pytest.raises(Exception) as exc:
            download_and_extract_subtitle(
                url="http://test", root_path=root_path, subtitle_name="subtitle.srt"
            )

        assert str(exc.value) == f"{root_path} is not a folder"

    def test_writes_contents_to_new_file(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        new_file: PosixPath = tmp_path / "subtitle.vtt"

        download_and_extract_subtitle(
            url="http://test", root_path=str(tmp_path), subtitle_name=new_file.name
        )

        assert new_file.is_file()
        with open(str(new_file), "rb") as f:
            assert f.read() == MockRequest._content


class TestRequestFromApi:
    def test_raises_when_api_returns_error(self, mocker: MockRequest) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)

        with pytest.raises(Exception) as exc:
            _request_from_api(url="throw_error://something")

        assert "Opensubtitles.org API returned" in str(exc.value)

    def test_returns_empty_list_when_text_not_loads_as_json(
        self, mocker: MockRequest
    ) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        mocker.patch("panel.tasks.tests.mocks.MockRequest.text", "lalala")

        assert _request_from_api(url="https://something") == []


class TestGetResponseFromApi:
    def test_calls_functions_correctly(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        mocker.patch("panel.tasks.tests.mocks.MockRequest.text", "lalala")
        request_from_api = mocker.spy(panel.tasks.subtitles, "_request_from_api")
        _file_hash: str = "abc"
        _file_byte_size: int = 1000
        _imdb_id: str = "tt01010101"
        _file_name: str = "video.mp4"
        _language: str = "eng"
        file_byte_size: str = f"/moviebytesize-{_file_byte_size}"
        file_hash: str = f"/moviehash-{_file_hash}"
        imdb_id = f"/imdbid-{_imdb_id[2:]}"
        _encoded_file_name: str = urllib.parse.quote(_file_name)
        file_name = f"/query-{_encoded_file_name}"
        language = f"/sublanguageid-{_language}"

        result = _get_response_from_api(
            file_hash=_file_hash,
            file_byte_size=_file_byte_size,
            imdb_id=_imdb_id,
            file_name=_file_name,
            limit=5,
            language=_language,
        )

        request_from_api.assert_any_call(OS_URL + imdb_id + language)
        request_from_api.assert_any_call(OS_URL + file_name + imdb_id + language)
        request_from_api.assert_any_call(
            OS_URL + file_byte_size + file_hash + imdb_id + language
        )
        assert result == []

    def test_returns_response_correctly(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)

        result = _get_response_from_api(
            file_hash="abcdef",
            file_byte_size=1,
            imdb_id="tt010101010",
            limit=5,
            file_name="video.mp4",
        )

        assert isinstance(result, list)
        assert result == []


def test_get_vtt_files_in_folder(tmp_path: PosixPath) -> None:
    videos: Set[str] = {"subtitle.str", "subtitle.vtt", "eng.srt", "eng.vtt"}
    for video in videos:
        (tmp_path / video).touch()

    result = _get_vtt_files_in_folder(tmp_path)

    assert isinstance(result, list)
    assert set(result) == {
        tmp_path / "subtitle.vtt",
        tmp_path / "eng.vtt",
    }


@pytest.mark.usefixtures("db")
def test_add_vtt_files_to_movie_content(tmp_path: PosixPath) -> None:
    videos: List[str] = ["ger.vtt", "subtitle.vtt"]
    file_to_lang: Dict[str, str] = {file_name: "ger" for file_name in videos}
    for video in videos:
        (tmp_path / video).touch()
    movie_content: MovieContent = MovieContentFactory()

    assert not MovieSubtitle.objects.exists()

    _add_vtt_files_to_movie_content(
        movie_content=movie_content,
        subtitles_folder=tmp_path,
        file_to_lang=file_to_lang,
    )
    movie_content.refresh_from_db()

    assert MovieSubtitle.objects.count() == 2
    assert movie_content.movie_subtitle.count() == 2

    movie_subtitles = movie_content.movie_subtitle.all()

    for index, movie_subtitle in enumerate(movie_subtitles):
        assert movie_subtitle.full_path == str(tmp_path / videos[index])
        assert movie_subtitle.relative_path == str(
            Path(tmp_path.parent.name) / tmp_path.name / videos[index]
        )
        assert movie_subtitle.file_name == videos[index]
        assert movie_subtitle.lang_three == "ger"
        assert movie_subtitle.suffix == ".vtt"


@pytest.mark.usefixtures("db")
def test_add_vtt_files_to_movie_content_skips_existing(tmp_path: PosixPath) -> None:
    videos: List[str] = ["eng.vtt", "subtitle.vtt"]
    file_to_lang: Dict[str, str] = {file_name: "ger" for file_name in videos}
    existing: PosixPath = tmp_path / videos[0]
    for video in videos:
        (tmp_path / video).touch()
    movie_subtitle: MovieSubtitle = MovieSubtitleFactory(
        full_path=str(existing),
        relative_path=existing.relative_to(existing.parent.parent.parent),
        file_name=existing.name,
        suffix=existing.suffix,
    )
    movie_content: MovieContent = MovieContentFactory.create(
        movie_subtitle=[movie_subtitle]
    )

    assert MovieSubtitle.objects.count() == 1
    assert movie_content.movie_subtitle.count() == 1

    _add_vtt_files_to_movie_content(
        movie_content=movie_content,
        subtitles_folder=tmp_path,
        file_to_lang=file_to_lang,
    )
    movie_content.refresh_from_db()

    assert MovieSubtitle.objects.count() == 2
    assert movie_content.movie_subtitle.count() == 2

    movie_subtitles = movie_content.movie_subtitle.all()

    for index, movie_subtitle in enumerate(movie_subtitles):
        assert movie_subtitle.full_path == str(tmp_path / videos[index])
        assert movie_subtitle.relative_path == str(
            Path(tmp_path.parent.name) / tmp_path.name / videos[index]
        )
        assert movie_subtitle.file_name == videos[index]
        assert movie_subtitle.suffix == ".vtt"


def test_change_permissions(tmp_path: PosixPath, mocker: MockerFixture) -> None:
    videos: List[str] = ["eng.vtt", "subtitle.vtt"]
    chmod = mocker.spy(panel.tasks.subtitles.os, "chmod")
    new_folder: PosixPath = tmp_path / "new_folder"
    new_folder.mkdir(exist_ok=True)
    for video in videos:
        (tmp_path / video).touch()
        (new_folder / video).touch()

    _change_permissions(tmp_path)

    chmod.assert_any_call(str(tmp_path / videos[0]), 0o644)
    chmod.assert_any_call(str(tmp_path / videos[1]), 0o644)
    chmod.assert_any_call(str(new_folder / videos[0]), 0o644)
    chmod.assert_any_call(str(new_folder / videos[1]), 0o644)
    chmod.assert_any_call(str(new_folder), 0o745)
    chmod.assert_any_call(str(tmp_path), 0o745)


class TestGetSubtitleLanguage:
    def test_when_no_settings(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.delattr(settings, "SUBTITLE_LANGS", raising=True)

        assert get_subtitle_language() == []

    def test_when_setting_is_empty(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SUBTITLE_LANGS", "")

        assert get_subtitle_language() == []

    def test_returns_setting(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SUBTITLE_LANGS", "eng,ger")

        assert get_subtitle_language() == ["eng", "ger"]


def _mock_get_response_from_api(
    file_hash, file_byte_size, imdb_id, file_name, limit, language
) -> List[ApiResponse]:
    return [
        ApiResponse(
            download_link="http://test",
            language=language,
            sub_filename="best_movie.srt",
            sub_hidden_name=f"{language}1.srt",
            sub_encoding="CP1252",
        ),
        ApiResponse(
            download_link="http://test2",
            language=language,
            sub_filename="lala.srt",
            sub_hidden_name=f"{language}2.srt",
            sub_encoding="CP1252",
        ),
    ]


@pytest.mark.usefixtures("db")
class TestFetchSubtitles:
    def test_raises_when_no_movie_content(self):
        with pytest.raises(MovieContent.DoesNotExist) as exc:
            fetch_subtitles(-999)

        assert str(exc.value) == "MovieContent matching query does not exist."

    def test_raises_when_movie_content_full_path_not_exists(self) -> None:
        movie_content: MovieContent = MovieContentFactory()
        with pytest.raises(FileNotFoundError) as exc:
            fetch_subtitles(movie_content.id)

        assert (
            str(exc.value)
            == f"{movie_content.full_path} does not exist for MovieContent {movie_content.id}"
        )

    def test_fetches_subtitles(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch("panel.tasks.subtitles.requests", MockRequest)
        mocker.patch("panel.tasks.subtitles.get_hash", lambda x: "somehash")
        mocker.patch(
            "panel.tasks.subtitles._get_response_from_api", _mock_get_response_from_api
        )
        mocker.patch.object(settings, "SUBTITLE_LANGS", "eng,ger")
        subtitle = tmp_path / "test.srt"
        subtitle.touch()
        subtitle_dir: str = "vtt_subtitles"
        movie_content: MovieContent = MovieContentFactory(full_path=str(tmp_path))
        MovieFactory.create(movie_content=[movie_content])
        langs: List[str] = get_subtitle_language()

        assert not movie_content.movie_subtitle.exists()

        fetch_subtitles(
            movie_content_id=movie_content.id, limit=2, delete_original=True
        )

        assert (tmp_path / subtitle_dir).is_dir()
        for lang in langs:
            assert (tmp_path / subtitle_dir / f"{lang}1.vtt").is_file()
            assert (tmp_path / subtitle_dir / f"{lang}2.vtt").is_file()
            assert not (tmp_path / subtitle_dir / f"{lang}1.srt").is_file()
            assert not (tmp_path / subtitle_dir / f"{lang}2.srt").is_file()
            assert not (tmp_path / subtitle_dir / f"{lang}3.vtt").is_file()
            assert not (tmp_path / subtitle_dir / f"{lang}3.srt").is_file()

        assert movie_content.movie_subtitle.count() == 5
        assert movie_content.movie_subtitle.first().full_path == str(
            tmp_path / subtitle_dir / f"{langs[0]}1.vtt"
        )

        assert {i.full_path for i in movie_content.movie_subtitle.all()}.issubset(
            {str(i) for i in (tmp_path / subtitle_dir).iterdir()}
        )

        assert movie_content.movie_subtitle.last().full_path == str(
            tmp_path / subtitle_dir / "org1.vtt"
        )


class TestGetSubtitlesFromPath:
    def test_simple_directory(self, tmp_path: PosixPath) -> None:
        subtitles: Set[PosixPath] = _get_subtitles_from_path(
            CreateFileTree.setup_basic(tmp_path)
        )

        assert len(subtitles) == 1
        assert next(iter(subtitles)).name == "test video file.srt"

    def test_complicated_directory(self, tmp_path: PosixPath) -> None:
        subtitles: Set[PosixPath] = _get_subtitles_from_path(
            CreateFileTree.setup_complicated(tmp_path)
        )

        assert len(subtitles) == 2
        assert {vid.name for vid in subtitles} == {
            "English subtitles.srt",
            "Spanish subtitles.srt",
        }

    def test_folder_structure(self, tmp_path: PosixPath) -> None:
        subtitles: Set[PosixPath] = _get_subtitles_from_path(
            CreateFileTree.setup_two_fold_depth(tmp_path)
        )

        assert len(subtitles) == 2
        assert Path(next(iter(subtitles))).parent.name == "raw_videos"
        assert Path(next(iter(subtitles))).parent.parent.name == "trailers"

    def test_ignores_subtitle_folder(self, tmp_path: PosixPath) -> None:
        subtitles_dir: PosixPath = tmp_path / "vtt_subtitles"
        subtitles_dir.mkdir(exist_ok=True)
        ignore: PosixPath = subtitles_dir / "org1.srt"
        include: PosixPath = tmp_path / "some subtitle.srt"
        ignore.touch()
        include.touch()

        subtitles: Set[PosixPath] = _get_subtitles_from_path(
            root=tmp_path, subtitles_folder=subtitles_dir
        )

        assert len(subtitles) == 1
        assert ignore not in subtitles
        assert include in subtitles


def test_search_existing_subtitles_and_move(tmp_path: PosixPath) -> None:
    CreateFileTree.setup_two_fold_depth(tmp_path)
    sub_folder: PosixPath = tmp_path / "subtitles"
    sub_folder.mkdir(exist_ok=True)

    _search_existing_subtitles_and_move(
        main_folder=tmp_path, subtitles_folder=sub_folder
    )

    for index, _f in enumerate(sub_folder.iterdir()):
        assert _f.is_file()
        assert _f.suffix == ".srt"
        assert _f.name == f"org{index + 1}.srt"


class TestGetEncoding:
    def test_accidental_empty_should_return_utf_8(self) -> None:
        assert _get_encoding(None) == "utf-8"

    def test_cp_encodings_should_return_without_cp(self) -> None:
        assert _get_encoding("CP1252") == "1252"

    def test_should_return_encoding_as_is(self) -> None:
        assert _get_encoding("iso8859_2") == "iso8859_2"
