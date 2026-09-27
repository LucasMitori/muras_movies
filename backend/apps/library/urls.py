from rest_framework.routers import DefaultRouter

from apps.library.views import (
    ConsumptionEventViewSet,
    LibraryEntryViewSet,
    RatingViewSet,
    ReviewCommentViewSet,
    ReviewViewSet,
)

app_name = "library"

router = DefaultRouter()
router.register("entries", LibraryEntryViewSet, basename="library-entry")
router.register("ratings", RatingViewSet, basename="rating")
router.register("consumption-events", ConsumptionEventViewSet, basename="consumption-event")
router.register("reviews", ReviewViewSet, basename="review")
router.register("review-comments", ReviewCommentViewSet, basename="review-comment")

urlpatterns = router.urls
