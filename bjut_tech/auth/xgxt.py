from __future__ import annotations

from typing import TYPE_CHECKING

from .cas import CasAuthentication

if TYPE_CHECKING:
    from ..tunnel import AbstractTunnel


class XgxtAuthentication:

    def __init__(
        self,
        tunnel: AbstractTunnel,
        username: str,
        password: str
    ):
        self.tunnel = tunnel
        self.base_url = 'https://xgxt.bjut.edu.cn'

        self.username = username
        self.password = password
        self.cas = CasAuthentication(tunnel, username, password)

        if not self.username or not self.password:
            raise ValueError('username and password are required')

    def check(self) -> bool:
        session = self.tunnel.get_session()
        url = self.tunnel.transform_url(f'{self.base_url}/index/summary/personal.htm')

        response = session.get(url, follow_redirects=False)

        return response.status_code == 200

    def authenticate(self):
        self.cas.authenticate(f'{self.base_url}/bgdLoginAction/cas.htm')
