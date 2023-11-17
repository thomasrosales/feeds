import pytest
from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient

from feeds_for_sendcloud.users.models import User
from tests.factories.feeds import FeedFactory, PostFactory
from tests.factories.users import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture()
def superuser() -> settings.AUTH_USER_MODEL:
    superuser = User.objects.filter(is_staff=True, is_superuser=True).first()
    if superuser is None:
        superuser = User.objects.create_superuser(
            "root",
            "root@sendcloud.com",
            "root",
        )
    return superuser


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def rss_xml() -> str:
    with open("tests/helpers/example.xml", "r") as file:
        read_content = file.read()
    return read_content


#
# API client
# ------------------------------------------------------------------------------


@pytest.fixture()
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def super_client(superuser):
    client = APIClient()
    client.force_authenticate(user=superuser)
    return client


#
# Models
# ------------------------------------------------------------------------------


@pytest.fixture()
def feed():
    return FeedFactory()


@pytest.fixture()
def posts():
    return PostFactory.create_batch(size=10)


@pytest.fixture()
def multiple_posts():
    def _make_post_records():
        return PostFactory.create_batch(size=10)

    return _make_post_records


@pytest.fixture
def feed_with_posts(multiple_posts):
    def _make_feed_record():
        return FeedFactory(posts=multiple_posts())

    return _make_feed_record
