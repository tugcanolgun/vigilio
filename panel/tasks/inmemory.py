import logging
import os
import sys
from typing import Any, Optional

import redis
from django.conf import settings


logger = logging.getLogger(__name__)


def get_redis_url() -> Optional[str]:
    if not hasattr(settings, "CELERY_RESULT_BACKEND"):
        logger.error(
            "CELERY_RESULT_BACKEND is not set. Settings may not work as intended."
        )
        return None

    return settings.CELERY_RESULT_BACKEND


def get_redis() -> Optional[redis.Redis]:
    if "pytest" in sys.modules:
        return None

    redis_url: Optional[str] = get_redis_url()

    try:
        r: redis.Redis = redis.from_url(redis_url)
        r.ping()
    except redis.exceptions.ConnectionError:
        logger.error("Redis is not available. Settings may not work as intended.")
        return None

    return r


def process_result(key: str, result: bytes) -> Any:
    try:
        if key in {"DELETE_ORIGINAL_FILES", "DEMO"}:
            return result in {"true", "True", "1"}
        else:
            return result.decode("utf-8")
    except Exception:
        logger.exception(f"Could not process redis result {key} {result}")
        return result


def get_redis_key(key: str) -> Any:
    r: Optional[redis.Redis] = get_redis()

    if r:
        return r.get(key)


def del_redis_key(key: str) -> Any:
    r: Optional[redis.Redis] = get_redis()

    if r:
        return r.delete(key)


def get_setting(key: str, suppress_errors: bool = False) -> Any:
    result: Optional[bytes] = get_redis_key(key)
    if result:
        return process_result(key, result)

    if hasattr(settings, key):
        return getattr(settings, key)

    if not suppress_errors:
        raise Exception(f"{key} could not be found or empty.")


def set_redis(key: str, value: Any) -> None:
    r: Optional[redis.Redis] = get_redis()

    if r:
        r.set(key, value)


def get_setting_or_environment(key: str) -> Any:
    setting: Any = get_setting(key, suppress_errors=True)
    if setting:
        return setting

    return os.environ.get(key)
