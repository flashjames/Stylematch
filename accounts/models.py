from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    url = models.URLField("Website", blank=True)
    company = models.CharField(max_length=50, blank=True)

# Return existing profile. If not created
# create an empty UserProfile entry for user
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
