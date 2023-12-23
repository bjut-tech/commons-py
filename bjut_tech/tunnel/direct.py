from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from ._base import AbstractTunnel

if TYPE_CHECKING:
    from httpx import Client
    from .._config import ConfigRegistry


class NoTunnel(AbstractTunnel):

    def authenticate(self):
        pass

    def transform_url(self, url: str) -> str:
        return url

    @classmethod
    def get_name(cls) -> str:
        return 'Direct'

    @classmethod
    def get_priority(cls) -> int:
        return 99

    @classmethod
    def is_available(cls) -> bool:
        try:
            # try to connect a known server
            sock = socket.create_connection(('172.20.4.15', 80), timeout=0.1)
            sock.close()

        except OSError or TimeoutError:
            # other kinds of exceptions are not expected
            return False

        return True

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        return cls(session)
