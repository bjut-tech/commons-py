from __future__ import annotations

import sys
import warnings
from typing import TYPE_CHECKING

from ._base import AbstractPersistenceProvider
from .noop import NoopPersistenceProvider
from .temp import TemporaryFilePersistenceProvider

try:
    from .oss import OssPersistenceProvider
except ImportError as e:
    print(e, file=sys.stderr)
    warnings.warn('OSS persistence not available due to import error')
    OssPersistenceProvider = AbstractPersistenceProvider

if TYPE_CHECKING:
    from .._config import ConfigRegistry


def get_persistence(config: ConfigRegistry) -> AbstractPersistenceProvider:
    cls_name = config.get('PERSISTENCE_TYPE', 'temp')

    if cls_name == 'oss':
        return OssPersistenceProvider.construct(config)
    elif cls_name == 'temp':
        return TemporaryFilePersistenceProvider.construct(config)
    elif cls_name == 'noop':
        return NoopPersistenceProvider.construct(config)
    else:
        raise ValueError(f'Unknown persistence type: {cls_name}')
