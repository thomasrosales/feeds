import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from feeds_for_sendcloud.feeds.api.serializers import PostSerializer
from feeds_for_sendcloud.feeds.models import Post

pytestmark = pytest.mark.django_db
route_basename = "api:posts"


def test_create(user, superuser, client, super_client):
    data = {
        "fake": "super_fake",
    }

    # authenticated user but not superuser

    response = client.post(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # anonymous user

    anonymous_client = APIClient()
    response = anonymous_client.post(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # authenticated superuser

    response = super_client.post(reverse(f"{route_basename}-list"), data, format="json")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_update(user, superuser, client, super_client):
    data = {
        "fake": "super_fake",
    }

    # authenticated user but not superuser

    response = client.put(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # anonymous user

    anonymous_client = APIClient()
    response = anonymous_client.put(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # authenticated superuser

    response = super_client.put(reverse(f"{route_basename}-list"), data, format="json")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_update_partial(user, superuser, client, super_client):
    data = {
        "fake": "super_fake",
    }

    # authenticated user but not superuser

    response = client.patch(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # anonymous user

    anonymous_client = APIClient()
    response = anonymous_client.patch(reverse(f"{route_basename}-list"), data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # authenticated superuser

    response = super_client.patch(reverse(f"{route_basename}-list"), data, format="json")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_list(user, client, feed_with_posts):
    feed1 = feed_with_posts()
    _ = feed_with_posts()

    feed1.follow(user)  # following this feed

    response = client.get(reverse(f"{route_basename}-list"), format="json")

    expected = PostSerializer(Post.objects.filter(feed=feed1.pk).order_by("id"), many=True).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


def test_retrieve(user, client, feed_with_posts):
    feed1 = feed_with_posts()
    feed2 = feed_with_posts()

    feed1.follow(user)  # following this feed

    post_from_followed_feed = feed1.posts.last()

    response = client.get(reverse(f"{route_basename}-detail", args=[post_from_followed_feed.pk]), format="json")

    expected = PostSerializer(Post.objects.get(pk=post_from_followed_feed.pk)).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected

    # Get post from unfollowed Feed

    post_from_unfollowed_feed = feed2.posts.last()

    response = client.get(reverse(f"{route_basename}-detail", args=[post_from_unfollowed_feed.pk]), format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_filters(user, client, feed_with_posts):
    feed1 = feed_with_posts()
    feed2 = feed_with_posts()

    feed1.follow(user)
    feed2.follow(user)

    read_posts = Post.objects.filter(feed_id=feed1.pk).order_by("id")[:5]
    for post in read_posts:
        post.read(user)

    # Filter read

    response = client.get(f"{reverse(f'{route_basename}-list')}?read=true", format="json")

    expected = PostSerializer(read_posts, many=True).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected

    # Filter unread

    response = client.get(f"{reverse(f'{route_basename}-list')}?read=false", format="json")

    expected = PostSerializer(
        Post.objects.filter(feed__in=[feed1.pk, feed2.pk]).exclude(id__in=[p.id for p in read_posts]).order_by("id"),
        many=True,
    ).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected
