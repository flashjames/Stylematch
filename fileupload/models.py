#-*- coding:utf-8 -*-
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
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    file = models.ImageField(upload_to=get_image_path)
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
    default_storage.delete(instance.file.path)

post_delete.connect(delete_filefield, Picture)
