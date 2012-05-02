#-*- coding:utf-8 -*-
from django.views.generic import TemplateView, UpdateView, DetailView, RedirectView, CreateView
from accounts.models import Service, UserProfile, OpenHours, Picture, InviteCode

from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from django.forms import ModelForm, ValidationError, Textarea
from django.conf import settings
import uuid, os, imp, re

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from accounts.models import weekdays_model

# TODO: import those that are used?
from tools import *


from registration.forms import RegistrationForm

from django.contrib.auth import login
from registration.signals import user_registered

from django import forms

# TODO: We should discuss a better structure for signals....
# Store in another file?
def user_created(sender, user, request, **kwargs):
    # Automatically login a user who was just created
    # This probably makes them more keen on proceeding the signup form.
    user.backend='django.contrib.auth.backends.ModelBackend'
    login(request, user)

    # set is_active = True, must be set and saved to DB after login function is called.
    userObject = User.objects.get(username = user)
    userObject.is_active = True
    userObject.save()

user_registered.connect(user_created)

class UserRegistrationForm(RegistrationForm):
    email = forms.CharField(required = False)
    first_name = forms.CharField(label = "Förnamn")
    last_name = forms.CharField(label = "Efternamn")
    invite_code = forms.CharField(label = "Inbjudningskod (just nu behövs en inbjudan för att gå med)")

    username = forms.EmailField(max_length=64, label = "Emailadress")

    def clean_email(self):
        """
        Since its actually not the email field but the username
        presented on form we use username as email too.
        """
        email = ""
        try:
            email = self.cleaned_data['username']
        except:
            email = ""

        return email

    def clean_invite_code(self):
        """
        Validates that the user have supplied a valid invite code.
        And marks the code as used, if the other fields are correctly filled.
        """
        supplied_invite_code = self.cleaned_data['invite_code']
        queryset = InviteCode.objects.filter(invite_code__iexact=supplied_invite_code).filter(used=False)

        # a permanent key which can be used by us
        if supplied_invite_code == "permanent1":
            return supplied_invite_code
        
        # check that the invite_code exists
        invite_code = queryset[:1]
        if not invite_code:
            raise forms.ValidationError(u'Din inbjudningskod (\'%s\') var felaktig. Vänligen kontrollera att du skrev rätt.' % supplied_invite_code)

        # only set the invite code to used=True if all other fields have
        # validated correctly
        # TODO: this is run even if the passwords doesnt match in the clean() method. since this function is run before clean()
        if self.is_valid():
            invite_code = invite_code[0]
            invite_code.used=True
            invite_code.save()
        
        return supplied_invite_code

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))

        MIN_LENGTH = 6
        if len(self.cleaned_data['password1']) < MIN_LENGTH:
            raise forms.ValidationError("Lösenordet är för kort, det ska innehålla minst 6 tecken.")
        return self.cleaned_data

    class Meta:
        exclude = ('email',)

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
            profile_picture  = self.get_profile_image(profile_user_id)[0]
        except:
            if self.is_authenticated:
                profile_picture = os.path.join(settings.STATIC_URL, 'img/default_image_profile_logged_in.jpg')
            else:
                profile_picture = os.path.join(settings.STATIC_URL, 'img/default_image_profile_not_logged_in.jpg')

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
            images = [os.path.join(settings.STATIC_URL, 'img/default_image_profile_not_logged_in.jpg')]

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


    def weekday_factory(self, obj, day = 'mon', pretty_dayname = 'Måndag'):
        """
        Helper function to create a dict with relevant day information.
        Extracts values from obj with attribute prefix DAY
        """

        attr_name = day
        open_time = self.get_opening_time(obj, attr_name)

        attr_name = day + "_closed"
        closed_time = self.get_opening_time(obj,attr_name)

        attr_name = day + "_lunch"
        lunch_start = self.get_opening_time(obj,attr_name)

        attr_name = day + "_lunch_closed"
        lunch_end = self.get_opening_time(obj,attr_name)

        day = {'day': pretty_dayname, 'open': open_time, 'closed': closed_time, 'lunch_start': lunch_start, 'lunch_end': lunch_end}

        return day

    def get_openinghours(self, profile_user_id):

        obj = OpenHours.objects.get(user__exact=profile_user_id)

        weekday_list =  ['Måndag',  'Tisdag', 'Onsdag', 'Torsdag', 'Fredag',
                        'Lördag', 'Söndag']

        openinghours_list =  []
        for index, day in enumerate(weekday_list):

            # Important:  weekdays_model[index] must be exactly same as in OpenHours model.
            # Should not be a problem now but this could be a future source of bugs.

            day_dict = self.weekday_factory(obj, weekdays_model[index], day)
            openinghours_list.append(day_dict)

        return openinghours_list

    def get_context_data(self, **kwargs):
        context = super(DisplayProfileView, self).get_context_data(**kwargs)
        
        # to display the parts associated to the profile,
        # we filter on the user_id of profile owner
        profile_user_id = context['profile'].user_id

        # get images displayed on profile
        context['profile_image'] = self.get_profile_image(profile_user_id)
        context['gallery_images'] = self.get_gallery_images(profile_user_id)

        # services the displayed userprofile have
        context['services'] = Service.objects.filter(user__exact=profile_user_id).filter(display_on_profile=True)

        for i in context['services']:
            i.length = format_minutes_to_pretty_format(i.length)


        # opening hours the displayed userprofile have
        context['weekdays'] = self.get_openinghours(profile_user_id)
        context['profile_image'] = self.get_profile_image_url(profile_user_id)


        return context

    def get_object(self, queryset=None):
        queryset = self.get_queryset()

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
        return obj

    def get(self, request, **kwargs):
        # used to check if user is authenticated, in get_profile_image_url()
        self.is_authenticated = request.user.is_authenticated()
        return super(DisplayProfileView, self).get(request, **kwargs)
        
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

        # if user havent set a profile_url, use the temporary_profile_url which is a uuid string
        if not profile_url:
            temporary_profile_url = self.get_user_temporary_profile_url()
            return reverse('profile_display_with_profile_url', kwargs={'slug': temporary_profile_url})

        return reverse('profile_display_with_profile_url', kwargs={'slug': profile_url})

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
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def is_systempath(self, profile_url):
        """
        Is the url used by the system, ie. defined in urls.py.
        It only matters under the root, since it's there the profiles will be.
        """
        # import python file with absolute path
        urls = imp.load_source('module.name', settings.PROJECT_DIR + "/urls.py")
        for urlpattern in urls.urlpatterns:
            # first part of the urlpattern as it will look to the user
            # ex. '^admin/asd$' -> 'admin'
            pattern = re.sub(r'[\^$]','',urlpattern.regex.pattern.split('/')[0])
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

        # is profile url ok?
        if not self.is_unique_url_name(data) or self.is_systempath(data):
            raise ValidationError("Den här sökvägen är redan tagen")
        return data

    class Meta:
        model = UserProfile
        widgets = {
            'profile_text': Textarea(attrs={'cols': 120, 'rows': 10}),
            }

class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Edit a stylist profile
    """
    model = UserProfile
    template_name = "profiles/profile_edit.html"
    form_class = UserProfileForm

    def __init__(self, *args, **kwargs):
        super(EditProfileView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('profile_edit')

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        Added request object to be sent to the form class
        """
        return form_class(self.request, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        obj = UserProfile.objects.get(user__exact=self.request.user.id)
        return obj

    def form_valid(self, form):
        f = form.save(commit=False)
        f.user = self.request.user
        f.save()
        form.save_m2m()
        return super(EditProfileView, self).form_valid(form)



class ServiceForm(ModelForm):
    class Meta:
        model = Service
        exclude = ('order')

class ServicesView(LoginRequiredMixin, TemplateView):
    """
    Display edit services page
    Many javascript dependencies one this page which interacts with the
    REST API specified in class ServiceResource
    """
    template_name = "accounts/service_form.html"

    def get_context_data(self, **kwargs):
        # auto_id = True  because Backbone.ModelBinding expects id's to be on the
        # form, id="name" not id="id_name"

        # "Initial"-dict defaults new services to show on profile.
        return {'form': ServiceForm(auto_id=True, initial={'display_on_profile': 1})}


class PicturesView1(LoginRequiredMixin, TemplateView):
    """
    Display edit pictures page
    Many javascript dependencies one this page which interacts with the
    REST API specified in class PictureResource
    """
    template_name = "accounts/profile_images_edit.html"

    def get_context_data(self, **kwargs):
        context = super(PicturesView, self).get_context_data(**kwargs)
        return context


class OpenHoursView(LoginRequiredMixin, UpdateView):
    model = OpenHours
    template_name = "accounts/hours_form.html"

    def __init__(self, *args, **kwargs):
        super(OpenHoursView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('profile_display_redirect')

    def get_object(self, queryset=None):
        obj = OpenHours.objects.get(user__exact=self.request.user.id)
        return obj



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
                raise ValidationError("Bilden är för stor ( > %s )" % convert_bytes(settings.MAX_IMAGE_SIZE))
            return file
        else:
            raise ValidationError("Filen kunde inte läsas")

    class Meta:
        model = Picture
        fields = ('file',)

class PicturesView(LoginRequiredMixin, CreateView):
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

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('profiles_edit_images')


    def get_form(self, form_class):
        form = super(PicturesView, self).get_form(form_class)
        form.instance.user = self.request.user
        return form

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):

        f = self.request.FILES.get('file')

        filename=get_unique_filename(f.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.filename = filename

        # default image type, Gallery
        self.object.image_type = 'G'
        self.object.save()
        form.save_m2m()
        return super(PicturesView, self).form_valid(form)

