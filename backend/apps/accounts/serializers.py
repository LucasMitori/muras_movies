from django.contrib.auth import password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework import serializers

from apps.accounts import visibility
from apps.accounts.models import Block, Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "bio",
            "avatar",
            "library_visibility",
            "diary_dates_visibility",
            "show_on_public_leaderboards",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "profile"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        normalized = BaseUserManager.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is taken.")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class PublicProfileSerializer(serializers.ModelSerializer):
    """The parts of a Profile safe to show anyone.

    The visibility settings themselves are deliberately absent: they are the
    owner's configuration, not public information. PublicUserSerializer
    exposes the *outcome* (can_view_library) instead, which is what a client
    actually needs in order to render.
    """

    class Meta:
        model = Profile
        fields = ["display_name", "bio", "avatar"]
        read_only_fields = fields


class PublicUserSerializer(serializers.ModelSerializer):
    """Another user as seen by the requester, including their relationship.

    The *_count fields read annotations when the queryset provides them (see
    PublicUserViewSet.get_queryset) so a list of users costs one query rather
    than four per row.
    """

    profile = PublicProfileSerializer(read_only=True)

    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    is_self = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    has_blocked = serializers.SerializerMethodField()
    can_view_library = serializers.SerializerMethodField()
    can_view_diary_dates = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "date_joined",
            "profile",
            "followers_count",
            "following_count",
            "ratings_count",
            "reviews_count",
            "is_self",
            "is_following",
            "is_followed_by",
            "has_blocked",
            "can_view_library",
            "can_view_diary_dates",
        ]
        read_only_fields = fields

    @property
    def _viewer(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_is_self(self, obj):
        viewer = self._viewer
        return bool(viewer and viewer.is_authenticated and viewer.pk == obj.pk)

    def get_is_following(self, obj):
        return visibility.is_following(self._viewer, obj)

    def get_is_followed_by(self, obj):
        viewer = self._viewer
        if not (viewer and viewer.is_authenticated):
            return False
        return visibility.is_following(obj, viewer)

    def get_has_blocked(self, obj):
        viewer = self._viewer
        if not (viewer and viewer.is_authenticated):
            return False
        return Block.objects.filter(blocker=viewer, blocked=obj).exists()

    def get_can_view_library(self, obj):
        return visibility.can_view(self._viewer, obj, obj.profile.library_visibility)

    def get_can_view_diary_dates(self, obj):
        return visibility.can_view(self._viewer, obj, obj.profile.diary_dates_visibility)
