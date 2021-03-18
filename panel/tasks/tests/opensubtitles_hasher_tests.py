from pathlib import PosixPath

import pytest

from panel.tasks.opensubtitles_hasher import get_hash


@pytest.fixture
def test_file(tmp_path: PosixPath) -> PosixPath:
    _test_file: PosixPath = tmp_path / "test_video.mp4"
    with open(str(_test_file), "wb") as out:
        out.truncate(1024 * 1024)

    return _test_file


def test_get_hash(test_file: PosixPath) -> None:
    assert get_hash(str(test_file)) == "0000000000100000"


def test_raises_when_file_too_small(tmp_path: PosixPath) -> None:
    (tmp_path / "small.mp4").touch()

    with pytest.raises(Exception) as exc:
        get_hash(str(tmp_path / "small.mp4"))

    assert str(exc.value) == "SizeError"


def test_raises_when_file_does_not_exist() -> None:
    with pytest.raises(Exception) as exc:
        get_hash("/some/file/location")

    assert (
        str(exc.value) == "[Errno 2] No such file or directory: '/some/file/location'"
    )
