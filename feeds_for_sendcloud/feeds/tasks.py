from datetime import datetime, timezone

from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from config.celery_app import app

from .exceptions import TaskException

logger = get_task_logger(__name__)


@app.task(name="process_posts")
def process_posts(feed_pk):
    Feed = apps.get_model("feeds", "Feed")
    feed = Feed.objects.get(pk=feed_pk)
    feed.process_source_posts()

    feed.last_refresh = datetime.now(timezone.utc)
    feed.save()

    return feed.status


@app.task(name="process_feeds_posts")
def update_feeds_posts():
    Feed = apps.get_model("feeds", "Feed")
    feeds = Feed.objects.next_execution_objects.all()
    for feed in feeds:
        feed.state = Feed.STATE_CHOICES.processing

    Feed.objects.bulk_update(feeds, ["state"])

    for feed in feeds:
        update_single_feed_posts.delay(feed.pk)


@app.task(autoretry_for=(TaskException,), retry_backoff=2, retry_kwargs={"max_retries": 3})
def update_single_feed_posts(feed_pk):
    Feed = apps.get_model("feeds", "Feed")
    try:
        feed = Feed.objects.get(pk=feed_pk)
    except ObjectDoesNotExist:
        logger.info(f"Feed({feed_pk}) was removed")
    else:
        feed.process_source_posts()
        if feed.has_failed():
            raise TaskException(f"Feed({feed.pk}) failed")
        logger.info(f"Feed({feed.pk}) updated")
