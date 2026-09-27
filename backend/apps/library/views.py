from rest_framework import permissions, viewsets

from apps.common.permissions import IsOwner
from apps.library.models import ConsumptionEvent, LibraryEntry, Rating, Review, ReviewComment
from apps.library.serializers import (
    ConsumptionEventSerializer,
    LibraryEntrySerializer,
    RatingSerializer,
    ReviewCommentSerializer,
    ReviewSerializer,
)


class OwnedResourceMixin:
    """List/detail queryset is always scoped to the caller — never trust a

    client-supplied user id in query params to see someone else's private
    library/rating/consumption data.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ["media_item"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class LibraryEntryViewSet(OwnedResourceMixin, viewsets.ModelViewSet):
    queryset = LibraryEntry.objects.select_related("media_item").prefetch_related("media_item__genres")
    serializer_class = LibraryEntrySerializer
    filterset_fields = ["media_item", "status"]


class RatingViewSet(OwnedResourceMixin, viewsets.ModelViewSet):
    queryset = Rating.objects.select_related("media_item")
    serializer_class = RatingSerializer


class ConsumptionEventViewSet(OwnedResourceMixin, viewsets.ModelViewSet):
    queryset = ConsumptionEvent.objects.select_related("media_item")
    serializer_class = ConsumptionEventSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Reviews are public content: anyone can read; only the author can edit/delete."""

    queryset = Review.objects.filter(is_hidden=False).select_related("user", "media_item")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner]
    filterset_fields = ["media_item", "user"]


class IsCommentAuthor(IsOwner):
    owner_field = "author"


class ReviewCommentViewSet(viewsets.ModelViewSet):
    """Bounded discussion under a review — public read, author-only write."""

    queryset = ReviewComment.objects.filter(is_hidden=False).select_related("author", "review")
    serializer_class = ReviewCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentAuthor]
    filterset_fields = ["review"]
