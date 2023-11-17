from rest_framework import serializers

from ..models import Feed, Post


class FeedSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = (
            "id",
            "source",
            "last_refresh",
            "state",
            "source_err",
            "following",
        )
        read_only_fields = ("last_refresh", "state", "source_err", "following")

    def get_following(self, obj: Feed):
        user = self.context["request"].user
        return obj.is_followed_by(user)


class PostSerializer(serializers.ModelSerializer):
    feed = serializers.SlugRelatedField(many=False, read_only=True, slug_field="source")

    class Meta:
        model = Post
        fields = (
            "id",
            "feed",
            "title",
            "description",
            "link",
        )
        read_only_fields = fields
