from __future__ import annotations

import socket
from functools import lru_cache
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from ._base import AbstractTunnel
from ..auth import LibziyuanAuthentication
from ..persistence import get_persistence

if TYPE_CHECKING:
    from httpx import Client
    from ..persistence import AbstractPersistenceProvider
    from .._config import ConfigRegistry


@lru_cache(maxsize=1)
def availability_check(time_hash) -> bool:
    del time_hash  # invalidate cache when time_hash changes

    try:
        sock = socket.create_connection(('libziyuan.bjut.edu.cn', 8118), timeout=1)
        sock.close()
        return True
    except OSError or TimeoutError:
        return False


class LibraryTunnel(AbstractTunnel):

    def __init__(self, session: Client, persistence: AbstractPersistenceProvider, username: str, password: str):
        super().__init__(session)

        self.auth = LibziyuanAuthentication(persistence, username, password)
        self.authenticate()

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

    def recover_url(self, url: str) -> str:
        parsed_url = urlparse(url)

        if not parsed_url.netloc.endswith('libziyuan.bjut.edu.cn:8118'):
            # not a webvpn url
            return url

        subdomain = parsed_url.netloc.replace('.libziyuan.bjut.edu.cn:8118', '')

        parts = subdomain.split('-')
        is_https = False
        port = None
        if parts and parts[-1] == 's':
            is_https = True
            parts.pop()
        if parts and parts[-1] == 'p':
            parts.pop()
            if parts and parts[-1].isdigit():
                port = int(parts[-1])
                parts.pop()

        hostname = '-'.join(parts)
        hostname = hostname.replace('--', '\x00')
        hostname = hostname.replace('-', '.')
        hostname = hostname.replace('\x00', '-')

        scheme = 'https' if is_https else 'http'
        if port is not None:
            netloc = f"{hostname}:{port}"
        else:
            netloc = hostname

        return parsed_url._replace(scheme=scheme, netloc=netloc).geturl()

    def transform_cookie(self, **kwargs) -> dict:
        if 'secure' in kwargs:
            kwargs['secure'] = False

        if 'domain' in kwargs:
            if kwargs['domain'][0] == '.':
                kwargs['name'] += '_-_' + kwargs['domain'][1:]
                kwargs['domain'] = '.libziyuan.bjut.edu.cn'
            else:
                domain = kwargs['domain'].replace('-', '--').replace('.', '-')
                domain += '-s'  # TODO: find a better way to handle https domains
                domain += '.libziyuan.bjut.edu.cn'
                kwargs['domain'] = domain

        return kwargs

    @classmethod
    def get_name(cls) -> str:
        return 'Library WebVPN'

    @classmethod
    def get_priority(cls) -> int:
        return 21

    @classmethod
    def is_available(cls) -> bool:
        # libziyuan tunnel is deprecated, use webvpn instead
        return False

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        return cls(session, get_persistence(config), config['CAS_USERNAME'], config['CAS_PASSWORD'])
