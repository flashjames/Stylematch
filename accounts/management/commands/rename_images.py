from django.core.management.base import BaseCommand
from accounts.models import GalleryImage, ProfileImage
import re


class Command(BaseCommand):
    help = "A one time solution to migrate images"

    def handle(self, *args, **options):
        gallery_images = GalleryImage.objects.all()
        for img in gallery_images:
            new_file = re.sub('^media/', '', img.file.name)
            if new_file.startswith('user-imgs'):
                img.file = new_file
                img.save()

        profile_images = ProfileImage.objects.all()
        for img in profile_images:
            new_file = re.sub('^media/', '', img.file.name)
            if new_file.startswith('user-imgs'):
                img.file = new_file
                img.save()
