from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_delete
from django.core.files.storage import default_storage

import os

class Picture(models.Model):
    # full path to upload image to, including filename
    def get_image_path(instance, filename):
        return os.path.join(settings.UPLOAD_PATH_USER_IMGS, instance.filename)

    # client side url to image
    def get_image_url(self):
        return os.path.join(settings.STATIC_URL,
                        settings.PATH_USER_IMGS, self.filename)

    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, user, filename, *args, **kwargs):
        # fill the fields, with correct values
        self.user = user
        self.filename = filename

        # default image type for now, Gallery
        self.image_type = 'G'
        super(Picture, self).save(*args, **kwargs)

    file = models.ImageField(upload_to=get_image_path)
    filename = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, editable=False)
    upload_date = models.DateTimeField(auto_now_add=True,editable=False)

    # choices probably not needed, only usable for forms to get readable name
    # what i wanted was a real enum which could be used when setting the value
    IMAGE_TYPE_CHOICES = (
        ('G', 'Gallery'),
        ('P', 'Profile'),
        )
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE_CHOICES,editable=False)

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
