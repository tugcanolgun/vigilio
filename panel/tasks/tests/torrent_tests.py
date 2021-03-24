import copy
import json
import os
import subprocess
from pathlib import PosixPath, Path
from typing import Any, Set, Dict, List

import celery
import pytest
from django.conf import settings
from django.test import override_settings
from pytest_mock import MockerFixture

import panel
from panel.models import MovieTorrent
from panel.tasks.tests.mocks import MockClient, MockClientRaises, MockSubprocess
from panel.tasks.tests.test_utils import RAW_INFO, TORRENTS
from panel.tasks.torrent import (
    get_qbittorrent_client,
    _get_qbittorrent_url,
    is_torrent_complete,
    _get_videos_from_path,
    get_videos_from_folder,
    _get_video_raw_detail,
    _convert_video_to_mp4,
    _hash,
    _get_video_detail,
    VideoDetail,
    _copy_mp4_to_new_hash_mp4,
    _create_and_write_to_meta_file,
    _process_videos,
    _get_media_folder,
    _change_and_move_parent_folder,
    _get_relative_path,
    check_and_process_torrent,
    _get_root_path,
    process_videos_in_folder,
    download_torrent,
)
from panel.tests.factories import MovieTorrentFactory
from stream.models import MovieContent, Movie
from stream.tests.factories import MovieContentFactory, MovieFactory


class TestGetQbittorrentClient:
    def test_get_qbittorrent_client(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)

        assert type(get_qbittorrent_client()) is MockClient

    def test_login_fails(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch(
            "panel.tasks.tests.mocks.MockClient.login", lambda x, y, z: "Fails."
        )

        with pytest.raises(Exception, match="Could not login to qbittorrent."):
            get_qbittorrent_client()

    def test_qbittorrent_not_running(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClientRaises)
        with pytest.raises(Exception, match="Qbittorrent is not running."):
            get_qbittorrent_client()


class TestGetQbittorrentUrl:
    @override_settings()
    def test_without_setting(self) -> None:
        del settings.QBITTORRENT_URL
        with pytest.raises(Exception):
            _get_qbittorrent_url()

    @pytest.mark.parametrize("qbit", [None, "", []])
    def test_with_incorrect_settings(self, qbit: Any, mocker: MockerFixture) -> None:
        mocker.patch.object(settings, "QBITTORRENT_URL", qbit)
        with pytest.raises(Exception) as exc:
            _get_qbittorrent_url()

        assert str(exc.value) == "QBITTORRENT_URL could not be found or empty."

    def test_with_correct_setting(self, mocker: MockerFixture) -> None:
        qbit_test: str = "http://localhost"
        mocker.patch.object(settings, "QBITTORRENT_URL", qbit_test)

        assert _get_qbittorrent_url() == qbit_test


@pytest.mark.usefixtures("db")
class TestIsTorrentComplete:
    def test_is_torrent_complete(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=1)

        assert is_torrent_complete(movie_torrent.id) is True

    def test_is_not_torrent_complete(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=2)

        assert is_torrent_complete(movie_torrent.id) is False

    def test_without_any_torrent(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=9999)

        with pytest.raises(Exception) as exc:
            is_torrent_complete(movie_torrent.id)

        assert (
            str(exc.value)
            == f"Movie torrent {movie_torrent.id} does not have any torrent associated with"
        )


class TestGetVideosFromPath:
    def test_simple_directory(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = _get_videos_from_path(
            CreateFileTree.setup_basic(tmp_path)
        )

        assert len(videos) == 1
        assert next(iter(videos)).name == "test video file.mp4"

    def test_complicated_directory(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = _get_videos_from_path(
            CreateFileTree.setup_complicated(tmp_path)
        )

        assert len(videos) == 4
        assert {vid.name for vid in videos} == {
            "test video file.mp4",
            "another video.mkv",
            "trailer HD.mp4",
            "raw video.mp4",
        }

    def test_folder_structure(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = _get_videos_from_path(
            CreateFileTree.setup_two_fold_depth(tmp_path)
        )

        assert len(videos) == 1
        assert Path(next(iter(videos))).parent.name == "raw_videos"
        assert Path(next(iter(videos))).parent.parent.name == "trailers"


class TestGetVideosFromFolder:
    def test_with_file(self, tmp_path) -> None:
        test_file = tmp_path / "testfile.mp4"
        test_file.touch()

        result: Set[PosixPath] = get_videos_from_folder(str(test_file))

        assert len(result) == 1
        assert next(iter(result)).name == "testfile.mp4"

    def test_with_non_video_file(self, tmp_path) -> None:
        test_file = tmp_path / "testfile.txt"
        test_file.touch()

        with pytest.raises(Exception) as exc:
            get_videos_from_folder(str(test_file))

        assert str(exc.value) == f"Given single file is not a video: {str(test_file)}"

    def test_simple_directory(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = get_videos_from_folder(
            str(CreateFileTree.setup_basic(tmp_path))
        )

        assert len(videos) == 1
        assert next(iter(videos)).name == "test video file.mp4"

    def test_complicated_directory(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = get_videos_from_folder(
            str(CreateFileTree.setup_complicated(tmp_path))
        )

        assert len(videos) == 4
        assert {vid.name for vid in videos} == {
            "test video file.mp4",
            "another video.mkv",
            "trailer HD.mp4",
            "raw video.mp4",
        }

    def test_folder_structure(self, tmp_path: PosixPath) -> None:
        videos: Set[PosixPath] = get_videos_from_folder(
            str(CreateFileTree.setup_two_fold_depth(tmp_path))
        )

        assert len(videos) == 1
        assert Path(next(iter(videos))).parent.name == "raw_videos"
        assert Path(next(iter(videos))).parent.parent.name == "trailers"


def test_get_video_raw_detail(tmp_path: PosixPath, mocker: MockerFixture) -> None:
    run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
    run.return_value = MockSubprocess(stdout=json.dumps(RAW_INFO).encode("UTF-8"))
    video_file: PosixPath = tmp_path / "video.mp4"
    video_file.touch()

    assert _get_video_raw_detail(video_file) == RAW_INFO
    subprocess.run.assert_called_once_with(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            str(video_file),
        ],
        stderr=-2,
        stdout=-1,
    )

    run.return_value = MockSubprocess(stdout=b"bad result")

    assert _get_video_raw_detail(video_file) == {}


def test_convert_video_to_mp4(tmp_path: PosixPath, mocker: MockerFixture) -> None:
    mocker.patch("panel.tasks.torrent.subprocess.run")
    video_file: PosixPath = tmp_path / "video.mp4"
    video_file.touch()
    new_video_path: Path = video_file.parent / (_hash(video_file.name) + ".mp4")

    _convert_video_to_mp4(video_file)

    subprocess.run.assert_called_once_with(
        ["ffmpeg", "-i", str(video_file), "-c", "copy", str(new_video_path)],
        stderr=-2,
        stdout=-1,
    )


def test_get_video_detail(tmp_path: PosixPath, mocker: MockerFixture) -> None:
    run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
    raw: Dict[str, str] = {"stream": "test"}
    run.return_value = MockSubprocess(stdout=json.dumps(raw).encode("UTF-8"))
    video: PosixPath = tmp_path / "video.mp4"
    video.touch()

    result: VideoDetail = _get_video_detail(video)

    assert result.full_path == str(video.parent / (_hash(video.name) + ".mp4"))
    assert result.file_name == _hash(video.name)
    assert result.file_extension == ".mp4"
    assert result.source_file_name == video.name
    assert result.source_file_extension == video.suffix
    assert result.width == 0
    assert result.height == 0
    assert result.duration == 0
    assert result.raw == raw


def test_copy_mp4_to_new_hash_mp4(tmp_path: PosixPath) -> None:
    video: PosixPath = tmp_path / "video test name.mkv"
    video.touch()

    _copy_mp4_to_new_hash_mp4(video)

    assert (tmp_path / (_hash(video.name) + ".mp4")).exists()


def test_create_and_write_to_meta_file(tmp_path: PosixPath) -> None:
    video: PosixPath = tmp_path / "video test name.mkv"
    video.touch()

    _create_and_write_to_meta_file(video)

    assert (tmp_path / "meta.txt").exists()
    with open(str(tmp_path / "meta.txt"), "r") as f:
        assert f.read() == "video test name.mkv\n"


class TestProcessVideos:
    def test_without_delete_original(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
        run.return_value = MockSubprocess(stdout=b'{"stream":[]}')
        video1: PosixPath = tmp_path / "video.mkv"
        video2: PosixPath = tmp_path / "test.mp4"
        video1.touch()
        video2.touch()

        result: List[VideoDetail] = _process_videos({video1, video2})

        assert len(result) == 2
        assert result[0].source_file_name in {video1.name, video2.name}
        assert result[1].source_file_name in {video1.name, video2.name}
        assert result[1].file_name in {_hash(video1.name), _hash(video2.name)}
        assert video1.exists()
        assert video2.exists()
        assert (tmp_path / (_hash(video2.name) + ".mp4")).exists()

    def test_with_delete_original(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
        run.return_value = MockSubprocess(stdout=b'{"stream":[]}')
        video1: PosixPath = tmp_path / "video.mkv"
        video2: PosixPath = tmp_path / "test.mp4"
        video1.touch()
        video2.touch()

        _process_videos({video1, video2}, delete_original=True)

        assert not video1.exists()
        assert not video2.exists()
        assert (tmp_path / (_hash(video2.name) + ".mp4")).exists()


@override_settings(MEDIA_FOLDER="/")
def test_get_media_folder(tmp_path) -> None:
    assert _get_media_folder() == "/"


class TestChangeAndMoveParentFolder:
    def test_returns_new_folder(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        old_folder: PosixPath = tmp_path / "old_folder"
        old_folder.mkdir(exist_ok=True)

        result: str = _change_and_move_parent_folder(str(old_folder))

        assert Path(result).is_dir()
        assert Path(result).name == _hash("old_folder")
        assert not old_folder.exists()

    def test_passing_a_file(self, tmp_path: PosixPath, mocker: MockerFixture) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        new_file: PosixPath = tmp_path / "test.txt"
        new_file.touch()

        result: str = _change_and_move_parent_folder(str(new_file))

        assert result == str(new_file)

    def test_returns_folder_from_base_dir(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "BASE_DIR", str(tmp_path))
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        folder_name: str = "s0med1r"
        (tmp_path / folder_name).mkdir(exist_ok=True)

        result: str = _change_and_move_parent_folder(f"/{folder_name}")

        assert result != f"/{folder_name}"
        assert Path(result).name == _hash(folder_name)
        assert not (tmp_path / folder_name).exists()
        assert (tmp_path / _hash(folder_name)).exists()


class TestGetRelativePath:
    def test_returns_relative_path(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        root_folder: PosixPath = tmp_path / "some_other_folder"
        root_folder.mkdir(exist_ok=True)
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))

        result: str = _get_relative_path(str(root_folder))

        assert result == "some_other_folder"

    def test_root_folder_does_not_start_with_media_folder(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        media_folder: PosixPath = tmp_path / "media_folder"
        media_folder.mkdir(exist_ok=True)
        mocker.patch.object(settings, "MEDIA_FOLDER", str(media_folder))

        result: str = _get_relative_path(str(tmp_path))

        assert result == str(tmp_path)

    def test_unexpected_root_folder_returns_itself(self) -> None:
        assert _get_relative_path({}) == {}


@pytest.mark.usefixtures("db")
class TestCheckAndProcessTorrent:
    def test_raises_if_no_movie_content(self) -> None:
        with pytest.raises(Exception) as exc:
            check_and_process_torrent(-10)

        assert str(exc.value) == f"MovieTorrent {-10} does not exists"

    def test_returns_none_if_torrent_is_complete(self) -> None:
        movie_torrent: MovieTorrent = MovieTorrentFactory()
        movie_torrent.is_complete = True
        movie_torrent.save()

        assert check_and_process_torrent(movie_torrent.id) is None

    def test_retries_if_torrent_not_complete(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch("panel.tasks.torrent.process_videos_in_folder")
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=2)

        with pytest.raises(celery.exceptions.Retry):
            check_and_process_torrent(movie_torrent.id)

    def test_if_torrent_is_complete(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch("shutil.move")
        mocker.patch("panel.tasks.torrent.process_videos_in_folder")
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=1)
        torrents: List[Dict[str, Any]] = MockClient().torrents(
            category=str(movie_torrent.id)
        )

        check_and_process_torrent(movie_torrent.id)

        movie_torrent.refresh_from_db()

        assert movie_torrent.is_complete is True
        assert movie_torrent.movie_content.full_path == torrents[0]["content_path"]
        assert movie_torrent.movie_content.main_folder == torrents[0]["content_path"]


@pytest.mark.usefixtures("db")
class TestGetRootPath:
    def test_if_full_path_is_a_dir(self, tmp_path: PosixPath) -> None:
        movie_content: MovieContent = MovieContentFactory()
        movie_content.full_path = str(tmp_path)
        movie_content.save()

        assert _get_root_path(movie_content.id) == str(tmp_path)

    def test_if_full_path_is_a_file(self, tmp_path: PosixPath) -> None:
        new_file: PosixPath = tmp_path / "test.mp4"
        new_file.touch()
        movie_content: MovieContent = MovieContentFactory()
        movie_content.full_path = str(new_file)
        movie_content.save()

        assert _get_root_path(movie_content.id) == str(tmp_path)

    def test_main_folder_is_defined_but_not_full_path(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        folder: PosixPath = tmp_path / "folder"
        folder.mkdir(exist_ok=True)
        movie_content: MovieContent = MovieContentFactory()
        movie_content.main_folder = folder.name
        movie_content.save()

        assert _get_root_path(movie_content.id) == str(folder)

    def test_full_path_as_file_and_main_folder_as_file(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        new_file: PosixPath = tmp_path / "test.mp4"
        new_file.touch()
        movie_content: MovieContent = MovieContentFactory()
        movie_content.full_path = str(new_file)
        movie_content.main_folder = new_file.name
        movie_content.save()

        assert _get_root_path(movie_content.id) == str(tmp_path)

    def test_raises_if_no_movie_torrent(self):
        movie_content: MovieContent = MovieContentFactory()

        with pytest.raises(Exception) as exc:
            _get_root_path(movie_content.id)

        assert (
            str(exc.value) == f"MovieTorrent could not be found for {movie_content.id}"
        )

    def test_raises_if_no_torrents(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=999)

        with pytest.raises(Exception) as exc:
            _get_root_path(movie_torrent.movie_content.id)

        assert (
            str(exc.value)
            == f"Torrent could not be found for movie content: {movie_torrent.movie_content.id}"
        )

    def test_returns_torrent_content_path(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        _torrents: List[Dict[str, Any]] = copy.deepcopy(TORRENTS)
        new_folder: PosixPath = tmp_path / "folder"
        new_folder.mkdir(exist_ok=True)
        new_file: PosixPath = new_folder / "test.mp4"
        new_file.touch()
        _torrents[0]["content_path"] = str(new_folder)
        _torrents[1]["content_path"] = str(new_file)
        mocker.patch.object(panel.tasks.tests.mocks, "TORRENTS", _torrents)
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=1)

        result: str = _get_root_path(movie_torrent.movie_content.id)

        assert result == str((tmp_path / "folder"))

    def test_returns_folder_under_media_folder(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        _torrents: List[Dict[str, Any]] = copy.deepcopy(TORRENTS)
        torrent_folder: PosixPath = tmp_path / "new folder"
        torrent_folder.mkdir(exist_ok=True)
        (tmp_path / _hash(torrent_folder.name)).mkdir(exist_ok=True)
        movie_torrent: MovieTorrent = MovieTorrentFactory(id=1)
        _torrents[0]["content_path"] = "/some/nonexist/folder/" + torrent_folder.name
        mocker.patch.object(panel.tasks.tests.mocks, "TORRENTS", _torrents)
        mocker.patch("panel.tasks.torrent.Client", MockClient)

        result: str = _get_root_path(movie_torrent.movie_content.id)

        assert result == str(tmp_path / _hash(torrent_folder.name))


@pytest.mark.usefixtures("db")
class TestProcessVideosInFolder:
    def test_raises_if_no_process_videos(self, tmp_path: PosixPath) -> None:
        movie_content: MovieContent = MovieContentFactory()
        movie_content.full_path = str(tmp_path)
        movie_content.save()

        with pytest.raises(Exception) as exc:
            process_videos_in_folder(movie_content.id)

        assert (
            str(exc.value)
            == f"No videos are returned to be processed for movie content {movie_content.id}"
        )

    def test_updates_movie_content_and_movie(
        self, mocker: MockerFixture, tmp_path: PosixPath
    ) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        mocker.patch("panel.tasks.torrent.fetch_subtitles.delay")
        mocker.patch("os.chmod")
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
        run.return_value = MockSubprocess(stdout=json.dumps(RAW_INFO).encode("UTF-8"))
        movie_content: MovieContent = MovieContentFactory()
        movie: Movie = MovieFactory.create(movie_content=[movie_content])
        movie_content.full_path = str(tmp_path)
        movie_content.save()
        video: PosixPath = tmp_path / "video.mkv"
        video.touch()

        process_videos_in_folder(movie_content.id)
        movie_content.refresh_from_db()
        movie.refresh_from_db()
        hashed_title: str = _hash(video.name)

        assert movie_content.full_path == str((tmp_path / (f"{hashed_title}.mp4")))
        assert movie_content.file_name == hashed_title
        assert movie_content.relative_path == f"{hashed_title}.mp4"
        assert movie_content.file_extension == ".mp4"
        assert movie_content.source_file_name == video.name
        assert movie_content.source_file_extension == video.suffix
        assert movie_content.resolution_width == RAW_INFO["streams"][0]["width"]
        assert movie_content.resolution_height == RAW_INFO["streams"][0]["height"]
        assert movie_content.is_ready is True
        assert movie.duration == int(float(RAW_INFO["streams"][0]["duration"]))

    def test_sub_functions_are_called(
        self, tmp_path: PosixPath, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(settings, "MEDIA_FOLDER", str(tmp_path))
        mocker.patch("panel.tasks.torrent.fetch_subtitles.delay")
        mocker.patch("os.chmod")
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        get_root_path = mocker.spy(panel.tasks.torrent, "_get_root_path")
        get_videos_from_folder = mocker.spy(
            panel.tasks.torrent, "get_videos_from_folder"
        )
        process_videos = mocker.spy(panel.tasks.torrent, "_process_videos")
        run = mocker.patch("panel.tasks.torrent.subprocess.run", autospec=True)
        run.return_value = MockSubprocess(stdout=json.dumps(RAW_INFO).encode("UTF-8"))
        movie_content: MovieContent = MovieContentFactory()
        MovieFactory.create(movie_content=[movie_content])
        movie_content.full_path = str(tmp_path)
        movie_content.save()
        video: PosixPath = tmp_path / "video.mkv"
        video.touch()
        hashed_title: str = _hash(video.name)

        process_videos_in_folder(
            movie_content_id=movie_content.id, delete_original=True
        )

        get_root_path.assert_called_once_with(movie_content_id=movie_content.id)
        get_videos_from_folder.assert_called_once_with(root_path=str(tmp_path))
        process_videos.assert_called_once_with(videos={video}, delete_original=True)
        os.chmod.assert_called_once_with(str((tmp_path / f"{hashed_title}.mp4")), 0o644)
        panel.tasks.torrent.fetch_subtitles.delay.assert_called_once_with(
            movie_content_id=movie_content.id,
            limit=5,
            delete_original=settings.DELETE_ORIGINAL_FILES,
        )


@pytest.mark.usefixtures("db")
class TestDownloadTorrent:
    def test_raises_if_no_movie_content(self) -> None:
        with pytest.raises(MovieContent.DoesNotExist) as exc:
            download_torrent(-999)

        assert str(exc.value) == "MovieContent matching query does not exist."

    def test_creates_movie_torrent(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch("panel.tasks.torrent.check_and_process_torrent.delay")
        mocker.patch("panel.tasks.torrent.download_movie_info.delay")
        movie_content: MovieContent = MovieContentFactory()
        MovieFactory.create(movie_content=[movie_content])

        assert not MovieTorrent.objects.filter(movie_content=movie_content).exists()

        download_torrent(movie_content_id=movie_content.id)

        assert MovieTorrent.objects.filter(movie_content=movie_content).exists()

    def test_functions_are_called_correctly(self, mocker: MockerFixture) -> None:
        mocker.patch("panel.tasks.torrent.Client", MockClient)
        mocker.patch("panel.tasks.torrent.check_and_process_torrent.delay")
        mocker.patch("panel.tasks.torrent.download_movie_info.delay")
        remove_category = mocker.spy(
            panel.tasks.tests.mocks.MockClient, "remove_category"
        )
        create_category = mocker.spy(
            panel.tasks.tests.mocks.MockClient, "create_category"
        )
        mocker.patch("panel.tasks.torrent.check_and_process_torrent.delay")
        mocker.patch("panel.tasks.torrent.download_movie_info.delay")
        download_from_link = mocker.spy(
            panel.tasks.tests.mocks.MockClient, "download_from_link"
        )
        movie_content: MovieContent = MovieContentFactory()
        MovieFactory.create(movie_content=[movie_content])

        download_torrent(movie_content_id=movie_content.id)

        remove_category.assert_called_once_with(str(movie_content.id))
        create_category.assert_called_once_with(str(movie_content.id))
        download_from_link.assert_called_once_with(
            movie_content.torrent_source, category=str(movie_content.id)
        )
        panel.tasks.torrent.check_and_process_torrent.delay.assert_called_once()
        panel.tasks.torrent.download_movie_info.delay.assert_called_once()


class CreateFileTree:
    @staticmethod
    def setup_basic(tmp_path: PosixPath) -> PosixPath:
        (tmp_path / "test video file.mp4").touch()
        (tmp_path / "banner.jpg").touch()
        (tmp_path / "metadata.txt").touch()
        (tmp_path / "test video file.srt").touch()

        return tmp_path

    @staticmethod
    def setup_complicated(tmp_path: PosixPath) -> PosixPath:
        subtitles = tmp_path / "subtitles"
        subtitles.mkdir()
        trailer = tmp_path / "trailers"
        trailer.mkdir()
        raw_videos = trailer / "raw_videos"
        raw_videos.mkdir()

        (tmp_path / "test video file.mp4").touch()
        (tmp_path / "another video.mkv").touch()
        (tmp_path / "banner.jpg").touch()
        (tmp_path / "metadata.txt").touch()
        (subtitles / "English subtitles.srt").touch()
        (subtitles / "Spanish subtitles.srt").touch()
        (trailer / "trailer 1.mov").touch()
        (trailer / "trailer HD.mp4").touch()
        (raw_videos / "test video file.avi").touch()
        (raw_videos / "raw video.mp4").touch()

        return tmp_path

    @staticmethod
    def setup_two_fold_depth(tmp_path: PosixPath) -> PosixPath:
        trailer = tmp_path / "trailers"
        trailer.mkdir()
        raw_videos = trailer / "raw_videos"
        raw_videos.mkdir()
        (raw_videos / "raw video.mp4").touch()
        (raw_videos / "raw video.srt").touch()
        (raw_videos / "test.srt").touch()

        return tmp_path
