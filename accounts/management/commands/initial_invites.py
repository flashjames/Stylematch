from django.core.management.base import BaseCommand
from accounts.models import UserProfile, InviteCode
import logging
import uuid

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Set initial 5 invite codes for all accounts"

    def handle(self, *args, **options):
        users = UserProfile.objects.all()
        invites = InviteCode.objects.all()

        for userprofile in users:
            # get all current nonused invite codes for this accounts
            user_invites = invites.filter(inviter=userprofile, reciever=None)

            # add new invite codes so the account has 5 total
            new_codes_count = 5 - user_invites.count()
            if new_codes_count < 0: new_codes_count = 0
            print
            print ("Going to add %d to %s" % (new_codes_count, userprofile))
            for i in range(new_codes_count):
                code = InviteCode.generate_code()
                invite_code = InviteCode(
                                invite_code=code,
                                inviter=userprofile.user
                              )
                invite_code.save()
                val = invite_code.pk
                print("Added one code( %s )" % invite_code)
