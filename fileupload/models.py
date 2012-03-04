from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_delete
from django.core.files.storage import default_storage

import os

class Picture(models.Model):
    def get_image_path(instance, filename):
        return os.path.join(settings.UPLOAD_PATH_USER_IMGS, instance.filename)

    def __unicode__(self):
        return self.file

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, user, filename, *args, **kwargs):
        self.user = user
        self.filename = filename
        super(Picture, self).save(*args, **kwargs)

    file = models.ImageField(upload_to=get_image_path)
    filename = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, editable=False)


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
