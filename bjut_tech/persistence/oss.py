from __future__ import annotations

from typing import TYPE_CHECKING

import oss2

from ._base import AbstractPersistenceProvider

if TYPE_CHECKING:
    from .._config import ConfigRegistry


class OssPersistenceProvider(AbstractPersistenceProvider):

    def __init__(self, auth: oss2.Auth, endpoint: str, bucket: str, prefix: str = ''):
        self.bucket = oss2.Bucket(auth, endpoint, bucket)
        self.prefix = prefix

    def get_object_name(self, name: str) -> str:
        if self.prefix[-1] != '/':
            self.prefix += '/'
        name = self.prefix + name
        if name[-4:] != '.bin':
            name += '.bin'
        return name

    def load(self, name: str):
        object_name = self.get_object_name(name)
        if self.bucket.object_exists(object_name):
            return self._deserialize(self.bucket.get_object(object_name).read())
        else:
            return None

    def save(self, name: str, obj):
        object_name = self.get_object_name(name)
        self.bucket.put_object(object_name, self._serialize(obj))

    def delete(self, name: str):
        object_name = self.get_object_name(name)
        if self.bucket.object_exists(object_name):
            self.bucket.delete_object(object_name)

    @classmethod
    def construct(cls, config: ConfigRegistry) -> AbstractPersistenceProvider:
        auth = oss2.Auth(
            config['ALIBABA_CLOUD_ACCESS_ID'],
            config['ALIBABA_CLOUD_ACCESS_SECRET']
        )

        endpoint = 'https://oss-cn-beijing-internal.aliyuncs.com' \
            if config.get('ALIBABA_CLOUD_INTERNAL', False) else \
            'https://oss-cn-beijing.aliyuncs.com'

        return cls(auth, endpoint, 'bjut-tech')
