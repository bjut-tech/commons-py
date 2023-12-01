from http import HTTPStatus

import httpx

from ..utils import random_ipv6


class CasAuthentication:

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        if not self.username or not self.password:
            raise ValueError('username and password are required')

    def validate_user(self) -> str:
        response = httpx.post('https://cas.bjut.edu.cn/v1/users', headers={
            'User-Agent': 'Mozilla/5.0',
            'X-Forwarded-For': random_ipv6()
        }, data={
            'username': self.username,
            'password': self.password
        }, verify=False)

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
