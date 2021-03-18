import pytest
from django.contrib.auth.models import User
from django.test import Client

from stream.tests.factories import UserFactory


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def user_client(client: Client, user: User) -> Client:
    client.force_login(user)

    return client
