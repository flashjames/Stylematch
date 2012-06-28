from django.core.management.base import BaseCommand
from accounts.models import GalleryImage
import re


class Command(BaseCommand):
    help = "A one time solution to migrate gallery images"

    def handle(self, *args, **options):
        gallery_images = GalleryImage.objects.all()

        for gi in gallery_images:
            new_file = re.sub('^media/', '', gi.file.name)
            if new_file.startswith('user-imgs'):
                gi.file = new_file
                gi.save()
