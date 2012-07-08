from django.core.management.base import BaseCommand
from index.models import ScheduledCheck
import re
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Checks all scheduled accounts and send out "
           "email if they are no longer good."

    def handle(self, *args, **options):
        users = ScheduledCheck.objects.filter(notification_sent=False)
        for user in users:
            if not not user.check():
                # User is no longer approved.
                # TODO: SEND E-MAIL TO ADMIN
                logger.warn("User %s %s is no longer valid" %
                        (user.first_name, user.last_name))
                user.notification_sent = True
                user.save()
            else:
                # User is valid, remove from ScheduledCheck
                logger.debug("User %s %s checked and approved." %
                        user.first_name, user.last_name))
                user.delete()
