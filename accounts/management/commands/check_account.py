from django.core.management.base import BaseCommand
from django.core.mail import send_mail
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
                # user is ok, remove from checks
                logger.debug("Checked %s with command, but no harm is done." % user)
                check.delete()
            else:
                # User is no longer approved.
                logger.warn("User %s %s is no longer valid" % \
                        (user.first_name, user.last_name))

                # send an email to admin about this.
                send_mail(u'Användare ej längre godkänd i %s: %s %s' % (userprofile.salon_city,
                                                userprofile.user.first_name,
                                                userprofile.user.last_name),
                          'http://stylematch.se/admin/auth/user/%s\n'
                          'http://stylematch.se/%s/' % (userprofile.user.pk,
                                    userprofile.profile_url),
                          'noreply@stylematch.se',
                          ['admin@stylematch.se'])
                check.notification_sent = True
                check.save()
