from django.core.management.base import BaseCommand
from accounts.models import ScheduledCheck, check_profile
import re
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ("Checks all scheduled accounts and send out "
           "email if they are no longer good.")

    def handle(self, *args, **options):
        checks = ScheduledCheck.objects.filter(notification_sent=False)
        for check in checks:
            user = check.user
            if check_profile(user.userprofile, create_checks=False):
                logger.debug("Checked %s with command, but no harm is done." % user)
            else:
                # User is no longer approved.
                # TODO: SEND E-MAIL TO ADMIN
                logger.warn("User %s %s is no longer valid" % \
                        (user.first_name, user.last_name))
                check.notification_sent = True
                check.save()
