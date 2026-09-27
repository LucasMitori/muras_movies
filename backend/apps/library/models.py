from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class LibraryStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    WATCHING = "watching", "Watching"
    COMPLETED = "completed", "Completed"
    DROPPED = "dropped", "Dropped"


class LibraryEntry(TimeStampedModel):
    """Current status of one media item in one user's personal library.

    Exactly one row per (user, media_item) — this is the "am I tracking
    this" state, separate from ConsumptionEvent's repeatable watch history.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="library_entries")
    media_item = models.ForeignKey("catalog.MediaItem", on_delete=models.CASCADE, related_name="library_entries")
    status = models.CharField(max_length=16, choices=LibraryStatus.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "media_item"], name="unique_library_entry_per_user_item"),
        ]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self):
        return f"{self.user_id}:{self.media_item_id} = {self.status}"


class ConsumptionEvent(TimeStampedModel):
    """One rewatch/watch occurrence, independent of the current LibraryEntry status."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumption_events")
    media_item = models.ForeignKey("catalog.MediaItem", on_delete=models.CASCADE, related_name="consumption_events")
    watched_on = models.DateField(null=True, blank=True, help_text="User-reported date; left blank if unknown.")
    is_rewatch = models.BooleanField(default=False)
    note = models.CharField(max_length=280, blank=True)

    class Meta:
        ordering = ["-watched_on", "-created_at"]
        indexes = [models.Index(fields=["user", "media_item"])]

    def __str__(self):
        return f"{self.user_id} watched {self.media_item_id} on {self.watched_on}"


class Rating(TimeStampedModel):
    """One current rating per (user, media_item). Half-star steps 0.5..5.0

    stored as integers 1..10 (value = stars * 2). No row means unrated —
    zero is never used to mean "no rating".
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    media_item = models.ForeignKey("catalog.MediaItem", on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "media_item"], name="unique_rating_per_user_item"),
        ]
        indexes = [models.Index(fields=["media_item"])]

    def __str__(self):
        return f"{self.user_id} rated {self.media_item_id}: {self.value}/10"


class Review(TimeStampedModel):
    """One editable review per (user, media_item)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    media_item = models.ForeignKey("catalog.MediaItem", on_delete=models.CASCADE, related_name="reviews")
    body = models.TextField(max_length=8000)
    contains_spoilers = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False, help_text="Set by moderation; content stays for audit trail.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "media_item"], name="unique_review_per_user_item"),
        ]
        indexes = [models.Index(fields=["media_item", "is_hidden"])]

    def __str__(self):
        return f"Review<{self.user_id}:{self.media_item_id}>"


class ReviewComment(TimeStampedModel):
    """Bounded reply tree: a comment's parent must belong to the same review

    and be a top-level comment (depth capped at 1 reply level), enforced in
    the serializer rather than the database.
    """

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    body = models.TextField(max_length=2000)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["review"])]

    def __str__(self):
        return f"Comment<{self.author_id} on review {self.review_id}>"
