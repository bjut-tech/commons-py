from __future__ import annotations

import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

from ..utils import random_ipv6

if TYPE_CHECKING:
    from ..tunnel import AbstractTunnel


class CasAuthentication:

    def __init__(
        self,
        tunnel: AbstractTunnel,
        username: str,
        password: str
    ):
        self.tunnel = tunnel
        self.base_url = 'https://cas.bjut.edu.cn'

        self.username = username
        self.password = password

        if not self.username or not self.password:
            raise ValueError('username and password are required')

    def validate_user(self) -> str:
        session = self.tunnel.get_session()
        url = self.tunnel.transform_url(f'{self.base_url}/v1/users')

        response = session.post(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'X-Forwarded-For': random_ipv6()
        }, data={
            'username': self.username,
            'password': self.password
        })

        if response.status_code == HTTPStatus.OK:
            return response.json()['authentication']['principal']['id']
        elif response.status_code == HTTPStatus.UNAUTHORIZED:
            raise ValueError('username or password is incorrect')
        elif response.status_code == HTTPStatus.LOCKED:
            raise RuntimeError('account is locked')
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RuntimeError('too many requests')
        else:
            response.raise_for_status()
            raise RuntimeError('unknown error')

    def authenticate(self, service_url: str):
        session = self.tunnel.get_session()
        url = self.tunnel.transform_url(f'{self.base_url}/v1/tickets')

        response = session.post(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'X-Forwarded-For': random_ipv6()
        }, data={
            'username': self.username,
            'password': self.password
        }, follow_redirects=False)

        if response.status_code != 201:
            print(response.status_code, response.text, file=sys.stderr)
            raise ValueError('CAS auth failed')

        ticket = response.headers['Location'].split('/')[-1]
        session.cookies.set(
            **self.tunnel.transform_cookie(name='CASTGC', value=ticket, domain='.bjut.edu.cn')
        )

        url = self.tunnel.transform_url(f'{self.base_url}/login')
        session.get(url, params={
            'service': service_url
        }, headers={
            'User-Agent': 'Mozilla/5.0',
            'X-Forwarded-For': random_ipv6()
        }, follow_redirects=True)
