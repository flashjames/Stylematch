from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    url = models.URLField("Website", blank=True)
    first_name = models.CharField("First name", max_length=20)
    last_name = models.CharField(max_length=20)
    salon = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    # max_length? less?
    profile_text = models.CharField(max_length=500)

    # adress, have personal adress to?
    # in frontend: should say salon adress
    

# Return existing profile. If not created
# create an empty UserProfile entry for user
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# used by django-profiles
def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    
get_absolute_url = models.permalink(get_absolute_url)
