import factory
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from feeds_for_sendcloud.feeds.models import Feed, Post


class FeedFactory(DjangoModelFactory):
    source = factory.Sequence(lambda n: f"https://somesite.com/rss/{n}")

    class Meta:
        model = Feed

    @post_generation
    def posts(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for post in extracted:
                self.posts.add(post)


class PostFactory(DjangoModelFactory):
    title = Faker("sentence", nb_words=10)
    description = Faker("paragraph", nb_sentences=3)
    link = factory.Sequence(lambda n: f"https://somelink.com/news/{n}")

    class Meta:
        model = Post

    feed = factory.SubFactory(FeedFactory)
