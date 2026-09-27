from rest_framework.routers import DefaultRouter

from apps.catalog.views import MediaItemViewSet

app_name = "catalog"

router = DefaultRouter()
router.register("media", MediaItemViewSet, basename="media-item")

urlpatterns = router.urls
