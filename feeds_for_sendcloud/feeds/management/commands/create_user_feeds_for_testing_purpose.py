import contextlib
from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from feeds_for_sendcloud.feeds.models import Feed


class Command(BaseCommand):
    def handle(self, *args, **options):
        with contextlib.suppress(Exception):
            User = get_user_model()

            user = User(username="root", password="root", email="root@sendcloud.com")
            user.is_superuser = True
            user.is_staff = True
            user.set_password("root")
            user.save()

            user_staff_1 = User(username="staff", password="staff", email="staff@sendcloud.com")
            user_staff_1.set_password("staff")
            user_staff_1.save()

            user_staff_2 = User(username="staff2", password="staff2", email="staff2@sendcloud.com")
            user_staff_2.set_password("staff2")
            user_staff_2.save()

        # Feeds
        with contextlib.suppress(Exception):
            date_last_refresh = datetime.now(timezone.utc) + timedelta(minutes=2)
            feeds = [
                Feed(source="https://www.clarin.com/rss/lo-ultimo/", state="updated", last_refresh=date_last_refresh),
                Feed(source="http://www.nu.nl/rss/Algemeen", state="updated", last_refresh=date_last_refresh),
                Feed(
                    source="https://feeds.feedburner.com/tweakers/mixed",
                    state="updated",
                    last_refresh=date_last_refresh,
                ),
            ]
            Feed.objects.bulk_create(feeds)
