from django.conf import settings
from rest_framework import serializers

from apps.catalog.models import Genre, MediaItem, MovieDetails, SeriesDetails


def _image_url(path, size):
    if not path:
        return None
    return f"{settings.TMDB_IMAGE_BASE_URL}{size}{path}"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]


class MovieDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieDetails
        fields = ["release_date", "runtime_minutes"]


class SeriesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeriesDetails
        fields = ["first_air_date", "last_air_date", "status", "number_of_seasons", "number_of_episodes"]


class MediaItemListSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = MediaItem
        fields = [
            "id",
            "slug",
            "media_type",
            "title",
            "poster_url",
            "genres",
            "external_vote_average",
            "muratori_rating_average",
            "muratori_rating_count",
        ]

    def get_poster_url(self, obj):
        return _image_url(obj.poster_path, "w342")


class MediaItemDetailSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)
    movie_details = MovieDetailsSerializer(read_only=True)
    series_details = SeriesDetailsSerializer(read_only=True)

    class Meta:
        model = MediaItem
        fields = [
            "id",
            "slug",
            "media_type",
            "title",
            "original_title",
            "original_language",
            "synopsis",
            "poster_url",
            "backdrop_url",
            "genres",
            "external_vote_average",
            "external_vote_count",
            "muratori_rating_average",
            "muratori_rating_count",
            "movie_details",
            "series_details",
        ]

    def get_poster_url(self, obj):
        return _image_url(obj.poster_path, "w500")

    def get_backdrop_url(self, obj):
        return _image_url(obj.backdrop_path, "w1280")
