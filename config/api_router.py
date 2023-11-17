from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from feeds_for_sendcloud.feeds.api.views import FeedViewSet, PostViewSet
from feeds_for_sendcloud.users.api.views import UserViewSet

router = DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register("feeds", FeedViewSet, basename="feeds")
router.register("posts", PostViewSet, basename="posts")

app_name = "api"
urlpatterns = router.urls
