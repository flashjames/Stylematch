#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    # allmän info
    profile_name = models.CharField("Namn", max_length=40, blank=True)
    profile_phone_number = models.CharField("Personligt telefonnummer", max_length=30, blank=True)
    # max_length? less?
    profile_text = models.CharField("Text att visa på profilen", max_length=500, blank=True)

    # TODO: add check if unique
    profile_url = models.CharField("Min profil sida http://avizera.se/", max_length=15, blank=True)

    """
    TODO:
    fixa så email från huvudprofilen visas här
    fixa så twitter och facebook profil visas här, se styleseat
    """
    
    # salong
    salon_name = models.CharField("Namn", max_length=30, blank=True)
    salon_city = models.CharField("Stad", max_length=30, blank=True)
    salon_url = models.URLField("Hemsida", blank=True)
    salon_adress = models.CharField(max_length=30, blank=True)
    salon_phone_number = models.CharField("Telefonnummer", max_length=30, blank=True)
    
    # TODO: add validation https://docs.djangoproject.com/en/dev/ref/contrib/localflavor/#sweden-se
    zip_adress = models.IntegerField("Postnummer", max_length=6, blank=True, null=True)
    url_online_booking = models.URLField("Adress till online bokningssystem", blank=True)
    show_booking_url = models.BooleanField("Visa länk till bokningssystem på hemsidan", blank=True)
        

# Return existing profile. If not created
# create an empty UserProfile entry for user
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# used by django-profiles
def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    
get_absolute_url = models.permalink(get_absolute_url)
