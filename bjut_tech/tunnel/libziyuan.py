from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from ._base import AbstractTunnel
from ..auth import LibziyuanAuthentication
from ..persistence import get_persistence

if TYPE_CHECKING:
    from httpx import Client
    from ..persistence import AbstractPersistenceProvider
    from .._config import ConfigRegistry


class LibraryTunnel(AbstractTunnel):

    def __init__(self, session: Client, persistence: AbstractPersistenceProvider, username: str, password: str):
        super().__init__(session)

        self.auth = LibziyuanAuthentication(persistence, username, password)
        self.auth.authenticate(self._session)

    def authenticate(self):
        self.auth.authenticate(self._session)

    def transform_url(self, url: str) -> str:
        parsed_url = urlparse(url)

        is_https = parsed_url.scheme == 'https'
        hostname = parsed_url.hostname
        port = parsed_url.port

        if hostname.endswith('libziyuan.bjut.edu.cn'):
            # already webvpn url
            return url
        else:
            hostname = hostname.replace('-', '--').replace('.', '-')

        if port is None:
            if is_https:
                hostname += '-s'
        elif is_https:
            hostname += f'-{port}-p-s'
        else:
            hostname += f'-{port}-p'

        netloc = f'{hostname}.libziyuan.bjut.edu.cn:8118'
        return parsed_url._replace(scheme='http', netloc=netloc).geturl()

    @classmethod
    def get_name(cls) -> str:
        return 'Library WebVPN'

    @classmethod
    def get_priority(cls) -> int:
        return 21

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        return cls(session, get_persistence(config), config['CAS_USERNAME'], config['CAS_PASSWORD'])
