"""Normalize TMDB payloads into MediaItem rows.

Upserts by ExternalId(provider="tmdb", external_id) so re-running an import
updates the existing row instead of creating a duplicate. Editorial
overrides (is_editorial_override=True) are never clobbered by a refresh.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import (
    ExternalId,
    ExternalIdProvider,
    Genre,
    MediaItem,
    MediaType,
    MovieDetails,
    SeriesDetails,
    SeriesStatus,
)

_TMDB_SERIES_STATUS_MAP = {
    "Returning Series": SeriesStatus.RETURNING,
    "Ended": SeriesStatus.ENDED,
    "Canceled": SeriesStatus.CANCELED,
    "In Production": SeriesStatus.IN_PRODUCTION,
}


def _unique_slug(title: str, media_type: str) -> str:
    base = slugify(title) or media_type
    candidate = base
    suffix = 1
    while MediaItem.objects.filter(slug=candidate).exists():
        suffix += 1
        candidate = f"{base}-{suffix}"
    return candidate


def _get_or_create_media_item(tmdb_id: int, media_type: str, title: str) -> tuple[MediaItem, bool]:
    external = ExternalId.objects.filter(
        provider=ExternalIdProvider.TMDB, external_id=str(tmdb_id)
    ).select_related("media_item").first()
    if external:
        return external.media_item, False

    media_item = MediaItem.objects.create(
        media_type=media_type,
        slug=_unique_slug(title, media_type),
        title=title,
    )
    ExternalId.objects.create(
        media_item=media_item, provider=ExternalIdProvider.TMDB, external_id=str(tmdb_id)
    )
    return media_item, True


def _sync_genres(media_item: MediaItem, genre_names: list[str]) -> None:
    genres = [Genre.objects.get_or_create(name=name)[0] for name in genre_names]
    media_item.genres.set(genres)


@transaction.atomic
def import_movie(payload: dict) -> MediaItem:
    tmdb_id = payload["id"]
    title = payload.get("title") or payload.get("original_title") or f"TMDB movie {tmdb_id}"
    media_item, created = _get_or_create_media_item(tmdb_id, MediaType.MOVIE, title)

    if created or not media_item.is_editorial_override:
        media_item.title = title
        media_item.original_title = payload.get("original_title", "")
        media_item.original_language = payload.get("original_language", "")
        media_item.synopsis = payload.get("overview", "")
        media_item.poster_path = payload.get("poster_path") or ""
        media_item.backdrop_path = payload.get("backdrop_path") or ""

    media_item.external_vote_average = payload.get("vote_average")
    media_item.external_vote_count = payload.get("vote_count")
    media_item.save()

    _sync_genres(media_item, [g["name"] for g in payload.get("genres", [])])

    MovieDetails.objects.update_or_create(
        media_item=media_item,
        defaults={
            "release_date": payload.get("release_date") or None,
            "runtime_minutes": payload.get("runtime"),
        },
    )

    ExternalId.objects.filter(media_item=media_item, provider=ExternalIdProvider.TMDB).update(
        last_synced_at=timezone.now()
    )

    return media_item


@transaction.atomic
def import_series(payload: dict) -> MediaItem:
    tmdb_id = payload["id"]
    title = payload.get("name") or payload.get("original_name") or f"TMDB series {tmdb_id}"
    media_item, created = _get_or_create_media_item(tmdb_id, MediaType.SERIES, title)

    if created or not media_item.is_editorial_override:
        media_item.title = title
        media_item.original_title = payload.get("original_name", "")
        media_item.original_language = payload.get("original_language", "")
        media_item.synopsis = payload.get("overview", "")
        media_item.poster_path = payload.get("poster_path") or ""
        media_item.backdrop_path = payload.get("backdrop_path") or ""

    media_item.external_vote_average = payload.get("vote_average")
    media_item.external_vote_count = payload.get("vote_count")
    media_item.save()

    _sync_genres(media_item, [g["name"] for g in payload.get("genres", [])])

    SeriesDetails.objects.update_or_create(
        media_item=media_item,
        defaults={
            "first_air_date": payload.get("first_air_date") or None,
            "last_air_date": payload.get("last_air_date") or None,
            "status": _TMDB_SERIES_STATUS_MAP.get(payload.get("status", ""), ""),
            "number_of_seasons": payload.get("number_of_seasons"),
            "number_of_episodes": payload.get("number_of_episodes"),
        },
    )

    ExternalId.objects.filter(media_item=media_item, provider=ExternalIdProvider.TMDB).update(
        last_synced_at=timezone.now()
    )

    return media_item
