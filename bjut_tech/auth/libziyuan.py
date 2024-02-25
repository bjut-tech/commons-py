from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Optional
from xml.etree import ElementTree

import rsa

if TYPE_CHECKING:
    from httpx import Client
    from ..persistence import AbstractPersistenceProvider


class LibziyuanAuthentication:

    def __init__(self, persistence: AbstractPersistenceProvider, username: str, password: str):
        self.username = username
        self.password = password

        if not self.username or not self.password:
            raise ValueError('username and password are required')

        self.persistence = persistence
        self.persistence_key = f'temp/libziyuan_cookies_{self.username}'

    @staticmethod
    def check(session: Client) -> bool:
        response = session.get('https://libziyuan.bjut.edu.cn/por/conf.csp?apiversion=1')
        if response.status_code != 200:
            return False

        etree = ElementTree.parse(BytesIO(response.content))
        if etree.getroot().tag == 'Conf':
            return True

        return False

    def authenticate(self, session: Optional[Client] = None) -> Client:
        if session is None:
            session = self._new_session()

        if self.check(session):
            return session

        saved_cookies = self.persistence.load(self.persistence_key)
        if saved_cookies is not None:
            session.cookies.update(saved_cookies)
            if self.check(session):
                print('[libziyuan] authenticated session reused')
                return session
            self.persistence.delete(self.persistence_key)

        response = session.get('https://libziyuan.bjut.edu.cn/por/login_auth.csp', params={
            'apiversion': 1
        })
        response.raise_for_status()

        etree = ElementTree.parse(BytesIO(response.content))
        csrf_token = etree.find('CSRF_RAND_CODE').text
        rsa_key = etree.find('RSA_ENCRYPT_KEY').text
        rsa_exp = etree.find('RSA_ENCRYPT_EXP').text

        pub_key = rsa.PublicKey(int(rsa_key, 16), int(rsa_exp))
        clear_text = f'{self.password}_{csrf_token}'.encode('utf-8')
        password_encrypted = rsa.encrypt(clear_text, pub_key).hex()

        response = session.post('https://libziyuan.bjut.edu.cn/por/login_psw.csp', params={
            'anti_replay': 1,
            'encrypt': 1,
            'apiversion': 1
        }, data={
            'mitm_result': '',
            'svpn_req_randcode': csrf_token,
            'svpn_name': self.username,
            'svpn_password': password_encrypted,
            'svpn_rand_code': ''
        })
        response.raise_for_status()
        if 'success' not in response.text:
            raise RuntimeError('Login to webvpn failed')

        self.persistence.save(self.persistence_key, session.cookies.jar)

    @staticmethod
    def _new_session():
        return Client(headers={
            'User-Agent': 'Mozilla/5.0'
        }, verify=False)
