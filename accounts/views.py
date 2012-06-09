#-*- coding:utf-8 -*-
import uuid
import os
import imp
import re
from django import forms
from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError, Textarea
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic import (TemplateView,
                                  UpdateView,
                                  DetailView,
                                  RedirectView,
                                  CreateView)
from braces.views import LoginRequiredMixin
from accounts.models import (Service,
                             UserProfile,
                             OpenHours,
                             Picture,
                             weekdays_model)
from tools import format_minutes_to_hhmm, format_minutes_to_pretty_format


class DisplayProfileView(DetailView):
    """
    Display a stylist profile
    """
    template_name = "profiles/profile_display.html"
    model = UserProfile

    # case insensitive since __iexact
    slug_field = "profile_url__iexact"
    context_object_name = "profile"

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_images(self, queryset):
        """
        Send back urls to the images, instead of Picture objects
        """
        images_lst = []
        for index, image in enumerate(queryset):
            images_lst.append(self.get_image_url(image))

        return images_lst

    def get_profile_image_url(self, profile_user_id):
        profile_picture = ''
        try:
            profile_picture = self.get_profile_image(profile_user_id)[0]
        except:
            if self.is_authenticated:
                profile_picture = os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_logged_in.jpg')
            else:
                profile_picture = os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_not_logged_in.jpg')

        return profile_picture

    def get_gallery_images(self, user, limit=0):
        """
        TODO: should have limit on number of imgs to display
        'G' = gallery images
        """
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='G').filter(display_on_profile=True)

        images = self.get_images(queryset)

        # if no gallery images uploaded, display a default image
        if not images:
            images = [os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_not_logged_in.jpg')]
        return images

    def get_profile_image(self, user):
        # 'C' = current profile image
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='C')

        return self.get_images(queryset)

    def get_opening_time(self, obj, attr_name):
        """
        Helper function for opening hours.
        If no time has been selected in the dropdown, -1 will be  the value.
        This is then used in template to print "CLOSED".
        """
        time = format_minutes_to_hhmm(getattr(obj, attr_name))
        if time == '':
            time = -1

        return time

    def weekday_factory(self, obj, day='mon', pretty_dayname='Måndag'):
        """
        Helper function to create a dict with relevant day information.
        Extracts values from obj with attribute prefix DAY
        """

        attr_name = day
        open_time = self.get_opening_time(obj, attr_name)

        attr_name = day + "_closed"
        closed_time = self.get_opening_time(obj, attr_name)

        day = {'day': pretty_dayname, 'open': open_time, 'closed': closed_time}

        return day

    def get_openinghours(self, profile_user_id):

        obj = OpenHours.objects.get(user__exact=profile_user_id)

        weekday_list = ['Måndag',
                        'Tisdag',
                        'Onsdag',
                        'Torsdag',
                        'Fredag',
                        'Lördag',
                        'Söndag']

        openinghours_list = []
        for index, day in enumerate(weekday_list):

            # Important:  weekdays_model[index] must be exactly same as in
            # OpenHours model. Should not be a problem now but this could be
            # a future source of bugs.

            day_dict = self.weekday_factory(obj, weekdays_model[index], day)
            openinghours_list.append(day_dict)
        return openinghours_list

    def get_context_data(self, **kwargs):
        context = super(DisplayProfileView, self).get_context_data(**kwargs)

        # to display the parts associated to the profile,
        # we filter on the user_id of profile owner
        profile_user_id = context['profile'].user_id

        # used to only display edit-profile menu, if at the user's profile
        current_user_id = self.request.user.id
        context['logged_in_user_profile'] = False
        if current_user_id == profile_user_id:
            context['logged_in_user_profile'] = True

        context['site_domain'] = settings.SITE_DOMAIN

        # get images displayed on profile
        context['profile_image'] = self.get_profile_image(profile_user_id)
        context['gallery_images'] = self.get_gallery_images(profile_user_id)

        # services the displayed userprofile have
        context['services'] = Service.objects.filter(
                                    user__exact=profile_user_id).filter(
                                    display_on_profile=True)

        for i in context['services']:
            i.length = format_minutes_to_pretty_format(i.length)

        profile_user = User.objects.filter(id__exact=profile_user_id)[0]
        context['first_name'] = profile_user.first_name
        context['last_name'] = profile_user.last_name

        # opening hours the displayed userprofile have
        context['weekdays'] = self.get_openinghours(profile_user_id)
        context['profile_image'] = self.get_profile_image_url(profile_user_id)

        return context

    def get_object(self, queryset=None):
        """
        Find the profile to display according to the slug field.
        """
        queryset = self.get_queryset()

        # used in the "get()" function, to determine if to redirect
        # to profile_url. in case there exists a profile_url and user
        # came from a temporary_profile_url
        self.redirect_to_profile_url = False

        # try find the profile with profile_url, which is a name
        slug = self.kwargs.get('slug', None)
        if slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

            # try find the profile, with a temporary profile url
            try:
                obj = queryset.get()
            except ObjectDoesNotExist:
                queryset = self.get_queryset()
                slug_field = "temporary_profile_url__exact"
                queryset = queryset.filter(**{slug_field: slug})
            else:
                return obj

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        else:
            # redirect to profile_url, if a profile_url exists
            if obj.profile_url:
                self.redirect_to_profile_url = True
        return obj

    def get(self, request, **kwargs):
        # used to check if user is authenticated, in get_profile_image_url()
        self.is_authenticated = request.user.is_authenticated()
        self.object = self.get_object()

        # redirect to profile_url
        if self.redirect_to_profile_url:
            return http.HttpResponseRedirect('/' + self.object.profile_url)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


class CreateSelfView(CreateView):
    """
    A createview that redirects to self and passes valid/invalid variables
    """
    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             invalid=True))


class UpdateSelfView(UpdateView):
    """
    An updateview that redirects to self and passes valid/invalid variables
    """
    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             invalid=True))


class RedirectToProfileView(RedirectView):
    """
    Redirects to the logged in user's profile with the profile_url
    or if it's not set, with temporary_profile_url.
    """

    # if this is set to True, browsers will cache the redirect for ever
    # which is no good (breaks the way we display the profile)
    permanent = False

    def get_redirect_url(self):
        profile_url = self.get_user_profile_url()

        # if user havent set a profile_url, use the temporary_profile_url
        # which is a uuid string
        if not profile_url:
            temporary_profile_url = self.get_user_temporary_profile_url()
            return reverse('profile_display_with_profile_url',
                           kwargs={'slug': temporary_profile_url})

        return reverse('profile_display_with_profile_url',
                       kwargs={'slug': profile_url})

    def get_user_profile_url(self):
        query = UserProfile.objects.filter(user=self.request.user).get()
        return query.profile_url

    def get_user_temporary_profile_url(self):
        query = UserProfile.objects.filter(user=self.request.user).get()
        return query.temporary_profile_url


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
        #import pdb;pdb.set_trace()
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
        """
        Check if the url is unique ie. it's not in use
        """
        data = self.cleaned_data['profile_url']

        # reverse() can't find url's with - (bindestreck) in it
        # TODO: Fix reverse() so user's can use - in their profile_url
        if '-' in data:
            raise ValidationError("Sökvägen får inte innehålla - "
                                  "(bindestreck)")

        # is profile url used by another user or a path used by django?
        if not self.is_unique_url_name(data) or self.is_systempath(data):
            raise ValidationError("Den här sökvägen är redan tagen")
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
        widgets = {
            'profile_text': Textarea(attrs={'cols': 120, 'rows': 10}),
            }


class EditProfileView(LoginRequiredMixin, UpdateSelfView):
    """
    Edit a stylist profile
    """
    model = UserProfile
    template_name = "profiles/profile_edit.html"
    form_class = UserProfileForm

    def __init__(self, *args, **kwargs):
        super(EditProfileView, self).__init__(*args, **kwargs)

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        Added request object to be sent to the form class
        """
        return form_class(self.request, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        obj = UserProfile.objects.get(user__exact=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(EditProfileView, self).get_context_data(**kwargs)
        context['update_success'] = "Uppdateringen lyckades!"
        context['update_failure'] = ("Oops! Något gick fel. Kontrollera att "
                                     "alla fält är korrekt ifyllda.")
        return context


class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ('name',
                  'description',
                  'length',
                  'price',
                  'display_on_profile')
        exclude = ('order')


class ServicesView(LoginRequiredMixin, TemplateView):
    """
    Display edit services page
    Many javascript dependencies one this page which interacts with the
    REST API specified in class ServiceResource
    """
    template_name = "accounts/service_form.html"

    def get_context_data(self, **kwargs):
        # auto_id = True  because Backbone.ModelBinding expects id's to be on
        # the form, id="name" not id="id_name"

        # "Initial"-dict defaults new services to show on profile.
        return {'form': ServiceForm(auto_id=True,
                                    initial={'display_on_profile': 1}
                                    )}


class OpenHoursView(LoginRequiredMixin, UpdateSelfView):
    model = OpenHours
    template_name = "accounts/hours_form.html"

    def __init__(self, *args, **kwargs):
        super(OpenHoursView, self).__init__(*args, **kwargs)

    def get_object(self, queryset=None):
        obj = OpenHours.objects.get(user__exact=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(OpenHoursView, self).get_context_data(**kwargs)
        context['update_success'] = "Uppdateringen lyckades!"
        context['update_failure'] = ("Oops! Något gick fel. Kontrollera att "
                                     "alla fält är korrekt ifyllda.")
        return context

"""
TODO: Put rest of this file, in another file?
Since all classes/functions is part of the same functionality
"""
import StringIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def get_unique_filename(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename


def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2iT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2iG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.1fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.iKB' % kilobytes
    else:
        size = '%.iB' % bytes
    return size


class PictureForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data['file']

        if file:
            if file._size > settings.MAX_IMAGE_SIZE:
                raise ValidationError("Bilden är för stor ( > %s )"
                                    % convert_bytes(settings.MAX_IMAGE_SIZE))
            if not file._name.endswith(('.jpg', '.gif', '.png')):
                raise ValidationError("Endast bildfiler i formaten "
                                      "PNG, JPG och GIF är accepterade.")

            return file
        else:
            raise ValidationError("Filen kunde inte läsas")

    class Meta:
        model = Picture
        fields = ('file', 'comment', 'image_type')


class PicturesView(LoginRequiredMixin, CreateSelfView):
    """
    Display edit pictures page
    Many javascript dependencies one this page which interacts with the
    REST API specified in class PictureResource
    """
    template_name = "accounts/profile_images_edit.html"
    model = Picture
    form_class = PictureForm

    def __init__(self, *args, **kwargs):
        super(PicturesView, self).__init__(*args, **kwargs)

    def get_form(self, form_class):
        form = super(PicturesView, self).get_form(form_class)
        form.instance.user = self.request.user
        return form

    def get_profile_image(self, user):
        # 'C' = current profile image
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='C')
        if queryset:
            profile_picture = queryset[0].get_image_url()
        else:
            profile_picture = os.path.join(
                                settings.STATIC_URL,
                                'img/default_image_profile_not_logged_in.jpg')

        return profile_picture

    def get_context_data(self, **kwargs):
        context = super(PicturesView, self).get_context_data(**kwargs)
        context['profile_image_url'] = self.get_profile_image(
                                                self.request.user.id
                                                )
        context['update_success'] = "Uppladdningen lyckades!"
        try:
            context['update_failure'] = kwargs['form']._errors['file']
        except:
            context['update_failure'] = ""

        return context

    def remove_old_profile_image(self, user):
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='C')
        # old profile image found -> delete
        if queryset:
            queryset[0].delete()

    def resize_image(self, original_image):
        """
        Resize original_image, if it's larger than max_width/max_height.
        And return a InMemoryUploadedFile of the image.
        """
        file_extension = original_image.content_type.split("/")[1]

        image = Image.open(original_image)

        max_width = max_height = 720
        (width, height) = image.size

        # Dont resize image, if it's smaller than max_width/max_height
        if width < max_width and height < max_height:
            return

        # Resize image but keep aspect ratio
        image.thumbnail((max_width, max_height), Image.ANTIALIAS)

        # Return resized image as InMemoryUploadedFile
        tempfile_io = StringIO.StringIO()
        image.save(tempfile_io, format=file_extension)
        return InMemoryUploadedFile(tempfile_io, None, original_image._name,
                                    original_image.content_type,
                                    tempfile_io.len, None)

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        image_type = form.cleaned_data['image_type']

        # This class is used to upload both Gallery and Profile images ->
        # only remove old profile image if it's a profile image that have
        # been uploaded
        if image_type == 'C':
            self.remove_old_profile_image(self.request.user)

        f = self.request.FILES.get('file')
        filename = get_unique_filename(f.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)

        # replace original image, with a resized version
        resized_image = self.resize_image(f)

        # Will only resize image if it's larger than maximum size
        # -> dont replace original image if it havent been resized
        if resized_image:
            self.object.file._file = resized_image

        self.object.user = self.request.user
        self.object.filename = filename

        self.object.save()
        form.save_m2m()
        return super(PicturesView, self).form_valid(form)
