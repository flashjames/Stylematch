#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from registration.signals import user_registered
from accounts.signals import approved_user_criteria_changed

from tools import list_with_time_interval, format_minutes_to_pretty_format

weekdays_model = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']

# used on all fields that need to have a forced max_length
# django doesnt do this validation by itself
# the value given to MaxLengthValidator should be same as max_length variable
from django.core.validators import MaxLengthValidator

import uuid
import os
import re
import logging

logger = logging.getLogger(__name__)


class ProfileValidationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def check_profile(sender, request=None, userprofile=None, create_checks=True, **kwargs):
    """
    When a critical field on a profile has changed this function will be
    called to make sure the profile is still good.

    If the profile is no longer good, a scheduled check object will be
    created that later on is being checked with a cron-script. To manually
    check the profiles use:
      ./manage.py check_profile

    """
    logger.debug("Checking %s" % sender)

    # Retrieve the correct ``userprofile`` profile
    if userprofile is None or userprofile.__class__ != UserProfile:
        if sender.__class__ == UserProfile:
            userprofile = sender
        else:
            instance = kwargs.get('instance')
            if (instance is not None and
                   (instance.__class__ == Service or
                    instance.__class__ == OpenHours)):
                userprofile = instance.user.userprofile
            else:
                logger.error("Check_profile got called from an unexpected "
                             "sender (%s)(class: %s)." % \
                                    (sender, sender.__class__))
                return False

    try:
        # Check the information about salon. address, phone etc
        if not userprofile.salon_name:
            raise ProfileValidationError("Salon name missing.")
        if not userprofile.salon_city:
            raise ProfileValidationError("Salon city missing.")
        if not userprofile.salon_adress:
            raise ProfileValidationError("Salon adress missing.")
        if not userprofile.zip_adress:
            raise ProfileValidationError("Zip adress missing.")
        if not userprofile.salon_phone_number:
            raise ProfileValidationError("Salon phonenumber missing.")

        # There must be a profile image
        if not (userprofile.profile_image_cropped or
                userprofile.profile_image_uncropped):

            raise ProfileValidationError("Profile image missing")

        # Open hours must be reviewed. This happens the first time a user
        # reviews them, and they cannot be "unreviewed".
        if not userprofile.user.openhours:
            raise ProfileValidationError("Openhours is no longer reviewed. "
                                         "How the hell did that happen??")

        # There must be at least one service
        try:
            Service.objects.get(user=userprofile.user)
        except Service.DoesNotExist:
            raise ProfileValidationError("User has no services.")
        except Service.MultipleObjectsReturned:
            pass

        # User must have written a description about themself.
        if not userprofile.profile_text:
            raise ProfileValidationError("Profile text missing")

        # At least one gallery image must be uploaded.
        gi = GalleryImage.objects.filter(user=userprofile.user)
        if gi:
            gi = gi.filter(display_on_profile=True)
            if not gi:
                raise ProfileValidationError("User has uploaded gallery images, "
                                             "but they are not visible.")
        else:
            raise ProfileValidationError("User has no uploaded gallery images.")

    except ProfileValidationError as e:
        # If the user has once been approved, but the profile is no longer
        # valid, then the user should be checked later again. If it turns out
        # to be invalid then too, an admin will be notified.

        # If the user hasn't been approved yet, the profile isn't visible and
        # the admin doesn't have to be notified.

        if userprofile.approved:
            logger.warn(e)
            if create_checks:
                sc, created = ScheduledCheck.objects.get_or_create(user=userprofile.user)
                if created:
                    logger.debug("Created new ScheduledCheck: %s" % sc.user)
        else:
            logger.debug("User %s was not approved for following reason: %s" % (userprofile, e))
        return False

    # If the user passed the test, approve the user.
    if not userprofile.approved:
        userprofile.approved = True
        userprofile.save()
        logger.debug("User %s just got approved!" % userprofile)

        # Send email notifying admin about this.
        send_mail(u'Godkänd användare i %s: %s %s' % (userprofile.salon_city,
                                        userprofile.user.first_name,
                                        userprofile.user.last_name),
                  'http://stylematch.se/admin/auth/user/%s\n'
                  'http://stylematch.se/%s/' % (userprofile.user.pk,
                            userprofile.profile_url),
                  'noreply@stylematch.se',
                  ['admin@stylematch.se'])
    return True
approved_user_criteria_changed.connect(check_profile)


def create_temporary_profile_url(sender, user, request, **kwargs):
    """
    Create a standard profile url at signup step using first name and
    last name. Add number if the url is already taken.

    John Nelson       -> /john-nelson
    John Nelson again -> /john-nelson2

    If, for some reason, first name isn't in POST data, bail out.
    """

    if 'first_name' not in request.POST:
        return
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']

    # Get all users with the same name
    users = User.objects.filter(first_name=first_name,
                                last_name=last_name)

    # This forces a double name to be separate in the list.
    # Eva Marie Johnson => ['Eva', 'Marie', 'Johnson']
    names = (first_name + " " + last_name).split(' ')

    # Join them together using hyphen
    # ['Eva', 'Marie', 'Johnson'] => "Eva-Marie-Johnson"
    tmp_url = "-".join(names).lower()
    tmp_url = re.sub(r'\s', '', tmp_url)

    # Append a number depending on how many that has the exact name before
    # ex. 2 users before have the exact same name:
    # "Eva-Marie-Johnson" => "Eva-Marie-Johnson3"
    if len(users) > 1:
        tmp_url += "%d" % (len(users))

    # Save the URL
    userprofile = user.userprofile
    userprofile.profile_url = tmp_url
    userprofile.save()
user_registered.connect(create_temporary_profile_url)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a a new user is created, create a corresponding UserProfile
    TODO:
    Create different profiles depending on if it's a stylist or a regular user
    """
    if created:
        UserProfile.objects.create(
                user=instance,
                temporary_profile_url=uuid.uuid4().hex,
                                   )
        OpenHours.objects.create(user=instance)


class DirtyFieldsMixin(object):
    """
    Add a method ``get_dirty_fields`` that allows a model to see the changed
    fields upon save().

    """
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self):
        return dict(
                [(f.name, getattr(self, f.name))
                 for f
                 in self._meta.local_fields
                 if not f.rel]
        )

    def get_dirty_fields(self):
        """
        Returns a dict of changed fields

        """
        new_state = self._as_dict()
        return dict(
                [(key, (value, new_state[key]))
                 for key, value
                 in self._original_state.iteritems()
                 if value != new_state[key]]
        )


class Service(models.Model):
    buffer = list_with_time_interval(
                start=30,
                stop=6 * 60,
                interval=30,
                format_function=format_minutes_to_pretty_format)
    TIME_CHOICES = tuple(buffer)

    length = models.IntegerField("Tidsåtgång *",
                                 choices=TIME_CHOICES,
                                 max_length=3)
    name = models.CharField("Namn (ex. Klippning kort hår) *",
                            max_length=20)
    price = models.IntegerField("Pris i kronor *", max_length=6)

    # TODO: längd på desc?
    description = models.CharField("Beskrivning (ex. Inklusive styling)",
                                   max_length=200,
                                   validators=[MaxLengthValidator(200)],
                                   blank=True)
    display_on_profile = models.BooleanField("Visa på profil", blank=True)

    # user that has this service
    user = models.ForeignKey(User, editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)

    class Meta:
        # deliver the services sorted on the order field
        # needs to be here, or the services admin ui will break
        ordering = ['order']


class OpenHours(models.Model):
    """
    TODO: Fix model description
    """

    # Do not change if you dont know what you're doing!!
    closed_value = -1

    time_list = list_with_time_interval(
                start=60 * 6,
                stop=60 * 24,
                interval=15)
    time_list.insert(0, (closed_value, 'Stängt'))

    # Since Python tuples are immutable we need to use a list as
    # a temporary buffer
    time_tuple = tuple(time_list)

    user = models.OneToOneField(User, editable=False)

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

        code = (day + ' = models.IntegerField('
                                    '"",'
                                    'choices=time_tuple,'
                                    'default=' + str(default_open_time) + ')')
        exec(code)

        code = (day + '_closed = models.IntegerField('
                                    '"",'
                                    'choices=time_tuple,'
                                    'default=' + str(default_close_time) + ')')
        exec(code)

    reviewed = models.BooleanField(default=False)


# client side url to images, without image filename
# used in the view that edit the images on the profile
def get_image_url(filename):
    return os.path.join(settings.MEDIA_URL,
                        settings.PATH_USER_IMGS,
                        filename)


class BaseImage(models.Model):
    # server-side, full path to upload image including filename
    def get_image_path(instance, filename):
        return os.path.join(settings.UPLOAD_PATH_USER_IMGS, instance.filename)

    def get_image_url(self):
        return get_image_url(self.filename)

    def __unicode__(self):
        return self.filename

    file = models.ImageField(upload_to=get_image_path,
                             blank=True)
    filename = models.CharField(max_length=50,
                                blank=True)
    user = models.ForeignKey(User,
                             editable=False)
    upload_date = models.DateTimeField(auto_now_add=True,
                                       editable=False)

    class Meta:
        abstract = True


class ProfileImage(BaseImage):
    cropped = models.BooleanField(default=False)


class GalleryImage(BaseImage):
    votes = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=100,
                               blank=True)
    order = models.PositiveIntegerField(blank=True,
                                        editable=True,
                                        null=True)
    display_on_profile = models.BooleanField("Visa på profil",
                                             blank=True,
                                             default=True)

    class Meta:
        # deliver the images sorted on the order field
        # needs to be here, or the edit_images ui will break
        ordering = ['order']


class UserProfile(DirtyFieldsMixin, models.Model):
    """
    TODO:
    fixa så twitter och facebook profil visas här, se styleseat
    fixa description till denna modell
    """
    user = models.OneToOneField(User, parent_link=True,
                                unique=True, editable=False)

    # max_length? less?
    profile_text = models.CharField("Om mig", max_length=500, blank=True)

    profile_url = models.CharField("http://stylematch.se/",
                                   max_length=40,
                                   blank=True)
    
    # dont remove this, it's this url that all facebook likes
    # for a profile are tied to 
    temporary_profile_url = models.CharField(editable=False,
                                             unique=True,
                                             max_length=36)

    # select phone number to display on profile
    DISPLAY_NUMBER_CHOICES = (
        (True, 'Personligt telefonnummer'),
        (False, 'Salongens telefonnummer'),
        )
    number_on_profile = models.BooleanField(
        "Vilket telefonnummer ska visas på profilen?",
        max_length=1,
        default=False,
        choices=DISPLAY_NUMBER_CHOICES)

    personal_phone_number = models.CharField("Personligt telefonnummer",
                                             max_length=30,
                                             blank=True,
                                             null=True)

    # salong
    salon_phone_number = models.CharField("Salongens telefonnummer",
                                          max_length=30,
                                          blank=True,
                                          null=True)
    salon_name = models.CharField("Salongens namn",
                                  max_length=30,
                                  blank=True)
    salon_city = models.CharField("Stad",
                                  max_length=30,
                                  blank=True)
    salon_url = models.URLField("Salongens hemsida",
                                blank=True)
    salon_adress = models.CharField("Salongens adress",
                                    max_length=30,
                                    blank=True)

    zip_adress = models.CharField("Postnummer",
                                  max_length=20,
                                  blank=True,
                                  null=True)

    url_online_booking = models.URLField("Adress till online bokningssystem",
                                         blank=True)
    show_booking_url = models.BooleanField("Min salong har online-bokning",
                                           blank=True)

    # on_delete=models.SET_NULL, since we dont want to delete UserProfile
    # when profile_image is deleted
    profile_image_cropped = models.ForeignKey(ProfileImage,
                                              unique=True,
                                              editable=False,
                                              null=True,
                                              blank=True,
                                              on_delete=models.SET_NULL,
                                              related_name='profile_image_cropped')
    profile_image_uncropped = models.ForeignKey(ProfileImage,
                                                unique=True,
                                                editable=False,
                                                null=True,
                                                blank=True,
                                                on_delete=models.SET_NULL,
                                                related_name='profile_image_uncropped')
    visible = models.BooleanField(
        "Visa i sökresultat och visa användarens bilder", default=False)
    visible_message_read = models.BooleanField(default=False)
    
    # when this field is True, the profile have all information a complete profile should have.
    # approved == 'approved by the system, to be in search results - need human approving tho
    # to be displayed in search results'.
    approved = models.BooleanField("Profilen är komplett", default=False)
    approved_message_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # remove accidental whitespaces from city
        self.salon_city = self.salon_city.strip()

        # check if the user is still valid
        dirties = self.get_dirty_fields()
        user_criterias = [
                'salon_city',
                'salon_adress',
                'zip_adress',
                'salon_phone_number',
                'openhours',
                'profile_text',
                ]
        for key in dirties.keys():
            if key in user_criterias:
                approved_user_criteria_changed.send(sender=self)
                break

        return super(UserProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s %s, %s' % (self.user.first_name,
                               self.user.last_name,
                               self.salon_city)


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
post_delete.connect(delete_filefield, ProfileImage)
post_delete.connect(delete_filefield, GalleryImage)


class InviteCode(models.Model):
    """
    NOTE: Keep the ``used`` boolean, because if the reciever gets
    deleted, there is no other way to know if the code has been
    used or not.

    """
    used = models.BooleanField("Have the invite code been used?",
                               default=False)
    invite_code = models.CharField("The string to use as invite code",
                                   max_length=30)
    comment = models.CharField("To who was the invitecode given? And so on..",
                               max_length=500,
                               null=True,
                               blank=True)
    inviter = models.ForeignKey(User, related_name='invitecode_inviter',
                                null=True,
                                blank=True)
    reciever = models.ForeignKey(User, related_name='invitecode_reciever',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)

    def __unicode__(self):
        if self.inviter is None:
            inviter = "-"
        else:
            inviter = "%s %s, %s" % (
                 self.inviter.first_name, self.inviter.last_name,
                 self.inviter.userprofile.salon_city,
                    )
        if self.reciever is None:
            reciever = "-"
        else:
            reciever = "%s %s, %s" % (
                self.reciever.first_name, self.reciever.last_name,
                self.reciever.userprofile.salon_city,
                    )
        return u'(%s) - %s invited %s - %s' % (
                self.invite_code, inviter, reciever, self.comment
                )


class Featured(models.Model):
    user = models.ForeignKey(UserProfile, null=False, blank=False)
    city = models.CharField("City", max_length=30, null=False, blank=False)

    def __unicode__(self):
        return "%s %s in %s" % (self.user.user.first_name,
                                self.user.user.last_name,
                                self.city)

    class Meta:
        unique_together = ('user', 'city')
        verbose_name_plural = "Featured profiles"


class ScheduledCheck(models.Model):
    """
    A model for accounts that has been approved, but no longer
    matches the criterias for being approved. A scheduled (cron)
    command will send out email for these accounts.

    """
    user = models.ForeignKey(User, null=False, blank=False, unique=True)
    notification_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.__unicode__()
