from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    MyBlocksView,
    PublicUserViewSet,
    RegisterView,
)

app_name = "accounts"

router = DefaultRouter()
router.register("users", PublicUserViewSet, basename="user")

urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="csrf"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("me/blocks/", MyBlocksView.as_view(), name="my-blocks"),
    path("", include(router.urls)),
]
