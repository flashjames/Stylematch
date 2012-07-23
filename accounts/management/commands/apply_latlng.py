from django.core.management.base import BaseCommand
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "A one time solution to get lat/lng attributes for all profiles"

    def handle(self, *args, **options):
        users = UserProfile.objects.all()

        for user in users:
            location = "%s, %s, %s" % (user.salon_adress, user.zip_adress, user.salon_city)
            latlng = user.geocode(location)
            user.latitude = latlng[0]
            user.longitude = latlng[1]
            user.save()
