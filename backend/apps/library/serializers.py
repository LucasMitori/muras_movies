from rest_framework import serializers

from apps.catalog.serializers import MediaItemListSerializer
from apps.library.models import ConsumptionEvent, LibraryEntry, Rating, Review, ReviewComment


class ReviewAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class LibraryEntrySerializer(serializers.ModelSerializer):
    # HiddenField + CurrentUserDefault: the client can never set another
    # user's id (no mass assignment), and it still participates in the
    # model's UniqueConstraint(user, media_item) validation.
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    media_item_detail = MediaItemListSerializer(source="media_item", read_only=True)

    class Meta:
        model = LibraryEntry
        fields = ["id", "user", "media_item", "media_item_detail", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    stars = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ["id", "user", "media_item", "value", "stars", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_stars(self, obj):
        return obj.value / 2


class ConsumptionEventSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ConsumptionEvent
        fields = ["id", "user", "media_item", "watched_on", "is_rewatch", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = ReviewAuthorSerializer(source="user", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "author", "media_item", "body", "contains_spoilers", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReviewCommentSerializer(serializers.ModelSerializer):
    author_user = serializers.HiddenField(source="author", default=serializers.CurrentUserDefault())
    author = ReviewAuthorSerializer(read_only=True)

    class Meta:
        model = ReviewComment
        fields = ["id", "review", "author_user", "author", "parent", "body", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_parent(self, parent):
        if parent is None:
            return parent
        if parent.parent_id is not None:
            raise serializers.ValidationError("Replies can only be one level deep.")
        return parent

    def validate(self, attrs):
        parent = attrs.get("parent")
        review = attrs.get("review") or getattr(self.instance, "review", None)
        if parent is not None and review is not None and parent.review_id != review.id:
            raise serializers.ValidationError({"parent": "Parent comment must belong to the same review."})
        return attrs
