import logging
import os
from typing import Optional

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def process_demo_setting() -> None:
    from panel.tasks.inmemory import get_redis_key, del_redis_key

    demo: bool = os.environ.get("DEMO", "false") in {
        "true",
        "True",
        "1",
    }

    redis_demo: Optional[bool] = get_redis_key("DEMO")
    if not redis_demo:
        logger.debug("DEMO is not stored in redis. No action is necessary.")
        return

    try:
        if bool(redis_demo) is demo:
            logger.debug(
                "redis and environment DEMO values match. No action is necessary."
            )
            return
    except Exception:
        pass

    logger.info("DEMO setting has been deleted from redis")
    del_redis_key("DEMO")


class PanelConfig(AppConfig):
    name = "panel"

    def ready(self):
        process_demo_setting()
