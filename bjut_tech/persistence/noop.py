from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import AbstractPersistenceProvider

if TYPE_CHECKING:
    from .._config import ConfigRegistry


class NoopPersistenceProvider(AbstractPersistenceProvider):

    def load(self, name: str):
        pass

    def save(self, name: str, obj):
        pass

    def delete(self, name: str):
        pass

    @classmethod
    def construct(cls, config: ConfigRegistry) -> AbstractPersistenceProvider:
        return cls()
