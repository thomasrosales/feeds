from django.contrib import admin

from .models import Feed, Post


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ["source", "state", "last_refresh"]
    search_fields = ["source", "state"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ["feed"]
    list_display = ["title", "feed_source", "link"]
    search_fields = ["title"]

    @admin.display(ordering="feed_source")
    def feed_source(self, obj):
        return obj.feed.source
