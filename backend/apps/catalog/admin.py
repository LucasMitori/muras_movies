from django.contrib import admin

from apps.catalog.models import ExternalId, Genre, MediaItem, MovieDetails, SeriesDetails


class MovieDetailsInline(admin.StackedInline):
    model = MovieDetails
    can_delete = False


class SeriesDetailsInline(admin.StackedInline):
    model = SeriesDetails
    can_delete = False


class ExternalIdInline(admin.TabularInline):
    model = ExternalId
    extra = 0


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "is_active", "muratori_rating_average", "muratori_rating_count")
    list_filter = ("media_type", "is_active", "is_editorial_override")
    search_fields = ("title", "original_title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [MovieDetailsInline, SeriesDetailsInline, ExternalIdInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
