import gzip
from dataclasses import dataclass
from typing import Optional, Any, Dict, List

import requests

from panel.tasks.tests.test_utils import TORRENTS


class MockClient:
    def __init__(self, url: str = "", verify: bool = False):
        ...

    @staticmethod
    def login(username: str, password: str) -> Optional[str]:
        return None

    @staticmethod
    def torrents(category: str = "") -> List[Dict[str, Any]]:
        if not category:
            return TORRENTS

        return [torrent for torrent in TORRENTS if torrent.get("category") == category]

    @staticmethod
    def remove_category(category: str = "") -> None:
        ...

    @staticmethod
    def create_category(category: str = "") -> None:
        ...

    @staticmethod
    def download_from_link(link: str = "", **kwargs) -> None:
        ...

    @staticmethod
    def download_from_file(link: str = "", **kwargs) -> None:
        ...


class MockClientRaises:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.ConnectionError()


@dataclass
class MockSubprocess:
    stdout: bytes


class MockRequest:
    _content: bytes = b"testfile"
    _text: str = '{"status": []}'
    _json: Dict[str, Any] = {"movie_results": []}

    def __init__(self, url: str = None):
        self.url = url
        if url.startswith("http"):
            self._status_code = 200
        else:
            self._status_code = 500

    @staticmethod
    def get(url: str, **kwargs):
        return MockRequest(url=url)

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def content(self) -> bytes:
        return gzip.compress(self._content, compresslevel=0)

    @property
    def text(self) -> str:
        return self._text

    def json(self) -> Dict[str, Any]:
        return self._json
