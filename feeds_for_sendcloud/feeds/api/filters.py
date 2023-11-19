from django_filters import Filter
from rest_framework.filters import BaseFilterBackend


class PostFilter(Filter):
    def filter(self, queryset, value):
        user = self.extra["request"].user
        return queryset.filter(users=user) if value else queryset.exclude(users=user)


class PostReadOrNotFilterBackend(BaseFilterBackend):
    filter_class = PostFilter
    READ_PARAM_MAP = {"true": True, "false": False}

    def filter_queryset(self, request, queryset, view):
        read_param = request.query_params.get("read")
        if read_param is None or read_param not in self.READ_PARAM_MAP.keys():
            return queryset
        read_param_mapped = self.READ_PARAM_MAP[read_param]
        return self.filter_class(field_name="read", request=request).filter(queryset, read_param_mapped)
