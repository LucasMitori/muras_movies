"""Who may see which part of another user's profile.

Kept in one module so the rule lives in exactly one place: every endpoint
that exposes another user's data asks the same question here, rather than
each view re-deriving the policy and drifting from the others.

Note there is deliberately no staff bypass. Moderators work through Django
admin, so granting `is_staff` a read-through here would widen the privacy
promise made to users without any endpoint actually needing it.
"""

from django.db.models import Q

from apps.accounts.models import Block, Follow, ProfileVisibility


def blocked_user_ids(user):
    """Ids of users `user` has blocked *or* who have blocked `user`.

    Blocking is symmetric for visibility: neither side sees the other, no
    matter who initiated it.
    """
    if not (user and user.is_authenticated):
        return set()
    pairs = Block.objects.filter(Q(blocker=user) | Q(blocked=user)).values_list("blocker_id", "blocked_id")
    return {other for pair in pairs for other in pair if other != user.pk}


def is_blocked_between(user_a, user_b):
    if not (user_a and user_a.is_authenticated):
        return False
    return Block.objects.filter(
        Q(blocker=user_a, blocked=user_b) | Q(blocker=user_b, blocked=user_a)
    ).exists()


def is_following(follower, followed):
    if not (follower and follower.is_authenticated):
        return False
    return Follow.objects.filter(follower=follower, followed=followed).exists()


def can_view(viewer, owner, visibility):
    """May `viewer` see an area of `owner`'s profile set to `visibility`?

    `viewer` may be an AnonymousUser. Owners always see their own data, even
    when the area is set to private.
    """
    viewer_is_authenticated = bool(viewer and viewer.is_authenticated)

    if viewer_is_authenticated and viewer.pk == owner.pk:
        return True

    if is_blocked_between(viewer, owner):
        return False

    if visibility == ProfileVisibility.PUBLIC:
        return True
    if visibility == ProfileVisibility.FOLLOWERS:
        return is_following(viewer, owner)
    return False
