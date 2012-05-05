#!/usr/bin/python
#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from tools import *

weekdays_model = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']   

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
        UserProfile.objects.create(user=instance,
                                   temporary_profile_url= uuid.uuid4().hex,
                                   display_on_first_page = True,
                                   salon_name = 'Namn på salongen',
                                   salon_city = 'Stad',
                                   salon_adress = 'Adress till salongen',
                                   profile_text = 'Det här är en beskrivande text av vad salongen är och står för, samt annan intressant information',
                                   number_on_profile = True,
                                   )

        OpenHours.objects.create(user=instance)

        Service.objects.create(user = instance, 
                                length = 60, 
                                name = "Klippning",
                                price = 500, 
                                description = "Kort klippning", 
                                display_on_profile = True)


        Service.objects.create(user = instance, 
                                length = 105, 
                                name = "Hårfärgning",
                                price = 140, 
                                description = "Naturliga färger", 
                                display_on_profile = True)

class UserProfile(models.Model):
    """
    TODO:
    fixa så email från huvudprofilen visas här
    fixa så twitter och facebook profil visas här, se styleseat
    """
    
    user = models.ForeignKey(User, unique=True, editable=False)
    profile_first_name = models.CharField("Förnamn", max_length=40, blank=True)
    profile_last_name = models.CharField("Efternamn", max_length=40, blank=True)
    
    display_on_first_page = models.BooleanField(editable=False)
    
    # max_length? less?
    profile_text = models.CharField("Om mig", max_length=500, blank=True)

    profile_url = models.CharField("Min Stylematchhemsida", max_length=15, blank=True, validators=[MaxLengthValidator(15)])
    # used to reach profile if no profile_url set
    temporary_profile_url = models.CharField(editable=False, unique=True, max_length=36)

    # select phone number to display on profile
    DISPLAY_NUMBER_CHOICES = (
        (True, 'Personligt telefonnummer'),
        (False, 'Salongens telefonnummer'),
        )
    number_on_profile = models.BooleanField("Vilket telefonnummer ska visas på profilen?",max_length=1, choices=DISPLAY_NUMBER_CHOICES)
    
    personal_phone_number = models.IntegerField("Personligt telefonnummer", max_length=20, blank=True,null=True)
  
    # salong
    salon_phone_number = models.IntegerField("Salongens telefonnummer", max_length=20, blank=True,null=True)
    salon_name = models.CharField("Salongens namn", max_length=30, blank=True)
    salon_city = models.CharField("Stad", max_length=30, blank=True)
    salon_url = models.URLField("Salongens hemsida", blank=True)
    salon_adress = models.CharField("Salongens adress",max_length=30, blank=True)
    
    zip_adress = models.IntegerField("Postnummer", max_length=6, blank=True, null=True)


    url_online_booking = models.URLField("Adress till online bokningssystem", blank=True)
    show_booking_url = models.BooleanField("Min salong har online-bokning", blank=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.profile_first_name, self.profile_last_name)

class Service(models.Model):
    buffer = generate_list_of_quarters(15, 420+15, format_minutes_to_pretty_format)
    TIME_CHOICES = tuple(buffer)


    length = models.IntegerField("Längd", choices=TIME_CHOICES,max_length=3)
    name = models.CharField("Namn (ex. Herrklippning)", max_length=20)
    price = models.IntegerField("Pris i kronor", max_length=6)
    
    # TODO: längd på desc? 
    description = models.CharField("Beskrivning", max_length=200, validators=[MaxLengthValidator(200)])
    display_on_profile = models.BooleanField("Visa på profil", blank=True)
    
    # user that has this service
    user = models.ForeignKey(User, editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)

    class Meta:
        # deliver the services sorted on the order field
        # needs to be here, or the services admin ui will break
        ordering = ['order']

class OpenHours(models.Model):

    # Do not change if you dont know what you're doing!!
    closed_value = -1

    
    time_list = generate_list_of_quarters(60 * 8, 60 * 22 + 15)
    time_list.insert(0, (closed_value, 'Stängt'))

    # Since Python tuples are immutable we need to use a list as a temporary buffer
    time_tuple = tuple(time_list)

    user = models.ForeignKey(User, editable=False)

    # 8:00 AM
    default_open_time = 480
    # 17:00 PM
    default_close_time = 1020

    # For time being, default lunches to always be closed.
    default_lunch_open = closed_value
    default_lunch_close = closed_value

    # Store days who should be defaulted as closed in a list for easier
    # configuration in future.
    default_closed_days = ['sun']

    # Instead of having duplicate code we generate the code dynamically and 
    # execute it. FIXME: This MIGHT be unsafe, so if any problem occurs in 
    # this model this is probably why.
    for day in weekdays_model:
    
        if day in default_closed_days:            
            default_open_time = closed_value
            default_close_time = closed_value

        code = day + ' = models.IntegerField("", choices=time_tuple, default = ' + str(default_open_time) + ')'
        exec(code)

        code = day + '_closed = models.IntegerField("", choices=time_tuple, default = ' + str(default_close_time) + ')'
        exec(code)

        code = day + '_lunch = models.IntegerField("", choices=time_tuple, default = ' + str(default_lunch_open) + ')'
        exec(code)

        code = day + '_lunch_closed = models.IntegerField("", choices=time_tuple, default = ' + str(default_lunch_close) + ')'
        exec(code)



from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_delete
from django.core.files.storage import default_storage

import os

# client side url to images, without image filename
# used in the view that edit the images on the profile
def get_image_url(filename):
    return os.path.join(settings.STATIC_URL,
                    settings.PATH_USER_IMGS, filename)

class Picture(models.Model):
    # server-side, full path to upload image including filename
    def get_image_path(instance, filename):
        return os.path.join(settings.UPLOAD_PATH_USER_IMGS, instance.filename)

    def get_image_url(self):
        return get_image_url(self.filename)

    def __unicode__(self):
        return self.filename

    file = models.ImageField(upload_to=get_image_path, blank = True)
    filename = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, editable=False)
    upload_date = models.DateTimeField(auto_now_add=True,editable=False)

    # choices probably not needed, only usable for forms to get readable name
    # what i wanted was a real enum which could be used when setting the value
    IMAGE_TYPE_CHOICES = (
        ('G', 'Gallery'),
        ('P', 'Unused Profile Image'),
        ('C', 'Current Profile Image'),
        )
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE_CHOICES,editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)
    
    # unused if it's a profile image
    display_on_profile = models.BooleanField("Visa på profil", blank=True)


    def save(self, *args, **kwargs):
        super(Picture, self).save(*args, **kwargs) 

        if self.image_type == 'C':
            # The newly saved Picture object was selected as current 
            # profile picture. Therefor we need to reset the previous profile pic.

            # There should not be more than 1 previous profile picture, but rather
            # safe than sorry. 
            Picture.objects.filter(user__exact= self.user).filter(
            image_type='C').exclude(id = self.id).update(image_type = 'G')

    class Meta:
        # deliver the images sorted on the order field
        # needs to be here, or the images admin ui will break
        ordering = ['order']

     
# Signals handler for deleting files after object record deleted
# In Django 1.3, delete a record not remove the associated files
def delete_filefield(sender, **kwargs):
    """Automatically deleted files when records removed.
    
    On Django 1.3, removing records will not followed by deleting files.
    Should manually delete PDF using signals post_delete.

    This function can be done more generic
    
    https://github.com/h3/django-webcore/blob/master/webcore/utils/storage.py#L8
    Explanation in comment 1 -
    http://obroll.com/automatically-delete-file-in-filefield-django-1-3-when-object-record-deleted/
    """
    instance = kwargs.get('instance')

    """
    The most natural way to get name of file would be instance.file.path
    but since we're using amazon S3 for storage, the file object does not
    have a path() method, which is called when trying to get attribute .path
    of a file object. -> using attribute .name which we save in the
    model.
    -> This will probably be a problem if we move to filebased storage.
    """
    
    default_storage.delete(instance.file.name)

post_delete.connect(delete_filefield, Picture)

class InviteCode(models.Model):
    used = models.BooleanField("Have the invite code been used?", default=False)
    invite_code = models.CharField("The string to use as invite code", max_length=30)
    comment = models.CharField("To who was the invitecode given? And so on..", max_length=500)
    
    def __unicode__(self):
        return u'Invitecode: %s Used: %s' % (self.invite_code, self.used)
