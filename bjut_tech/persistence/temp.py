from __future__ import annotations

import os
from tempfile import gettempdir, gettempprefix
from typing import TYPE_CHECKING

from ._base import AbstractPersistenceProvider

if TYPE_CHECKING:
    from .._config import ConfigRegistry


class TemporaryFilePersistenceProvider(AbstractPersistenceProvider):

    def __init__(self):
        self.dir = os.path.join(gettempdir(), gettempprefix() + 'bjut-tech')

    def __repr__(self):
        return f'TemporaryFilePersistenceProvider(dir={self.dir})'

    def get_path(self, name: str):
        path = os.path.join(self.dir, name)
        if path[-4:] != '.bin':
            path += '.bin'
        return path

    def load(self, name: str):
        if not os.path.exists(self.get_path(name)):
            return None

        with open(self.get_path(name), 'rb') as f:
            return self._deserialize(f.read())

    def save(self, name: str, obj):
        path = self.get_path(name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as f:
            f.write(self._serialize(obj))

    def delete(self, name: str):
        path = self.get_path(name)
        if os.path.exists(path):
            os.remove(path)

    @classmethod
    def construct(cls, config: ConfigRegistry) -> AbstractPersistenceProvider:
        return cls()
