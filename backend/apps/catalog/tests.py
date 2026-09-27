import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Genre, MediaItem, MediaType, MovieDetails


@pytest.fixture
def action_movie(db):
    item = MediaItem.objects.create(media_type=MediaType.MOVIE, slug="fast-and-furious", title="Fast and Furious")
    MovieDetails.objects.create(media_item=item, runtime_minutes=106)
    item.genres.add(Genre.objects.create(name="Action"))
    return item


@pytest.fixture
def hidden_movie(db):
    return MediaItem.objects.create(
        media_type=MediaType.MOVIE, slug="unlisted", title="Unlisted Movie", is_active=False
    )


@pytest.mark.django_db
def test_catalog_list_is_public_and_excludes_inactive_items(action_movie, hidden_movie):
    response = APIClient().get("/api/media/")
    assert response.status_code == 200
    slugs = [row["slug"] for row in response.data["results"]]
    assert "fast-and-furious" in slugs
    assert "unlisted" not in slugs


@pytest.mark.django_db
def test_catalog_detail_includes_movie_details(action_movie):
    response = APIClient().get(f"/api/media/{action_movie.id}/")
    assert response.status_code == 200
    assert response.data["movie_details"]["runtime_minutes"] == 106
    assert response.data["genres"][0]["name"] == "Action"


@pytest.mark.django_db
def test_anonymous_user_cannot_write_to_the_catalog(action_movie):
    response = APIClient().patch(f"/api/media/{action_movie.id}/", {"title": "Hacked title"})
    # Read-only viewset: PATCH isn't even a routed method.
    assert response.status_code == 405
