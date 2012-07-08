#-*- coding:utf-8 -*-
import imp
import re
from django import forms
from django.conf import settings
from accounts.models import (Service,
                             UserProfile,
                             GalleryImage,
                             ProfileImage)
from django.forms import ModelForm, ValidationError, Textarea
from django.utils.translation import ugettext as _


class UserProfileForm(ModelForm):
    """
    Validates that profile_url is unique
    """
    first_name = forms.CharField(label=_(u'Förnamn'),
                                 max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u'Efternamn'),
                                max_length=30,
                                required=False)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def is_systempath(self, profile_url):
        """
        Is the url used by the system, ie. defined in urls.py.
        It only matters under the root, since it's there the profiles will be.
        """
        # import python file with absolute path
        urls = imp.load_source('module.name',
                               settings.PROJECT_DIR + "/urls.py")
        for urlpattern in urls.urlpatterns:
            # first part of the urlpattern as it will look to the user
            # ex. '^admin/asd$' -> 'admin'
            pattern = re.sub(r'[\^$]',
                             '',
                             urlpattern.regex.pattern.split('/')[0])
            if pattern and pattern == profile_url:
                return True

        return False

    def is_unique_url_name(self, profile_url):
        """
        Is url used by another user?
        """
        # should be ok to not have any profile_url set
        if not profile_url:
            return True

        # find profiles that have the specific profile_url
        query = UserProfile.objects.filter(profile_url__iexact=profile_url)

        # the current profile shouldn't be in the result
        query = query.exclude(user=self.request.user)
        if query:
            return False

        return True

    def clean_profile_url(self):
        data = self.cleaned_data['profile_url']
        if data == "":
            raise ValidationError("Stylematch-adressen kan inte vara tom")
        if not re.match("^[A-Za-z0-9ÅÄÖåäö-]*$", data):
            raise ValidationError("Stylematch-adressen får endast innehålla:"
                                  "bokstäver, siffror och bindestreck (-)")

        # is profile url used by another user or a path used by django?
        if not self.is_unique_url_name(data) or self.is_systempath(data):
            raise ValidationError("Den här Stylematch-adressen är redan tagen")
        return data

    def strip_all_except_digits(self, number):
        """
        Removes all characters except digits
        """
        return re.sub("[^0-9]", "", number)

    def clean_personal_phone_number(self):
        number = self.cleaned_data.get('personal_phone_number')
        return self.strip_all_except_digits(number)

    def clean_salon_phone_number(self):
        number = self.cleaned_data.get('salon_phone_number')
        return self.strip_all_except_digits(number)

    def save(self, *args, **kw):
        # save the fields that dont belong to UserProfile object
        self.request.user.first_name = self.cleaned_data.get('first_name')
        self.request.user.last_name = self.cleaned_data.get('last_name')
        self.request.user.save()
        return super(UserProfileForm, self).save(*args, **kw)

    class Meta:
        model = UserProfile
        exclude = ('visible',)
        widgets = {
            'profile_text': Textarea(attrs={'cols': 120, 'rows': 10}),
            }

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ('name',
                  'description',
                  'length',
                  'price',
                  'display_on_profile')
        exclude = ('order')

class GalleryImageForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data['file']

        if file:
            if file._size > settings.MAX_IMAGE_SIZE:
                raise ValidationError("Bilden är för stor ( > %s )"
                                    % convert_bytes(settings.MAX_IMAGE_SIZE))
            filename = file._name.lower() 
            if not filename.endswith(('.jpg', '.gif', '.png')):
                raise ValidationError("Endast bildfiler i formaten "
                                      "PNG, JPG och GIF är accepterade.")

            return file
        else:
            raise ValidationError("Du måste välja en bild")

    class Meta:
        model = GalleryImage
        fields = ('file', 'comment')


class ProfileImageForm(GalleryImageForm):
    class Meta:
        model = ProfileImage
        fields = ('file',)


class CropCoordsForm(forms.Form):
    """
    Used to retrive coordinates to crop Uncropped profile image with
    """
    start_x_coordinate = forms.IntegerField(widget=forms.HiddenInput())
    start_y_coordinate = forms.IntegerField(widget=forms.HiddenInput())
    width = forms.IntegerField(widget=forms.HiddenInput())
    height = forms.IntegerField(widget=forms.HiddenInput())



