from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint
from django.db.models.functions import Lower

from apps.common.models import TimeStampedModel


class User(AbstractUser):
    """Custom user identity, defined before the first migration per the spec.

    Email is required and unique; username stays as the login handle so
    URLs like /users/<handle> stay stable even if a user changes email.
    """

    email = models.EmailField(unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(Lower("email"), name="user_email_ci_unique"),
        ]

    def __str__(self):
        return self.username


class ProfileVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    FOLLOWERS = "followers", "Followers only"
    PRIVATE = "private", "Private"


class Profile(TimeStampedModel):
    """One-to-one extension of User for display/privacy preferences."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    library_visibility = models.CharField(
        max_length=16, choices=ProfileVisibility.choices, default=ProfileVisibility.PUBLIC
    )
    diary_dates_visibility = models.CharField(
        max_length=16, choices=ProfileVisibility.choices, default=ProfileVisibility.FOLLOWERS
    )
    show_on_public_leaderboards = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name or self.user.username


class Follow(TimeStampedModel):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["follower", "followed"], name="unique_follow"),
            CheckConstraint(condition=~Q(follower=F("followed")), name="no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower_id} -> {self.followed_id}"


class Block(TimeStampedModel):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["blocker", "blocked"], name="unique_block"),
            CheckConstraint(condition=~Q(blocker=F("blocked")), name="no_self_block"),
        ]

    def __str__(self):
        return f"{self.blocker_id} blocks {self.blocked_id}"
