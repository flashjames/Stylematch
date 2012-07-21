from django.core.management.base import BaseCommand
from accounts.models import GalleryImage
from index.models import InspirationVote
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ("Clear all votes and vote objects")

    def handle(self, *args, **options):
        InspirationVote.objects.all().delete()
        GalleryImage.objects.all().update(votes=0)
