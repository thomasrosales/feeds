from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ..models import Feed, Post
from .filters import PostReadOrNotFilterBackend
from .serializers import FeedSerializer, PostSerializer


class FeedViewSet(ModelViewSet):
    serializer_class = FeedSerializer
    queryset = Feed.objects.prefetch_related("followers", "posts").all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ("following_me", "unfollowing_me", "force_update"):
            return [IsAuthenticated()]
        if self.action not in ("list", "retrieve"):
            # FIXME: consider adding force_update to the IsAdminUser permission
            permission_classes += [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["POST"], url_path="following-me")
    def following_me(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        instance.follow(user)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"], url_path="unfollowing-me")
    def unfollowing_me(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        instance.unfollow(user)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"], url_path="force-update")
    def force_update(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        if not instance.is_followed_by(user):
            return Response(
                {"error": "You must follow the feed before force refresh"}, status=status.HTTP_400_BAD_REQUEST
            )
        instance.process_source_posts(force=True)
        return Response({"state": instance.state}, status=status.HTTP_200_OK)


class PostViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.select_related("feed").all()
    filter_backends = [DjangoFilterBackend, PostReadOrNotFilterBackend, OrderingFilter]
    ordering_fields = ["feed__last_refresh"]
    filterset_fields = ["feed"]
    ordering = ["id"]

    @extend_schema(
        parameters=[
            OpenApiParameter("read", OpenApiTypes.BOOL, OpenApiParameter.QUERY),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        feeds = Feed.objects.filter(followers=user).values_list("pk")
        return super().get_queryset().filter(feed__in=feeds)

    @action(detail=True, methods=["POST"], url_path="read")
    def read(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        instance.read(user)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"], url_path="unread")
    def unread(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        instance.unread(user)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
