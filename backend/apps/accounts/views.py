from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.accounts import visibility
from apps.accounts.models import Block, Follow, User
from apps.accounts.serializers import (
    LoginSerializer,
    ProfileSerializer,
    PublicUserSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.library.models import ConsumptionEvent, LibraryEntry
from apps.library.serializers import LibraryEntrySerializer, PublicConsumptionEventSerializer


class AuthRateThrottle(AnonRateThrottle):
    scope = "auth"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """GET this once before login/register so the browser has a CSRF cookie."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "Account is disabled."}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class PublicUserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Other people's profiles, their social graph, and their library/diary.

    Readable anonymously, because public profile pages are meant to be
    server-rendered and indexable, while every mutation requires a session.
    """

    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"
    # Django usernames allow ., @, + and -, which the router's default lookup
    # regex would cut the URL short on. Match anything up to the next slash.
    lookup_value_regex = "[^/]+"

    def get_queryset(self):
        qs = (
            User.objects.filter(is_active=True)
            .select_related("profile")
            .annotate(
                followers_count=Count("followers", distinct=True),
                following_count=Count("following", distinct=True),
                ratings_count=Count("ratings", distinct=True),
                # A hidden review is shown nowhere, so it must not be counted
                # either, or the number contradicts the visible review list.
                reviews_count=Count("reviews", filter=Q(reviews__is_hidden=False), distinct=True),
            )
            .order_by("username")
        )

        # Blocking is mutual invisibility: a blocked user is absent from
        # listings and 404s on retrieve, rather than 403-ing and thereby
        # confirming that the account exists.
        hidden = visibility.blocked_user_ids(self.request.user)
        if hidden:
            qs = qs.exclude(pk__in=hidden)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(profile__display_name__icontains=search))
        return qs

    def _target_ignoring_blocks(self):
        """Look a user up without the block exclusion applied.

        Unblocking needs this: an already-blocked user is filtered out of
        get_queryset, so going through get_object() would 404 and leave the
        block impossible to undo.
        """
        return get_object_or_404(User.objects.filter(is_active=True), username=self.kwargs["username"])

    @action(detail=True, methods=["post", "delete"], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, username=None):
        target = self.get_object()
        if target.pk == request.user.pk:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            # get_or_create keeps a double-tap idempotent instead of raising
            # on the unique_follow constraint.
            Follow.objects.get_or_create(follower=request.user, followed=target)
            return Response(status=status.HTTP_201_CREATED)

        Follow.objects.filter(follower=request.user, followed=target).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], permission_classes=[permissions.IsAuthenticated])
    def block(self, request, username=None):
        target = self._target_ignoring_blocks()
        if target.pk == request.user.pk:
            return Response({"detail": "You cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            Block.objects.get_or_create(blocker=request.user, blocked=target)
            # Drop any follow in both directions. Leaving them would keep
            # feeding each user's activity to the other through a relationship
            # neither of them can now see or remove.
            Follow.objects.filter(
                Q(follower=request.user, followed=target) | Q(follower=target, followed=request.user)
            ).delete()
            return Response(status=status.HTTP_201_CREATED)

        Block.objects.filter(blocker=request.user, blocked=target).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _paginated_users(self, base_queryset):
        hidden = visibility.blocked_user_ids(self.request.user)
        qs = base_queryset.filter(is_active=True).select_related("profile").order_by("username")
        if hidden:
            qs = qs.exclude(pk__in=hidden)
        page = self.paginate_queryset(qs)
        serializer = PublicUserSerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def followers(self, request, username=None):
        target = self.get_object()
        return self._paginated_users(User.objects.filter(following__followed=target))

    @action(detail=True, methods=["get"])
    def following(self, request, username=None):
        target = self.get_object()
        return self._paginated_users(User.objects.filter(followers__follower=target))

    @action(detail=True, methods=["get"])
    def library(self, request, username=None):
        target = self.get_object()
        if not visibility.can_view(request.user, target, target.profile.library_visibility):
            raise PermissionDenied("This library is not visible to you.")

        entries = (
            LibraryEntry.objects.filter(user=target)
            .select_related("media_item")
            .prefetch_related("media_item__genres")
            .order_by("-updated_at")
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            entries = entries.filter(status=status_filter)

        page = self.paginate_queryset(entries)
        serializer = LibraryEntrySerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def diary(self, request, username=None):
        """Whether the diary is listed at all is governed by library_visibility;
        the watch dates are governed separately by diary_dates_visibility, so a
        user can share what they watched without revealing when.
        """
        target = self.get_object()
        if not visibility.can_view(request.user, target, target.profile.library_visibility):
            raise PermissionDenied("This diary is not visible to you.")

        show_dates = visibility.can_view(request.user, target, target.profile.diary_dates_visibility)
        events = (
            ConsumptionEvent.objects.filter(user=target)
            .select_related("media_item")
            .prefetch_related("media_item__genres")
        )
        page = self.paginate_queryset(events)
        context = {**self.get_serializer_context(), "show_dates": show_dates}
        serializer = PublicConsumptionEventSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)


class MyBlocksView(generics.ListAPIView):
    """The requester's own block list, so a block can be found and undone."""

    serializer_class = PublicUserSerializer

    def get_queryset(self):
        return (
            User.objects.filter(blocked_by__blocker=self.request.user)
            .select_related("profile")
            .order_by("username")
        )
