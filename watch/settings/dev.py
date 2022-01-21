import os

from watch.settings.base import *

DEBUG = True

INTERNAL_IPS = type(str("c"), (), {"__contains__": lambda *a: True})()


CSRF_TRUSTED_ORIGINS.extend([f"http://{domain}:8000" for domain in os.environ.get("ALLOWED_URLS", "").split(",")])

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
