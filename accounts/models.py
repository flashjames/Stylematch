#!/usr/bin/python
#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


# used on all fields that need to have a forced max_length
# django doesnt do this validation by itself
# the value given to MaxLengthValidator should be same as max_length variable
from django.core.validators import MaxLengthValidator

import uuid

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a a new user is created, create a corresponding UserProfile
    TODO: Create different profiles depending on if it's a stylist or a regular user
    """
    if created:
        UserProfile.objects.create(user=instance, temporary_profile_url=uuid.uuid4().hex)
	
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    profile_name = models.CharField("Namn", max_length=40, blank=True)
    profile_phone_number = models.CharField("Personligt telefonnummer", max_length=30, blank=True)
    
    # max_length? less?
    profile_text = models.CharField("Text att visa på profilen", max_length=500, blank=True)

    # TODO: add check if unique
    profile_url = models.CharField("Min profil sida http://avizera.se/", max_length=15, blank=True, validators=[MaxLengthValidator(15)])
    # used to reach profile if no profile_url set
    temporary_profile_url = models.CharField(editable=False, unique=True, max_length=36)

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
    name = models.CharField("Service (ex. Färga hår)", max_length=20)
    price = models.IntegerField("Pris i kronor", max_length=6)
    
    # TODO: längd på desc? 
    description = models.CharField("Förklaring", max_length=200, validators=[MaxLengthValidator(200)])
    display_on_profile = models.BooleanField("Visa på profil", blank=True)
    
    # user that has this service
    user = models.ForeignKey(User, editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)

    class Meta:
        ordering = ['order']
