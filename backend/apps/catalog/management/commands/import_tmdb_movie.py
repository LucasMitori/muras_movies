from django.core.management.base import BaseCommand, CommandError

from apps.catalog.importers import import_movie
from apps.catalog.integrations.tmdb import TMDBClient, TMDBError


class Command(BaseCommand):
    help = "Import (or refresh) one movie from TMDB by its TMDB id."

    def add_arguments(self, parser):
        parser.add_argument("tmdb_id", type=int)

    def handle(self, *args, **options):
        tmdb_id = options["tmdb_id"]
        try:
            with TMDBClient() as client:
                payload = client.movie(tmdb_id)
        except TMDBError as exc:
            raise CommandError(str(exc)) from exc

        media_item = import_movie(payload)
        self.stdout.write(self.style.SUCCESS(f"Imported movie #{media_item.id}: {media_item.title}"))
