import os
from typing import Dict, Any

from environs import Env

_ENTRIES_STR = [
    'CAS_USERNAME',
    'CAS_PASSWORD',
    'JW_PASSWORD',
    'JW_BASE_URL',
    'ALIBABA_CLOUD_ACCESS_KEY_ID',
    'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
    'NOTIFY_EMAIL',
    'PERSISTENCE_TYPE'
]

_ENTRIES_INTEGER = [
    # nothing
]

_ENTRIES_BOOL = [
    'ALIBABA_CLOUD_INTERNAL',
    'NOTIFY_DRY_RUN'
]

_env = Env()
_env.read_env(os.path.join(os.getcwd(), '.env'))


class ConfigRegistry:
    _overrides: Dict[str, Any]

    def __init__(self):
        self._overrides = {}

    def __getitem__(self, key: str):
        return self.get(key)

    def get(self, key: str, default=None):
        if key in self._overrides:
            return self._overrides[key]
        elif key in _ENTRIES_STR:
            return _env.str(key, default=default)
        elif key in _ENTRIES_INTEGER:
            return _env.int(key, default=default)
        elif key in _ENTRIES_BOOL:
            return _env.bool(key, default=default)
        else:
            raise ValueError(f'Unknown config key: {key}')

    def set_overrides(self, overrides: Dict[str, Any]):
        self._overrides = overrides

    def clear_overrides(self):
        self._overrides = {}
