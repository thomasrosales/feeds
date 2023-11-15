from datetime import datetime, timezone

import requests
from django.db import models, transaction
from django_lifecycle import LifecycleModel, hook, AFTER_SAVE
from model_utils import Choices
from model_utils.models import TimeStampedModel
from rest_framework import status

from feeds_for_sendcloud.feeds.managers import PostsManager, FeedsManager, FeedsNextExecutionManager
from feeds_for_sendcloud.users.models import User
from feeds_for_sendcloud.utils.rss import xml_to_dict

from .tasks import process_posts


class Feed(LifecycleModel, TimeStampedModel):
    STATE_CHOICES = Choices("initial", "processing", "updated", "failed", "invalid")
    source = models.URLField(max_length=500, unique=True, db_index=True)
    last_refresh = models.DateTimeField()
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="initial",
    )

    # Relationships

    followers = models.ManyToManyField(
        User,
        related_name="feeds",
    )

    # Managers

    objects = FeedsManager()
    next_execution_objects = FeedsNextExecutionManager()

    # Hooks

    @hook(AFTER_SAVE, when="status", is_now="initial")
    def init_process_posts(self):
        transaction.on_commit(
            lambda: process_posts.delay(self.pk)
        )

    # Business Logic

    def process_source_posts(self):
        response = requests.get(self.source)
        if response.status_code != status.HTTP_200_OK:
            self.state = self.STATE_CHOICES.failed
        else:
            self._process_rss_content(response.text)
            self.state = self.STATE_CHOICES.updated
            self.last_refresh = datetime.now(timezone.utc)
        self.save()

    def _process_rss_content(self, rss_content):
        rss = xml_to_dict(rss_content)
        new_posts = []
        for entry in rss.entries:
            if not self.posts.filter(link=entry.link).exists():
                post = Post(title=entry.title, description=entry.description, link=entry.link, feed=self)
                new_posts.append(post)
        Post.objects.bulk_create(new_posts)

    def follow(self, user: User):
        self.followers.add(user)

    def unfollow(self, user: User):
        self.followers.remove(user)

    def has_failed(self):
        return self.state in [self.STATE_CHOICES.invalid, self.STATE_CHOICES.failed]


class Post(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(max_length=200)

    # Relationships

    feed = models.ForeignKey(Feed, related_name="posts", on_delete=models.CASCADE)
    user_reads = models.ManyToManyField(
        User,
        through="ReadPostUser",
        through_fields=("post", "user"),
    )

    class Meta:
        unique_together = ("link", "post")
        indexes = [
            models.Index(fields=("link", "title")),
        ]

    # Managers

    objects = PostsManager()

    def read(self, user: User):
        self.user_reads.add(user)

    def unread(self, user: User):
        self.user_reads.remove(user)


class ReadPostUser(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
