from unittest.mock import patch

import pytest
import requests
from addict import Dict
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from feeds_for_sendcloud.feeds.api.serializers import FeedSerializer
from feeds_for_sendcloud.feeds.models import Feed
from tests.factories.feeds import FeedFactory

pytestmark = pytest.mark.django_db
route_basename = "api:feeds"


def test_create(user, superuser, client, super_client):
    data = {
        "source": "https://someurl.com/rss",
    }

    # authenticated user but not superuser

    response = client.post(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # anonymous user

    anonymous_client = APIClient()
    response = anonymous_client.post(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # authenticated superuser

    response = super_client.post(reverse(f"{route_basename}-list"), data, format="json")
    expected = FeedSerializer(Feed.objects.last(), context={"request": response.wsgi_request}).data

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == expected


def test_multiple_following_me(user, client):
    feeds = FeedFactory.create_batch(size=4)

    feed1 = feeds[0]
    response = client.post(reverse(f"{route_basename}-following-me", args=[feed1.id]), format="json")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert feed1.is_followed_by(user)
    assert feed1.followers.filter(pk=user.pk).exists()

    feed2 = feeds[3]
    response = client.post(reverse(f"{route_basename}-following-me", args=[feed2.id]), format="json")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert feed2.is_followed_by(user)
    assert feed2.followers.filter(pk=user.pk).exists()

    assert user.feeds.count() == 2
    assert [item[0] for item in user.feeds.order_by("pk").values_list("pk")] == [feed1.pk, feed2.pk]


def test_unfollowing_me(user, client, feed):
    feed.followers.add(user)

    response = client.post(reverse(f"{route_basename}-unfollowing-me", args=[feed.id]), format="json")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert feed.is_followed_by(user) is False
    assert not feed.followers.filter(pk=user.pk).exists()


def test_force_update(user, client, feed, rss_xml):

    response = client.post(reverse(f"{route_basename}-force-update", args=[feed.id]), format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "You must follow the feed before force refresh"

    feed.followers.add(user)

    with patch.object(requests, "get") as mock_requests_get:
        mock_requests_get.return_value = Dict(
            {"status_code": status.HTTP_200_OK, "text": rss_xml, "headers": {"content-type": "text/xml"}}
        )
        response = client.post(reverse(f"{route_basename}-force-update", args=[feed.id]), format="json")

    feed.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"state": feed.state}
    assert feed.posts.count() == 2
    assert feed.state == "updated"
    mock_requests_get.assert_called_once_with(feed.source)
