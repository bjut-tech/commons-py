from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import oss2
except ImportError:
    oss2 = None

from ._base import AbstractPersistenceProvider

if TYPE_CHECKING:
    from .._config import ConfigRegistry


class OssPersistenceProvider(AbstractPersistenceProvider):

    def __init__(self, auth: oss2.Auth, endpoint: str, bucket: str, prefix: str = ''):
        self.bucket = oss2.Bucket(auth, endpoint, bucket)
        self.prefix = prefix

    def get_object_name(self, name: str) -> str:
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
        if oss2 is None:
            raise ImportError('Unable to use `oss` persistence since `oss2` is not installed. Please install it first.')

        auth = oss2.Auth(
            config['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            config['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
        )

        endpoint = 'https://oss-cn-beijing-internal.aliyuncs.com' \
            if config.get('ALIBABA_CLOUD_INTERNAL', False) else \
            'https://oss-cn-beijing.aliyuncs.com'

        return cls(auth, endpoint, 'bjut-tech')
