from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Client, Cookies
    from .._config import ConfigRegistry


class AbstractTunnel:

    def __init__(self, session: Client):
        self._session = session

    def get_session(self) -> Client:
        return self._session

    def authenticate(self):
        raise NotImplementedError

    def transform_url(self, url: str) -> str:
        raise NotImplementedError

    def transform_cookie(self, **kwargs):
        raise NotImplementedError

    def resume(self, cookies: Cookies):
        self._session.cookies = cookies
        self.authenticate()

    @classmethod
    def get_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_priority(cls) -> int:
        raise NotImplementedError

    @classmethod
    def is_available(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        raise NotImplementedError
