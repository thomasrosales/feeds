from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from celery.exceptions import Retry

from feeds_for_sendcloud.feeds.models import Feed
from feeds_for_sendcloud.feeds.tasks import process_feeds_posts, process_posts, update_single_feed_posts
from tests.factories.feeds import FeedFactory

pytestmark = pytest.mark.django_db


@patch.object(Feed, "process_source_posts")
def test_process_posts(mock_process_source_posts, feed):
    process_posts(feed.pk)
    mock_process_source_posts.assert_called_once()


@patch("feeds_for_sendcloud.feeds.tasks.update_single_feed_posts")
def test_process_feeds_posts(mock_update_single_feed_posts, caplog):
    date_last_refresh = datetime.now(timezone.utc) - timedelta(minutes=6)
    feeds = FeedFactory.create_batch(size=5, state="updated", last_refresh=date_last_refresh)

    process_feeds_posts()

    assert mock_update_single_feed_posts.delay.call_count == len(feeds)
    assert caplog.messages[0] == "Feeds to be processing: 5"


@patch("feeds_for_sendcloud.feeds.tasks.update_single_feed_posts")
def test_process_feeds_posts_up_to_date(mock_update_single_feed_posts):
    date_last_refresh = datetime.now(timezone.utc) - timedelta(minutes=2)
    _ = FeedFactory.create_batch(size=5, state="updated", last_refresh=date_last_refresh)

    process_feeds_posts()

    mock_update_single_feed_posts.delay.assert_not_called()


def test_update_single_feed_posts_success(feed, caplog):
    feed.state = "updated"
    feed.save()

    with patch.object(Feed, "process_source_posts"):
        update_single_feed_posts(feed.pk)

    assert caplog.messages[0] == f"Feed({feed.pk}) updated"


@patch("feeds_for_sendcloud.feeds.tasks.update_single_feed_posts.retry")
def test_update_single_feed_posts_retry(mock_update_single_feed_posts_retry, feed):
    feed.state = "invalid"
    feed.save()

    mock_update_single_feed_posts_retry.side_effect = Retry()

    with pytest.raises(Retry):
        update_single_feed_posts(feed.pk)


def test_update_single_feed_posts_object_does_not_exists(caplog):
    update_single_feed_posts(999)
    assert caplog.messages[0] == "Feed(999) was removed"
