from django.core.management.base import BaseCommand, CommandError

from apps.catalog.importers import import_movie, import_series
from apps.catalog.integrations.tmdb import TMDBClient, TMDBError


class Command(BaseCommand):
    help = "Seed the catalog with TMDB's popular movies and series (bounded page count)."

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=1, help="Pages of ~20 results each, per media type.")
        parser.add_argument("--movies-only", action="store_true")
        parser.add_argument("--series-only", action="store_true")

    def handle(self, *args, **options):
        pages = options["pages"]
        do_movies = not options["series_only"]
        do_series = not options["movies_only"]

        try:
            with TMDBClient() as client:
                if do_movies:
                    self._import_pages(
                        client.popular_movies, client.movie, import_movie, pages, "movie"
                    )
                if do_series:
                    self._import_pages(
                        client.popular_series, client.series, import_series, pages, "series"
                    )
        except TMDBError as exc:
            raise CommandError(str(exc)) from exc

    def _import_pages(self, list_fn, detail_fn, import_fn, pages, label):
        for page in range(1, pages + 1):
            results = list_fn(page=page).get("results", [])
            for summary in results:
                # /popular only returns genre_ids, not full genre names, and
                # omits runtime/status — fetch the full detail payload so
                # the first import is complete, not just a stub.
                detail = detail_fn(summary["id"])
                media_item = import_fn(detail)
                self.stdout.write(f"  {label} #{media_item.id}: {media_item.title}")
            self.stdout.write(self.style.SUCCESS(f"Imported page {page} of popular {label} results."))
