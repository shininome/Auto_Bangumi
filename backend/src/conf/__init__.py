
from version import APP_VERSION

from .config import get_program_config
from .search_provider import SEARCH_CONFIG

__all__ = [
    "SEARCH_CONFIG",
    "get_program_config",
    "APP_VERSION",
]
