from __future__ import annotations

import socket
import time
from functools import lru_cache
from typing import TYPE_CHECKING

from ._base import AbstractTunnel

if TYPE_CHECKING:
    from httpx import Client
    from .._config import ConfigRegistry


@lru_cache(maxsize=1)
def availability_check(time_hash) -> bool:
    del time_hash  # invalidate cache when time_hash changes

    try:
        # try to connect to a known server
        sock = socket.create_connection(('172.20.4.15', 80), timeout=1)
        sock.close()
        return True
    except OSError or TimeoutError:
        return False


class NoTunnel(AbstractTunnel):

    def authenticate(self):
        pass

    def transform_url(self, url: str) -> str:
        return url

    def recover_url(self, url: str) -> str:
        return url

    def transform_cookie(self, **kwargs) -> dict:
        return kwargs

    @classmethod
    def get_name(cls) -> str:
        return 'Direct'

    @classmethod
    def get_priority(cls) -> int:
        return 99

    @classmethod
    def is_available(cls) -> bool:
        return availability_check(time.time() // 600)

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        return cls(session)
