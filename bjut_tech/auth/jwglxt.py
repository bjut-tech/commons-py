from __future__ import annotations

import time
from base64 import b64decode, b64encode
from math import floor
from typing import Tuple, Optional, TYPE_CHECKING

import rsa
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from ..tunnel import AbstractTunnel


class JwglxtAuthentication:

    def __init__(self, tunnel: AbstractTunnel, username: str, password: str):
        self.key: Optional[Tuple[str, str]] = None
        self.tunnel = tunnel

        self.username = username
        self.password = password

        if not self.username or not self.password:
            raise ValueError('username and password are required')

    def check(self) -> bool:
        session = self.tunnel.get_session()
        url = self.tunnel.transform_url('https://jwglxt.bjut.edu.cn/xtgl/index_initMenu.html')

        response = session.get(url, params={
            '_t': floor(time.time() * 1000)
        }, follow_redirects=False)

        return response.status_code == 200

    def authenticate(self):
        self._get_key()
        pub_key = rsa.PublicKey(int(self.key[0], 16), int(self.key[1], 16))
        password_encrypted = rsa.encrypt(self.password.encode('utf-8'), pub_key)
        password_encrypted = b64encode(password_encrypted).decode()

        session = self.tunnel.get_session()
        url = self.tunnel.transform_url('https://jwglxt.bjut.edu.cn/xtgl/login_slogin.html')
        session.post(url, params={
            'time': floor(time.time() * 1000)
        }, data={
            'csrftoken': self._get_csrf_token(),
            'yhm': self.username,
            'mm': password_encrypted
        })

        if not self.check():
            raise RuntimeError('Login failed')

    def _get_key(self):
        if self.key is not None:
            return

        session = self.tunnel.get_session()
        url = self.tunnel.transform_url('https://jwglxt.bjut.edu.cn/xtgl/login_getPublicKey.html')

        response = session.get(url)
        response.raise_for_status()
        data = response.json()

        self.key = (
            b64decode(data['modulus'].encode()).hex(),
            b64decode(data['exponent'].encode()).hex()
        )

    def _get_csrf_token(self):
        session = self.tunnel.get_session()
        url = self.tunnel.transform_url('https://jwglxt.bjut.edu.cn/xtgl/login_slogin.html')

        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('input', {'id': 'csrftoken'}).get('value')
