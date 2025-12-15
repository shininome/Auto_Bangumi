import logging

from models.config import Downloader as DownloaderConfig
from conf.config import get_config_by_key

from .download_client import DownloadClient
from .download_queue import DownloadQueue, download_queue

logger = logging.getLogger(__name__)

_client: DownloadClient | None = None


def get_client() -> DownloadClient:
    """获取下载客户端，如果未初始化则返回默认客户端"""
    if _client is None:
        return DownloadClient(DownloaderConfig())
    return _client


def init(config: DownloaderConfig | None = None) -> bool:
    if config is None:
        config = get_config_by_key("downloader", DownloaderConfig)
    global _client
    try:
        _client = DownloadClient(config)
    except Exception as e:
        logger.error(f"Failed to initialize DownloadClient: {e}")
        return False
    return True


__all__ = [
    "DownloadClient",
    "DownloadQueue",
    "get_client",
    "download_queue",
]
