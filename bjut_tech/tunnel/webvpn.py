from __future__ import annotations

import socket
import time
from functools import lru_cache
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ._base import AbstractTunnel
from ..auth import CasAuthentication

if TYPE_CHECKING:
    from httpx import Client
    from .._config import ConfigRegistry


@lru_cache(maxsize=1)
def availability_check() -> bool:
    try:
        sock = socket.create_connection(('webvpn.bjut.edu.cn', 443), timeout=1)
        sock.close()
        return True
    except OSError or TimeoutError:
        return False


class WebvpnTunnel(AbstractTunnel):

    def __init__(self, session: Client, username: str, password: str):
        super().__init__(session)

        self.base_url = 'https://webvpn.bjut.edu.cn'
        self.iv = self.key = b'wrdvpnisthebest!'
        self.auth = CasAuthentication(self, username, password)
        self.authenticate()

    def refresh_info(self):
        session = self.get_session()
        url = f'{self.base_url}/user/info'
        response = session.get(url, params={
            '_t': round(time.time() * 1000)
        }, follow_redirects=False)
        if response.status_code != 200:
            raise RuntimeError('Failed to get webvpn info')
        try:
            data = response.json()
            self.iv = data['wrdvpnIV'].encode()
            self.key = data['wrdvpnKey'].encode()
        except KeyError:
            pass

    def check_authentication(self) -> bool:
        try:
            self.refresh_info()
            return True
        except RuntimeError:
            return False

    def authenticate(self):
        if not self.check_authentication():
            self.auth.authenticate_oauth(f'{self.base_url}/login?cas_login=true')
        if not self.check_authentication():
            raise RuntimeError('Failed to authenticate')

    def transform_url(self, url: str) -> str:
        parsed_base_url = urlparse(self.base_url)
        parsed_url = urlparse(url)
        domain = parsed_url.hostname

        cipher = AES.new(self.key, AES.MODE_CFB, iv=self.iv, segment_size=128)
        padded = pad(domain.encode('utf-8'), AES.block_size)
        encoded = self.iv.hex() + cipher.encrypt(padded).hex()[:len(domain) * 2]

        path = f'/{parsed_url.scheme}'
        if parsed_url.port:
            path += f'-{parsed_url.port}'
        path += f'/{encoded}{parsed_url.path}'

        return parsed_url._replace(scheme=parsed_base_url.scheme, netloc=parsed_base_url.netloc, path=path).geturl()

    def recover_url(self, url: str) -> str:
        parsed_url = urlparse(url)

        parts = parsed_url.path.lstrip('/').split('/', 1)
        if len(parts) == 1:
            return url
        scheme_port_encoded, remainder_path = parts

        if '-' in scheme_port_encoded:
            scheme, port = scheme_port_encoded.split('-', 1)
        else:
            scheme = scheme_port_encoded
            port = None

        parts = remainder_path.split('/', 1)
        if len(parts) == 1:
            encoded_host = parts[0]
            remainder_path = ''
        else:
            encoded_host, remainder_path = parts

        iv_hex = encoded_host[:32]
        encoded_host = encoded_host[32:]
        if len(iv_hex) < 32:
            return url
        try:
            iv = bytes.fromhex(iv_hex)
            encoded_host = bytes.fromhex(encoded_host)
            cipher = AES.new(self.key, AES.MODE_CFB, iv=iv, segment_size=128)
            decrypted_domain = cipher.decrypt(encoded_host)
            try:
                domain = unpad(decrypted_domain, AES.block_size).decode('utf-8')
            except ValueError:
                domain = decrypted_domain.decode('utf-8')
        except ValueError:
            return url

        return parsed_url._replace(
            scheme=scheme,
            netloc=f'{domain}:{port}' if port else domain,
            path=f'/{remainder_path}'
        ).geturl()

    def transform_cookie(self, **kwargs):
        # it seems this tunnel does not support setting cookies
        return kwargs

    @classmethod
    def get_name(cls) -> str:
        return 'WebVPN'

    @classmethod
    def get_priority(cls) -> int:
        return 22

    @classmethod
    def is_available(cls) -> bool:
        return availability_check()

    @classmethod
    def construct(cls, session: Client, config: ConfigRegistry) -> AbstractTunnel:
        return cls(session, config['CAS_USERNAME'], config['CAS_PASSWORD'])
