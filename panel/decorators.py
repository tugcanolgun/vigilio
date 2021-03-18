from functools import wraps
from typing import TypeVar, Callable, Any, Union

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.exceptions import PermissionDenied

from panel.api.utils import (
    is_qbittorrent_running,
    is_redis_online,
    is_celery_running,
)
from panel.handlers import is_demo, are_settings_filled
from panel.tasks.setup_panel import is_panel_ready

T = TypeVar("T", bound=Callable[..., Any])


def setup_required(func: T) -> T:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not is_panel_ready():
            return redirect(reverse("panel:setup_panel"))

        return func(*args, **kwargs)

    return wrapper


def is_background_running() -> bool:
    if not is_qbittorrent_running() or not is_redis_online() or not is_celery_running():
        return False

    return True


def check_background(func: T) -> T:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not is_background_running():
            next: str = "/"
            if args:
                next = args[0].path

            return redirect(f"{reverse('panel:background_processes')}?next={next}")

        return func(*args, **kwargs)

    return wrapper


def check_demo(func: T) -> T:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Union[T, PermissionDenied]:
        if is_demo():
            raise PermissionDenied("This is not allowed in DEMO mode.")

        return func(*args, **kwargs)

    return wrapper


def check_settings(func: T) -> T:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not are_settings_filled():
            next: str = "/"
            if args:
                next = args[0].path

            return redirect(f"{reverse('panel:initial_setup')}?next={next}")

        return func(*args, **kwargs)

    return wrapper
