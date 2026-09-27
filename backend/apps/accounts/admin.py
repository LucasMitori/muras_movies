from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import Block, Follow, Profile, User


@admin.register(User)
class MuratoriUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "library_visibility")
    search_fields = ("user__username", "display_name")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_at")
    autocomplete_fields = ("follower", "followed")


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")
    autocomplete_fields = ("blocker", "blocked")
