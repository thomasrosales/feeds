from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from config.celery_app import app

from .exceptions import TaskException
from ..utils.task_retries import get_next_retry_countdown

logger = get_task_logger(__name__)


@app.task(name="process_posts")
def process_posts(feed_pk):
    Feed = apps.get_model("feeds", "Feed")
    feed = Feed.objects.get(pk=feed_pk)

    feed.process_source_posts()

    return feed.state


@app.task(name="process_feeds_posts", ignore_result=True)
def process_feeds_posts():
    Feed = apps.get_model("feeds", "Feed")
    feeds = Feed.next_execution_objects.all()
    for feed in feeds:
        feed.state = Feed.STATE_CHOICES.processing

    Feed.objects.bulk_update(feeds, ["state"])

    logger.info(f"Feeds to be processing: {feeds.count()}")

    for feed in feeds:
        update_single_feed_posts.delay(feed.pk)


# https://docs.celeryq.dev/en/latest/userguide/tasks.html#Task.retry_backoff
@app.task(bind=True, ignore_result=True)
def update_single_feed_posts(self, feed_pk):
    Feed = apps.get_model("feeds", "Feed")
    try:
        feed = Feed.objects.get(pk=feed_pk)
    except ObjectDoesNotExist:
        logger.info(f"Feed({feed_pk}) was removed")
    else:
        feed.process_source_posts()
        if feed.has_failed:
            raise self.retry(
                exc=TaskException(f"Feed({feed.pk}) - {feed.state}"),
                max_retries=3,
                countdown=get_next_retry_countdown(str(self.request.retries + 1)),
            )
        logger.info(f"Feed({feed.pk}) updated")
