from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import dill

if TYPE_CHECKING:
    from .._config import ConfigRegistry


class AbstractPersistenceProvider:

    def load(self, name: str):
        raise NotImplementedError

    def save(self, name: str, obj):
        raise NotImplementedError

    def delete(self, name: str):
        raise NotImplementedError

    @classmethod
    def construct(cls, config: ConfigRegistry) -> AbstractPersistenceProvider:
        raise NotImplementedError

    @staticmethod
    def _serialize(obj) -> bytes:
        return dill.dumps(obj)

    @staticmethod
    def _deserialize(data: bytes):
        try:
            return dill.loads(data)
        except Exception as e:
            print('Error while deserializing:', e, file=sys.stderr)
            return None
