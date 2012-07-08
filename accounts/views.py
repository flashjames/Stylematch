#-*- coding:utf-8 -*-
import os
import StringIO
from PIL import Image
from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import Http404
from django.utils.translation import ugettext as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView,
                                  UpdateView,
                                  DetailView,
                                  RedirectView,
                                  CreateView,
                                  FormView)
from braces.views import LoginRequiredMixin
from accounts.models import (Service,
                             UserProfile,
                             OpenHours,
                             GalleryImage,
                             ProfileImage,
                             weekdays_model)
from tools import (format_minutes_to_hhmm,
                   format_minutes_to_pretty_format,
                   get_unique_filename)
from accounts.forms import (UserProfileForm,
                            ServiceForm,
                            GalleryImageForm,
                            ProfileImageForm,
                            CropCoordsForm)


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

    def get_profile_image_url(self):
        profile_picture = ''
        try:
            profile_picture = self.get_profile_image(self.object.user)
        except:
            if self.is_authenticated and self.object.user == self.request.user:
                profile_picture = os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_logged_in.jpg')
            else:
                profile_picture = os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_not_logged_in.jpg')

        return profile_picture

    def get_gallery_images(self, limit=0):
        """
        TODO: should have limit on number of imgs to display
        """
        queryset = GalleryImage.objects.filter(
            user__exact=self.object.user).filter(display_on_profile=True)

        # if no gallery images uploaded, display a default image
        if not queryset:
            if self.is_authenticated and self.object.user == self.request.user:
                return []
            queryset = [os.path.join(
                        settings.STATIC_URL,
                        'img/default_image_profile_not_logged_in.jpg')]
        return queryset
    
    def get_profile_image(self, user):
        userprofile = user.userprofile

        # display cropped profile image if there's any
        if userprofile.profile_image_cropped:
            profile_image = userprofile.profile_image_cropped
        else:
            profile_image = userprofile.profile_image_uncropped

        return self.get_image_url(profile_image)

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

    def get_openinghours(self, obj):

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

        # used to only display edit-profile menu, if at the user's profile
        context['logged_in_user_profile'] = self.request.user == self.object.user

        context['site_domain'] = settings.SITE_DOMAIN

        # get images displayed on profile
        context['profile_image'] = self.get_profile_image_url()
        context['gallery_images'] = self.get_gallery_images()

        # services the displayed userprofile have
        context['services'] = Service.objects.filter(
                                    user=self.object.user).filter(
                                    display_on_profile=True)

        for i in context['services']:
            i.length = format_minutes_to_pretty_format(i.length)

        context['first_name'] = self.object.user.first_name
        context['last_name'] = self.object.user.last_name

        # opening hours the displayed userprofile have
        try:
            obj = OpenHours.objects.get(user=self.object.user)
            context['openhours_reviewed'] = obj.reviewed
            context['weekdays'] = self.get_openinghours(obj)
        except:
            pass

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


class RedirectToProfileView(LoginRequiredMixin, RedirectView):
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
        return self.request.user.userprofile.profile_url

    def get_user_temporary_profile_url(self):
        return self.request.user.userprofile.temporary_profile_url


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Edit a stylist profile
    """
    model = UserProfile
    template_name = "profiles/profile_edit.html"
    form_class = UserProfileForm

    def form_valid(self, form):
        """
        Needs to be overridden because regular form_valid returns
        a HttpRedirectResponse() which cannot take context data
        """
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))

    def form_invalid(self, form):
        """
        Passes 'invalid' context variable
        """
        return self.render_to_response(self.get_context_data(form=form,
                                                             invalid=True))

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        Added request object to be sent to the form class
        """
        return form_class(self.request, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def get_context_data(self, **kwargs):
        context = super(EditProfileView, self).get_context_data(**kwargs)
        context['update_success'] = "Uppdateringen lyckades!"
        context['update_failure'] = ("Oops! Något gick fel. Kontrollera att "
                                     "alla fält är korrekt ifyllda.")
        return context


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


class OpenHoursView(LoginRequiredMixin, UpdateView):
    model = OpenHours
    template_name = "accounts/hours_form.html"

    def form_valid(self, form):
        """
        Passes 'valid' context variable
        """
        if not self.object.reviewed:
            self.object.reviewed = True
            self.object.save()
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))

    def get_success_url(self):
        return reverse('profiles_add_hours')

    def get_object(self, queryset=None):
        obj = OpenHours.objects.get(user__exact=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(OpenHoursView, self).get_context_data(**kwargs)
        context['update_success'] = "Uppdateringen lyckades!"
        context['update_failure'] = ("Oops! Något gick fel. Kontrollera att "
                                     "alla fält är korrekt ifyllda.")
        return context


class EditImagesView(LoginRequiredMixin, CreateView):
    """
    Display edit images page
    The view handle upload of GalleryImage, but not upload of ProfileImage
    even if ProfileImage is displayed on this page.
    Many javascript dependencies one this page which interacts with the
    REST API specified in class PictureResource
    """
    template_name = "accounts/edit_images.html"
    form_class = GalleryImageForm

    def get_success_url(self):
        return reverse('edit_images')

    def form_invalid(self, form):
        """
        Passes 'invalid' context variable
        """
        return self.render_to_response(self.get_context_data(form=form,
                                                             invalid=True))

    def get_form(self, form_class):
        form = super(EditImagesView, self).get_form(form_class)
        form.instance.user = self.request.user
        return form

    def get_context_data(self, **kwargs):
        context = super(EditImagesView, self).get_context_data(**kwargs)
        context['profile'] = self.request.user.userprofile

        context['crop_coords_form'] = CropCoordsForm()

        context['update_success'] = "Uppladdningen lyckades!"
        try:
            context['update_failure'] = kwargs['form']._errors['file']
        except:
            context['update_failure'] = ""

        return context

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
            # fileposition indicator needs to be set to beginning of file
            # else the saved file will be corrupt
            original_image.seek(0)
            return original_image

        # Resize image but keep aspect ratio
        image.thumbnail((max_width, max_height), Image.ANTIALIAS)

        # Return resized image as InMemoryUploadedFile
        tempfile_io = StringIO.StringIO()
        image.save(tempfile_io, format=file_extension)

        # fileposition indicator needs to be set to beginning of file
        # else the saved file will be corrupt
        tempfile_io.seek(0)
        return InMemoryUploadedFile(tempfile_io, None, original_image._name,
                                    original_image.content_type,
                                    tempfile_io.len, None)

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        image = self.request.FILES.get('file')
        filename = get_unique_filename(image.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)

        # replace original image, with a resized version
        self.object.file._file = self.resize_image(image)

        self.object.user = self.request.user
        self.object.filename = filename

        self.object.save()
        form.save_m2m()
        
        # Can't user super().form_valid(**kwargs) since form_valid returns
        # a HttpRedirectResponse() which cannot take context data
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))

class SaveProfileImageView(EditImagesView):
    form_class = ProfileImageForm

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        image = self.request.FILES.get('file')
        filename = get_unique_filename(image.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)
          
        # replace original image, with a resized version
        self.object.file._file = self.resize_image(image)
        
        self.object.user = self.request.user
        self.object.filename = filename

        self.object.save()
        form.save_m2m()

        current_userprofile = self.request.user.userprofile
        # remove old uncropped profile image
        if current_userprofile.profile_image_uncropped:
            current_userprofile.profile_image_uncropped.delete()
        
        # update UserProfile foreign key, to point at new uncropped profile image
        current_userprofile.profile_image_uncropped = self.object
        current_userprofile.save()
        
        # Can't user super().form_valid(**kwargs) since form_valid returns
        # a HttpRedirectResponse() which cannot take context data
        return self.render_to_response(self.get_context_data(form=form,
                                                             valid=True))


class SaveProfileImageView(EditImagesView):
    """
    Saves the supplied image as Uncropped Profile Image and deletes
    old Uncropped Profile image.
    """
    form_class = ProfileImageForm

    def get_success_url(self):
        return reverse('crop_image')

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        image = self.request.FILES.get('file')
        filename = get_unique_filename(image.name)

        current_userprofile = self.request.user.userprofile

        # remove old uncropped profile image
        if current_userprofile.profile_image_uncropped:
            # for explanation why this is here, check same if case
            # in CropPictureView
            if (current_userprofile.profile_image_cropped !=
                current_userprofile.profile_image_uncropped):

                current_userprofile.profile_image_uncropped.delete()

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)

        # replace original image, with a resized version
        self.object.file._file = self.resize_image(image)

        self.object.user = self.request.user
        self.object.filename = filename

        self.object.save()
        form.save_m2m()

        # update UserProfile foreign key,
        # to point at new uncropped profile image
        current_userprofile.profile_image_uncropped = self.object
        current_userprofile.save()

        return HttpResponseRedirect(self.get_success_url())


class CropPictureView(LoginRequiredMixin, FormView):
    """
    Crops the file referenced at profile_image_uncropped with user supplied
    coordinates and saves it to filesystem.
    This file becomes the new profile_image_cropped.

    TODO: The operation crop -> save to filesystem/database, is probably
    very inefficient.
    Since it converts from PIL.Image -> StringIO
    -> ContentFile and then default_storage.save() probably does some stuff.
    """
    form_class = CropCoordsForm
    template_name = "accounts/crop_image.html"

    def get_success_url(self):
        return reverse('profile_display_redirect')

    def crop(self, original_image, image_filename, start_x_coordinate,
             start_y_coordinate, width, height):
        """
        Returns cropped image.
        The image is cropped with the supplied coordinates
        """
        import imghdr
        file_extension = imghdr.what("", original_image.read(2048))
        original_image.seek(0)

        image = Image.open(original_image)
        image = image.crop((start_x_coordinate,
                            start_y_coordinate,
                            start_x_coordinate + width,
                            start_y_coordinate + height))

        # Return cropped image as ContentFile
        tempfile_io = StringIO.StringIO()
        image.save(tempfile_io, format=file_extension)

        tempfile_io.seek(0)

        return ContentFile(tempfile_io.read())

    def get_context_data(self, **kwargs):
        context = super(CropPictureView, self).get_context_data(**kwargs)
        current_userprofile = self.request.user.userprofile
        context['profile_image_uncropped'] = (
            current_userprofile.profile_image_uncropped)
        return context

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        current_userprofile = self.request.user.userprofile

        if not current_userprofile.profile_image_uncropped:
            raise ObjectDoesNotExist("No uncropped profile image found")

        image_uncropped = current_userprofile.profile_image_uncropped.file

        #import pdb;pdb.set_trace()
        image = default_storage.open(image_uncropped.name)
        filename = get_unique_filename(image.name)

        start_x_coordinate = form.cleaned_data['start_x_coordinate']
        start_y_coordinate = form.cleaned_data['start_y_coordinate']
        width = form.cleaned_data['width']
        height = form.cleaned_data['height']

        cropped_image = self.crop(image,
                  filename,
                  start_x_coordinate,
                  start_y_coordinate,
                  width,
                  height)
        
        # remove old cropped profile image
        if current_userprofile.profile_image_cropped:
            """
            When we added the possibiltiy to crop images,
            we added a profile_image_cropped and profile_image_uncropped
            foreign key reference to the cropped and uncropped image.
            When we did the data migration, we set profile_image_cropped and
            profile_image_uncropped to point at the uncropped ProfileImage object,
            so all users that havent uploaded a new image and cropped it have this
            right now.

            -> Dont delete the 'old' cropped_profile_image, which in the reality isnt cropped.
            If we delete profile_image_cropped, we'll get a database error since
            profile_image_uncropped foreign key now will point at a deleted object

            This if-case can be removed when all users have a cropped profile image!
            Dont forget to remove same if-case in SaveProfileImageView.
            """
            if (current_userprofile.profile_image_cropped !=
                current_userprofile.profile_image_uncropped):
                current_userprofile.profile_image_cropped.delete()

        # save the cropped image
        picture = ProfileImage(filename=filename,
                          user=self.request.user, cropped=True)
        picture.file.save(filename, cropped_image, True)
        picture.save()

        # update UserProfile foreign key,
        # to point at new cropped profile image
        current_userprofile.profile_image_cropped = picture
        current_userprofile.save()

        return HttpResponseRedirect(self.get_success_url())
