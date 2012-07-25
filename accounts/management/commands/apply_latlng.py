from django.core.management.base import BaseCommand
from accounts.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "A one time solution to get lat/lng attributes for all profiles"

    def handle(self, *args, **options):
        users = UserProfile.objects.all()

        for user in users:
            location = "%s, %s, %s" % (user.salon_adress, user.zip_adress, user.salon_city)
            logger.debug("Giving latlng to \"%s\"" % location)
            latlng = user.geocode(location)
            if latlng[0] is None or latlng[1] is None:
                logger.error("Couldn't geocode location: %s" % location)
            else:
                logger.debug("Coordinates returned: %s" % ", ".join(latlng))
                user.latitude = latlng[0]
                user.longitude = latlng[1]
                user.save()
