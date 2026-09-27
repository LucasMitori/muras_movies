"""Rebuildable aggregates derived from user activity in other apps.

Kept in catalog (not library) so MediaItem stays the single owner of its
own cached fields; library only triggers a recompute after it commits.
"""

from decimal import Decimal

from django.db.models import Avg, Count

# Bayesian-average tuning: a title needs MIN_VOTES ratings before its own
# average outweighs the platform-wide prior. Keeps one 5-star vote from
# outranking a title with hundreds of consistent ratings.
MIN_VOTES = 5
GLOBAL_PRIOR_MEAN = Decimal("7.0")  # on the 1..10 stored scale (3.5 stars)


def recompute_media_item_rating(media_item_id):
    from apps.catalog.models import MediaItem

    stats = MediaItem.objects.filter(pk=media_item_id).first()
    if stats is None:
        return

    agg = stats.ratings.aggregate(avg=Avg("value"), count=Count("id"))
    count = agg["count"] or 0
    avg = agg["avg"]

    if count == 0:
        MediaItem.objects.filter(pk=media_item_id).update(muratori_rating_average=None, muratori_rating_count=0)
        return

    avg = Decimal(str(avg))
    m = Decimal(MIN_VOTES)
    v = Decimal(count)
    bayesian = (v / (v + m)) * avg + (m / (v + m)) * GLOBAL_PRIOR_MEAN

    MediaItem.objects.filter(pk=media_item_id).update(
        muratori_rating_average=bayesian.quantize(Decimal("0.01")),
        muratori_rating_count=count,
    )
