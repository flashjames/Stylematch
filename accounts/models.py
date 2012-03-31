#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Return existing profile. If not created
# create an empty UserProfile entry for user
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# used by django-profiles
def get_absolute_url(self):
        return ('profile_display', (), { 'username': self.user.username })
    
get_absolute_url = models.permalink(get_absolute_url)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
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

class Service(models.Model):
    TIME_CHOICES = (
        (15, '15 minuter'),
        (30, '30 minuter'),
        (45,'45 minuter'),
        (60, '1 timme'),
        (75, '1 timme 15 minuter'),
        (90,'1 timme 30 minuter'),
        (105,'1 timme 45 minuter'),
        (120,'2 timmar'),
        (135,'2 timmar 15 minuter'),
        (150,'2 timmar 30 minuter'),
        (165,'2 timmar 45 minuter'),
        (180,'3 timmar'),
        (195,'3 timmar 15 minuter'),
        (210,'3 timmar 30 minuter'),
        (225,'3 timmar 45 minuter'),
        (240,'4 timmar'),
        (300,'5 timmar'),
        (360,'6 timmar'),
        (420,'7 timmar'),
        )
    length = models.IntegerField("Tid", choices=TIME_CHOICES,max_length=3)
    name = models.CharField("Service (ex. Färga hår)", max_length=40)
    price = models.IntegerField("Pris i kronor", max_length=6)
    
    # TODO: längd på desc?
    description = models.CharField("Förklaring", max_length=200)
    display_on_profile = models.BooleanField("Visa på profil", blank=True)
    
    # user that has this service
    user = models.ForeignKey(User, editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)

    class Meta:
        ordering = ['order']

