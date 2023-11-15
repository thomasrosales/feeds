from datetime import datetime, timezone

from django.db import models
from django.db.models import ExpressionWrapper, DateTimeField, F
from django.db.models.functions import ExtractMinute


class FeedsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("-created")


class FeedsNextExecutionManager(models.Manager):
    def get_queryset(self):
        date_now = datetime.now(timezone.utc)
        return (
            super()
            .get_queryset()
            .filter(status="updated")
            .annotate(
                next_execution=ExpressionWrapper(
                    date_now - F("last_refresh"), output_field=DateTimeField()
                )
            )
            .annotate(next_execution_minutes=ExtractMinute("next_execution"))
            .filter(next_execution_minutes__gte=5)
        )


class PostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("-created")
