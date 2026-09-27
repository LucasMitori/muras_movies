from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.catalog.services import recompute_media_item_rating
from apps.library.models import Rating


def _schedule_recompute(media_item_id):
    transaction.on_commit(lambda: recompute_media_item_rating(media_item_id))


@receiver(post_save, sender=Rating)
def rating_saved(sender, instance, **kwargs):
    _schedule_recompute(instance.media_item_id)


@receiver(post_delete, sender=Rating)
def rating_deleted(sender, instance, **kwargs):
    _schedule_recompute(instance.media_item_id)
