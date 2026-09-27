from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from rest_framework import permissions, viewsets

from apps.catalog.filters import MediaItemFilter
from apps.catalog.models import MediaItem
from apps.catalog.serializers import MediaItemDetailSerializer, MediaItemListSerializer


class MediaItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only catalog. Writes only happen via admin/import tooling."""

    queryset = MediaItem.objects.filter(is_active=True).prefetch_related("genres").select_related(
        "movie_details", "series_details"
    )
    permission_classes = [permissions.AllowAny]
    filterset_class = MediaItemFilter
    # Lookup by numeric PK (default). The frontend route is /movies/[id]-[slug]
    # so IDs stay stable across slug/title edits; the slug is cosmetic only.

    def get_serializer_class(self):
        if self.action == "list":
            return MediaItemListSerializer
        return MediaItemDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            vector = SearchVector("title", weight="A") + SearchVector("original_title", weight="B")
            query = SearchQuery(search, search_type="websearch")
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by("-rank")
        else:
            qs = qs.order_by("-muratori_rating_count", "title")
        return qs
