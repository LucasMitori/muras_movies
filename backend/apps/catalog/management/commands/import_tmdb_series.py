from django.core.management.base import BaseCommand, CommandError

from apps.catalog.importers import import_series
from apps.catalog.integrations.tmdb import TMDBClient, TMDBError


class Command(BaseCommand):
    help = "Import (or refresh) one TV series from TMDB by its TMDB id."

    def add_arguments(self, parser):
        parser.add_argument("tmdb_id", type=int)

    def handle(self, *args, **options):
        tmdb_id = options["tmdb_id"]
        try:
            with TMDBClient() as client:
                payload = client.series(tmdb_id)
        except TMDBError as exc:
            raise CommandError(str(exc)) from exc

        media_item = import_series(payload)
        self.stdout.write(self.style.SUCCESS(f"Imported series #{media_item.id}: {media_item.title}"))
