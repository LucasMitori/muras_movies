"""Social graph and privacy enforcement.

The visibility tests matter more than the follow/block plumbing: they are the
only thing standing between a user's "followers only" setting and a stranger
reading their library.
"""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Block, Follow, ProfileVisibility, User
from apps.catalog.models import MediaItem, MediaType
from apps.library.models import ConsumptionEvent, LibraryEntry, LibraryStatus

PASSWORD = "a-strong-password-1"


@pytest.fixture
def make_user(db):
    def _make(username, **profile_fields):
        user = User.objects.create_user(username=username, email=f"{username}@example.com", password=PASSWORD)
        if profile_fields:
            for field, value in profile_fields.items():
                setattr(user.profile, field, value)
            user.profile.save()
        return user

    return _make


@pytest.fixture
def media_item(db):
    return MediaItem.objects.create(media_type=MediaType.MOVIE, slug="a-film", title="A Film")


def logged_in(user):
    client = APIClient()
    assert client.login(username=user.username, password=PASSWORD)
    return client


# --- following --------------------------------------------------------------


def test_follow_and_unfollow_updates_the_relationship_and_counts(make_user):
    alice, bob = make_user("alice"), make_user("bob")
    client = logged_in(alice)

    assert client.post("/api/accounts/users/bob/follow/").status_code == 201
    assert Follow.objects.filter(follower=alice, followed=bob).exists()

    bob_detail = client.get("/api/accounts/users/bob/")
    assert bob_detail.data["followers_count"] == 1
    assert bob_detail.data["is_following"] is True

    assert client.delete("/api/accounts/users/bob/follow/").status_code == 204
    assert not Follow.objects.filter(follower=alice, followed=bob).exists()


def test_following_twice_is_idempotent_rather_than_a_constraint_error(make_user):
    alice, bob = make_user("alice"), make_user("bob")
    client = logged_in(alice)

    assert client.post("/api/accounts/users/bob/follow/").status_code == 201
    assert client.post("/api/accounts/users/bob/follow/").status_code == 201
    assert Follow.objects.filter(follower=alice, followed=bob).count() == 1


def test_cannot_follow_yourself(make_user):
    alice = make_user("alice")
    assert logged_in(alice).post("/api/accounts/users/alice/follow/").status_code == 400


def test_following_requires_authentication(make_user):
    make_user("bob")
    assert APIClient().post("/api/accounts/users/bob/follow/").status_code in (401, 403)


def test_followers_and_following_lists(make_user):
    alice, bob = make_user("alice"), make_user("bob")
    Follow.objects.create(follower=alice, followed=bob)

    client = logged_in(alice)
    followers = client.get("/api/accounts/users/bob/followers/")
    assert [row["username"] for row in followers.data["results"]] == ["alice"]

    following = client.get("/api/accounts/users/alice/following/")
    assert [row["username"] for row in following.data["results"]] == ["bob"]


# --- blocking --------------------------------------------------------------


def test_blocking_hides_the_user_from_listings_and_detail_in_both_directions(make_user):
    alice, bob = make_user("alice"), make_user("bob")
    Block.objects.create(blocker=alice, blocked=bob)

    # The blocker cannot see the blocked user...
    as_alice = logged_in(alice)
    assert as_alice.get("/api/accounts/users/bob/").status_code == 404
    assert "bob" not in [row["username"] for row in as_alice.get("/api/accounts/users/").data["results"]]

    # ...and the blocked user cannot see the blocker either.
    as_bob = logged_in(bob)
    assert as_bob.get("/api/accounts/users/alice/").status_code == 404
    assert "alice" not in [row["username"] for row in as_bob.get("/api/accounts/users/").data["results"]]


def test_blocking_removes_existing_follows_in_both_directions(make_user):
    alice, bob = make_user("alice"), make_user("bob")
    Follow.objects.create(follower=alice, followed=bob)
    Follow.objects.create(follower=bob, followed=alice)

    assert logged_in(alice).post("/api/accounts/users/bob/block/").status_code == 201
    assert not Follow.objects.filter(follower__in=[alice, bob], followed__in=[alice, bob]).exists()


def test_a_block_can_be_undone_even_though_the_user_is_hidden(make_user):
    """Regression guard: the blocked user is excluded from the viewset's
    queryset, so unblock must not resolve the target through get_object().
    """
    alice, bob = make_user("alice"), make_user("bob")
    Block.objects.create(blocker=alice, blocked=bob)

    client = logged_in(alice)
    assert client.delete("/api/accounts/users/bob/block/").status_code == 204
    assert not Block.objects.filter(blocker=alice, blocked=bob).exists()
    assert client.get("/api/accounts/users/bob/").status_code == 200


def test_cannot_block_yourself(make_user):
    alice = make_user("alice")
    assert logged_in(alice).post("/api/accounts/users/alice/block/").status_code == 400


def test_my_blocks_lists_only_users_the_requester_blocked(make_user):
    alice, bob, carol = make_user("alice"), make_user("bob"), make_user("carol")
    Block.objects.create(blocker=alice, blocked=bob)
    Block.objects.create(blocker=carol, blocked=alice)

    response = logged_in(alice).get("/api/accounts/me/blocks/")
    assert [row["username"] for row in response.data["results"]] == ["bob"]


# --- library visibility ----------------------------------------------------


@pytest.fixture
def owner_with_library(make_user, media_item):
    def _make(library_visibility):
        owner = make_user("owner", library_visibility=library_visibility)
        LibraryEntry.objects.create(user=owner, media_item=media_item, status=LibraryStatus.COMPLETED)
        return owner

    return _make


def test_public_library_is_readable_anonymously(owner_with_library):
    owner_with_library(ProfileVisibility.PUBLIC)
    response = APIClient().get("/api/accounts/users/owner/library/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_followers_only_library_is_hidden_from_anonymous_and_non_followers(owner_with_library, make_user):
    owner_with_library(ProfileVisibility.FOLLOWERS)
    stranger = make_user("stranger")

    assert APIClient().get("/api/accounts/users/owner/library/").status_code == 403
    assert logged_in(stranger).get("/api/accounts/users/owner/library/").status_code == 403


def test_followers_only_library_is_visible_to_a_follower(owner_with_library, make_user):
    owner = owner_with_library(ProfileVisibility.FOLLOWERS)
    follower = make_user("follower")
    Follow.objects.create(follower=follower, followed=owner)

    response = logged_in(follower).get("/api/accounts/users/owner/library/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_being_followed_by_the_owner_does_not_grant_access(owner_with_library, make_user):
    """followers-only means people who follow the owner, not people the owner
    follows. Getting this backwards would leak the library to anyone the owner
    chose to follow.
    """
    owner = owner_with_library(ProfileVisibility.FOLLOWERS)
    other = make_user("other")
    Follow.objects.create(follower=owner, followed=other)

    assert logged_in(other).get("/api/accounts/users/owner/library/").status_code == 403


def test_private_library_is_hidden_from_everyone_but_the_owner(owner_with_library, make_user):
    owner = owner_with_library(ProfileVisibility.PRIVATE)
    follower = make_user("follower")
    Follow.objects.create(follower=follower, followed=owner)

    assert APIClient().get("/api/accounts/users/owner/library/").status_code == 403
    assert logged_in(follower).get("/api/accounts/users/owner/library/").status_code == 403

    own = logged_in(owner).get("/api/accounts/users/owner/library/")
    assert own.status_code == 200
    assert own.data["count"] == 1


def test_can_view_library_flag_matches_the_enforced_outcome(owner_with_library, make_user):
    owner_with_library(ProfileVisibility.FOLLOWERS)
    stranger = make_user("stranger")
    client = logged_in(stranger)

    assert client.get("/api/accounts/users/owner/").data["can_view_library"] is False
    assert client.get("/api/accounts/users/owner/library/").status_code == 403


# --- diary dates -----------------------------------------------------------


def test_diary_dates_are_withheld_while_the_diary_itself_stays_visible(make_user, media_item):
    owner = make_user(
        "owner",
        library_visibility=ProfileVisibility.PUBLIC,
        diary_dates_visibility=ProfileVisibility.PRIVATE,
    )
    ConsumptionEvent.objects.create(user=owner, media_item=media_item, watched_on="2026-01-15")

    response = APIClient().get("/api/accounts/users/owner/diary/")
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["watched_on"] is None


def test_diary_dates_are_shown_when_visibility_allows(make_user, media_item):
    owner = make_user(
        "owner",
        library_visibility=ProfileVisibility.PUBLIC,
        diary_dates_visibility=ProfileVisibility.PUBLIC,
    )
    ConsumptionEvent.objects.create(user=owner, media_item=media_item, watched_on="2026-01-15")

    response = APIClient().get("/api/accounts/users/owner/diary/")
    assert response.data["results"][0]["watched_on"] == "2026-01-15"


def test_diary_is_hidden_entirely_when_the_library_is_private(make_user, media_item):
    owner = make_user("owner", library_visibility=ProfileVisibility.PRIVATE)
    ConsumptionEvent.objects.create(user=owner, media_item=media_item, watched_on="2026-01-15")

    assert APIClient().get("/api/accounts/users/owner/diary/").status_code == 403
