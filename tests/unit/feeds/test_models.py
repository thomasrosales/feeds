from unittest.mock import patch

import pytest
import requests
from addict import Dict
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_str_representation(feed):
    assert str(feed) == f"Feed({feed.pk}) for {feed.source}"


def test_follow(feed, user):
    feed.follow(user)

    assert feed.is_followed_by(user)
    assert user.is_following_feed(feed.id)


def test_unfollow(feed, user):
    feed.followers.add(user)
    feed.unfollow(user)

    assert not feed.is_followed_by(user)
    assert not user.is_following_feed(feed.id)


@patch.object(requests, "get")
def test_process_source_posts_success(mock_requests_get, feed, rss_xml):
    mock_requests_get.return_value = Dict(
        {"status_code": status.HTTP_200_OK, "text": rss_xml, "headers": {"content-type": "text/xml"}}
    )

    feed.process_source_posts()

    assert feed.posts.count() == 2
    assert all(title in feed.posts.values_list("title", flat=True) for title in ["RSS Tutorial", "XML Tutorial"])
    assert feed.state == "updated"
    mock_requests_get.assert_called_once_with(feed.source)


@patch.object(requests, "get")
def test_process_source_posts_success_duplicated_posts(mock_requests_get, feed, rss_xml):
    mock_requests_get.return_value = Dict(
        {"status_code": status.HTTP_200_OK, "text": rss_xml, "headers": {"content-type": "text/xml"}}
    )

    feed.process_source_posts()

    # Execute the process again

    feed.process_source_posts()

    assert feed.posts.count() == 2
    assert all(title in feed.posts.values_list("title", flat=True) for title in ["RSS Tutorial", "XML Tutorial"])
    assert feed.state == "updated"
    mock_requests_get.assert_called_with(feed.source)
    assert mock_requests_get.call_count == 2


@patch.object(requests, "get")
def test_process_source_posts_invalid_headers(mock_requests_get, feed):
    mock_requests_get.return_value = Dict(
        {"status_code": status.HTTP_200_OK, "text": "", "headers": {"content-type": "text/html"}}
    )

    feed.process_source_posts()

    assert feed.posts.count() == 0
    assert feed.state == "invalid"
    assert feed.has_failed
    assert feed.is_invalid
    mock_requests_get.assert_called_once_with(feed.source)


@patch.object(requests, "get")
def test_process_source_posts_xml_presents_in_header(mock_requests_get, feed):
    mock_requests_get.return_value = Dict(
        {"status_code": status.HTTP_200_OK, "text": "", "headers": {"content-type": "magic/xml"}}
    )

    feed.process_source_posts()

    assert feed.posts.count() == 0
    assert feed.state == "updated"
    assert not feed.has_failed
    assert not feed.is_invalid
    mock_requests_get.assert_called_once_with(feed.source)


@patch.object(requests, "get")
def test_process_source_posts_wrong_source(mock_requests_get, feed):
    mock_requests_get.return_value = Dict(
        {"status_code": status.HTTP_400_BAD_REQUEST, "text": {"error": "some error"}}
    )

    feed.process_source_posts()

    assert feed.posts.count() == 0
    assert feed.state == "failed"
    assert feed.source_err == {"status_code": 400, "error": {"error": "some error"}}
    assert feed.has_failed
    mock_requests_get.assert_called_once_with(feed.source)
