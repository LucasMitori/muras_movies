from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class Genre(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MediaType(models.TextChoices):
    MOVIE = "movie", "Movie"
    SERIES = "series", "Series"


class MediaItem(TimeStampedModel):
    """Stable canonical identity for a title, regardless of source provider.

    MovieDetails / SeriesDetails hold type-specific fields. Ratings, library
    entries, and reviews all point at MediaItem so the same review model
    works across every media type Muratori eventually supports.
    """

    media_type = models.CharField(max_length=16, choices=MediaType.choices)
    slug = models.SlugField(max_length=220, unique=True)

    title = models.CharField(max_length=300)
    original_title = models.CharField(max_length=300, blank=True)
    original_language = models.CharField(max_length=10, blank=True)
    synopsis = models.TextField(blank=True)

    poster_path = models.CharField(max_length=300, blank=True)
    backdrop_path = models.CharField(max_length=300, blank=True)

    genres = models.ManyToManyField(Genre, related_name="media_items", blank=True)

    # Provider-attributed rating, kept visibly separate from Muratori's own.
    external_vote_average = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    external_vote_count = models.PositiveIntegerField(null=True, blank=True)

    # Rebuildable aggregate of Muratori's own Rating rows (see library.Rating).
    muratori_rating_average = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    muratori_rating_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_editorial_override = models.BooleanField(
        default=False, help_text="Set once staff hand-edit fields; provider sync must not overwrite them."
    )

    class Meta:
        indexes = [
            models.Index(fields=["media_type", "is_active"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.media_type})"


class MovieDetails(models.Model):
    media_item = models.OneToOneField(MediaItem, on_delete=models.CASCADE, related_name="movie_details")
    release_date = models.DateField(null=True, blank=True)
    runtime_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"MovieDetails<{self.media_item_id}>"


class SeriesStatus(models.TextChoices):
    RETURNING = "returning", "Returning series"
    ENDED = "ended", "Ended"
    CANCELED = "canceled", "Canceled"
    IN_PRODUCTION = "in_production", "In production"


class SeriesDetails(models.Model):
    media_item = models.OneToOneField(MediaItem, on_delete=models.CASCADE, related_name="series_details")
    first_air_date = models.DateField(null=True, blank=True)
    last_air_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SeriesStatus.choices, blank=True)
    number_of_seasons = models.PositiveIntegerField(null=True, blank=True)
    number_of_episodes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"SeriesDetails<{self.media_item_id}>"


class ExternalIdProvider(models.TextChoices):
    TMDB = "tmdb", "TMDB"
    IMDB = "imdb", "IMDb"


class ExternalId(TimeStampedModel):
    """Namespaced provider identity used for dedupe and incremental sync."""

    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name="external_ids")
    provider = models.CharField(max_length=20, choices=ExternalIdProvider.choices)
    external_id = models.CharField(max_length=64)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "external_id"], name="unique_provider_external_id"),
            models.UniqueConstraint(fields=["media_item", "provider"], name="unique_media_item_provider"),
        ]

    def __str__(self):
        return f"{self.provider}:{self.external_id}"
