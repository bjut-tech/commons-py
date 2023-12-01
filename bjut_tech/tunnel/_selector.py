from __future__ import annotations

from typing import TYPE_CHECKING

from .direct import NoTunnel
from .libziyuan import LibraryTunnel

if TYPE_CHECKING:
    from httpx import Client
    from ._base import AbstractTunnel
    from .._config import ConfigRegistry

_TUNNELS = [
    NoTunnel,
    LibraryTunnel
]


class TunnelSelector:

    def __init__(self, session: Client, config: ConfigRegistry):
        self._session = session
        self._config = config

    def get_best(self) -> AbstractTunnel:
        priorities = []
        for i, tunnel_cls in enumerate(_TUNNELS):
            priorities.append((i, tunnel_cls.get_priority()))

        priorities.sort(key=lambda x: x[1], reverse=True)

        for i, _ in priorities:
            tunnel_cls = _TUNNELS[i]
            if tunnel_cls.is_available():
                print(f'Tunnel selected: [{tunnel_cls.get_priority()}] {tunnel_cls.get_name()}')
                return tunnel_cls.construct(self._session, self._config)

        raise RuntimeError('No tunnel available')

    @staticmethod
    def check_availability(cls_name: str) -> bool:
        for tunnel_cls in _TUNNELS:
            if tunnel_cls.__name__ == cls_name:
                return tunnel_cls.is_available()
        return False
