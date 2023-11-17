from datetime import datetime, timezone

import requests
from django.db import models
from django_lifecycle import AFTER_SAVE, LifecycleModel, hook
from model_utils import Choices
from model_utils.models import TimeStampedModel
from rest_framework import status

from feeds_for_sendcloud.users.models import User
from feeds_for_sendcloud.utils.rss import parse_rss_to_dict, xml_is_present

from .managers import FeedsManager, FeedsNextExecutionManager, PostsManager
from .tasks import process_posts


class Feed(LifecycleModel, TimeStampedModel):
    VALID_SOURCES = ("application/rss+xml; charset=utf-8", "text/xml", "text/xml; charset=utf-8")
    STATE_CHOICES = Choices("initial", "processing", "updated", "failed", "invalid")
    source = models.URLField(max_length=500, unique=True, db_index=True)
    last_refresh = models.DateTimeField(default=None, null=True)
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="initial",
    )
    source_err = models.JSONField(default=dict, blank=True)

    # Relationships

    followers = models.ManyToManyField(User, related_name="feeds", blank=True)

    # Managers

    objects = FeedsManager()
    next_execution_objects = FeedsNextExecutionManager()

    # Hooks

    @hook(AFTER_SAVE, when="state", is_now="initial", on_commit=True)
    def init_process_posts(self):
        process_posts.delay(self.pk)

    # Business Logic

    def process_source_posts(self, force=False):
        if self.is_invalid and not force:
            return
        response = requests.get(self.source)
        if response.status_code != status.HTTP_200_OK:
            self.state = self.STATE_CHOICES.failed
            self.source_err = {"status_code": response.status_code, "error": response.text}
        elif response.headers["content-type"] not in self.VALID_SOURCES or not xml_is_present(
            response.headers["content-type"]
        ):
            self.state = self.STATE_CHOICES.invalid
        else:
            self._process_rss_content_and_create_posts(response.text)
            self.state = self.STATE_CHOICES.updated
            self.last_refresh = datetime.now(timezone.utc)
        self.save()

    def _process_rss_content_and_create_posts(self, rss_content):
        rss = parse_rss_to_dict(rss_content)
        new_posts = []
        for entry in rss.entries:
            if not self.posts.filter(link=entry.link).exists():
                post = Post(title=entry.title, description=entry.get("description", ""), link=entry.link, feed=self)
                new_posts.append(post)
        Post.objects.bulk_create(new_posts)

    def follow(self, user: User):
        self.followers.add(user)

    def unfollow(self, user: User):
        self.followers.remove(user)

    def is_followed_by(self, user: User):
        return self.followers.filter(pk=user.pk).exists()

    @property
    def has_failed(self):
        return self.state in [self.STATE_CHOICES.invalid, self.STATE_CHOICES.failed]

    @property
    def is_invalid(self):
        return self.state == self.STATE_CHOICES.invalid

    def __str__(self):
        return f"Feed({self.pk}) for {self.source}"


class Post(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=200)

    # Relationships

    feed = models.ForeignKey(Feed, related_name="posts", on_delete=models.CASCADE)
    users = models.ManyToManyField(
        User,
        related_name="read_posts",
    )

    class Meta:
        unique_together = ("link", "feed")
        indexes = [
            models.Index(fields=("link", "title")),
        ]

    # Managers

    objects = PostsManager()

    def read(self, user: User):
        if user.is_following_feed(self.feed.pk):
            self.users.add(user)

    def unread(self, user: User):
        # if a user decided to stop following a feed
        # all read posts will be associated to him, but he cannot perform any operation
        if user.is_following_feed(self.feed.pk):
            self.users.remove(user)

    def __str__(self):
        return f"Post({self.pk}) object with title {self.title}"
