import django_filters

from apps.catalog.models import MediaItem, MediaType


class MediaItemFilter(django_filters.FilterSet):
    media_type = django_filters.ChoiceFilter(choices=MediaType.choices)
    genre = django_filters.CharFilter(field_name="genres__slug")

    class Meta:
        model = MediaItem
        fields = ["media_type", "genre"]
