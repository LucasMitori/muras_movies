from django.contrib import admin

from apps.library.models import ConsumptionEvent, LibraryEntry, Rating, Review, ReviewComment


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "media_item", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "media_item__title")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "media_item", "value", "updated_at")
    search_fields = ("user__username", "media_item__title")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "media_item", "is_hidden", "updated_at")
    list_filter = ("is_hidden", "contains_spoilers")
    search_fields = ("user__username", "media_item__title", "body")


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ("author", "review", "parent", "is_hidden", "created_at")
    list_filter = ("is_hidden",)


@admin.register(ConsumptionEvent)
class ConsumptionEventAdmin(admin.ModelAdmin):
    list_display = ("user", "media_item", "watched_on", "is_rewatch")
    list_filter = ("is_rewatch",)
