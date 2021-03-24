import datetime
from typing import Iterable

from django.utils.timezone import make_aware
from lazysignup.models import LazyUser

from watch.celery import app


@app.task
def delete_demo_users(expiration_second: int = 7200) -> None:
    delete_before: datetime.datetime = make_aware(
        datetime.datetime.utcnow()
    ) - datetime.timedelta(seconds=expiration_second)
    lazy_users: Iterable[LazyUser] = LazyUser.objects.filter(
        user__last_login__lt=delete_before
    ).prefetch_related("user")

    for lazy_user in lazy_users:
        lazy_user.user.delete()
