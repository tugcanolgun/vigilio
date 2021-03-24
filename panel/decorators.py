from functools import wraps
from typing import TypeVar, Callable, Any, Union
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from lazysignup.decorators import _allow_lazy_user
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from panel.api.utils import (
    is_qbittorrent_running,
    is_redis_online,
    is_celery_running,
)
from panel.handlers import is_demo, are_settings_filled
from panel.tasks.demo_tasks import delete_demo_users
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


def _login_required(view_func: T, request: HttpRequest, *args, **kwargs) -> T:
    if request.user.is_authenticated:
        return view_func(request, *args, **kwargs)
    path = request.build_absolute_uri()
    resolved_login_url = resolve_url(settings.LOGIN_URL)
    # If the login url is the same scheme and net location then just
    # use the path as the "next" url.
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if (not login_scheme or login_scheme == current_scheme) and (
        not login_netloc or login_netloc == current_netloc
    ):
        path = request.get_full_path()
    from django.contrib.auth.views import redirect_to_login

    return redirect_to_login(path, resolved_login_url, "next")


def demo_or_login_required(func: T) -> T:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if is_demo():
            _allow_lazy_user(*args, **kwargs)
            delete_demo_users.delay()
            return func(*args, **kwargs)

        return _login_required(func, *args, **kwargs)

    return wrapper


class DemoOrIsAuthenticated(BasePermission):
    """
    Allows access to everyone if demo mode.
    Allows access only to authenticated users if not demo mode.
    """

    def has_permission(self, request, view):
        if is_demo():
            return True

        return bool(request.user and request.user.is_authenticated)
