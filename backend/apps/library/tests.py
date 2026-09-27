import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import MediaItem, MediaType
from apps.library.models import Rating, Review


@pytest.fixture
def movie(db):
    return MediaItem.objects.create(media_type=MediaType.MOVIE, slug="a-movie", title="A Movie")


@pytest.fixture
def alice(db):
    return User.objects.create_user(username="alice", email="alice@example.com", password="alice-password-1")


@pytest.fixture
def bob(db):
    return User.objects.create_user(username="bob", email="bob@example.com", password="bob-password-12")


def client_as(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_rating_is_unique_per_user_and_media_item(alice, movie):
    client = client_as(alice)
    first = client.post("/api/ratings/", {"media_item": movie.id, "value": 8})
    assert first.status_code == 201

    duplicate = client.post("/api/ratings/", {"media_item": movie.id, "value": 5})
    assert duplicate.status_code == 400
    assert Rating.objects.filter(user=alice, media_item=movie).count() == 1


@pytest.mark.django_db(transaction=True)
def test_rating_updates_media_item_bayesian_aggregate(alice, bob, movie):
    # transaction=True: the aggregate recompute runs on transaction.on_commit,
    # which a plain django_db test never fires (it wraps the test in an
    # atomic block that's rolled back, not committed).
    client_as(alice).post("/api/ratings/", {"media_item": movie.id, "value": 10})
    client_as(bob).post("/api/ratings/", {"media_item": movie.id, "value": 6})

    movie.refresh_from_db()
    assert movie.muratori_rating_count == 2
    # Two ratings pulled toward the 7.0 prior with MIN_VOTES=5: strictly
    # between the raw average (8.0) and the prior, not equal to either.
    assert 7.0 < float(movie.muratori_rating_average) < 8.0


@pytest.mark.django_db
def test_user_cannot_edit_another_users_review(alice, bob, movie):
    review = Review.objects.create(user=alice, media_item=movie, body="Alice's take.")

    bob_client = client_as(bob)
    response = bob_client.patch(f"/api/reviews/{review.id}/", {"body": "hijacked"})
    assert response.status_code == 403

    review.refresh_from_db()
    assert review.body == "Alice's take."


@pytest.mark.django_db
def test_library_entry_list_never_leaks_other_users_entries(alice, bob, movie):
    from apps.library.models import LibraryEntry, LibraryStatus

    LibraryEntry.objects.create(user=alice, media_item=movie, status=LibraryStatus.COMPLETED)
    LibraryEntry.objects.create(user=bob, media_item=movie, status=LibraryStatus.WATCHING)

    response = client_as(alice).get("/api/entries/")
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["status"] == LibraryStatus.COMPLETED


@pytest.mark.django_db
def test_anonymous_user_cannot_create_a_rating(movie):
    response = APIClient().post("/api/ratings/", {"media_item": movie.id, "value": 8})
    assert response.status_code in (401, 403)
