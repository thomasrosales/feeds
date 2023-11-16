from datetime import datetime, timezone

from django.db import models
from django.db.models import DurationField, ExpressionWrapper, F


class FeedsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("-created")


class FeedsNextExecutionManager(models.Manager):
    def get_queryset(self):
        date_now = datetime.now(timezone.utc)
        return (
            super()
            .get_queryset()
            .filter(state="updated")
            .annotate(time_difference=ExpressionWrapper(date_now - F("last_refresh"), output_field=DurationField()))
            .filter(time_difference__gte="5 minutes")  # this just works for postgres database
        )


class PostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("-created")
