#-*- coding:utf-8 -*-
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DetailView, RedirectView
from accounts.models import Service, UserProfile, OpenHours
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from django.forms import ModelForm, ValidationError
from tastypie.validation import FormValidation
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from django.contrib.auth.models import User

from tools import *



class DisplayProfileView(DetailView):
    """
    Display a stylist profile
    """
    template_name = "profiles/profile_display.html"
    model = UserProfile
    
    # case insensitive since __iexact
    slug_field = "profile_url__iexact"
    context_object_name = "profile"


    def weekday_factory(self, obj, day = 'mon', pretty_dayname = 'Måndag'):

        """ 
        Helper function to create a list with relevant day information.
        Extracts values from obj with attribute prefix DAY
        """

        attr_name = day
        open_time = format_minutes_to_hhmm(getattr(obj, attr_name))

        attr_name = day + "_closed"
        closed_time = format_minutes_to_hhmm(getattr(obj, attr_name))


        attr_name = day + "_lunch"
        lunch_start = format_minutes_to_hhmm(getattr(obj, attr_name))


        attr_name = day + "_lunch_closed"
        lunch_end = format_minutes_to_hhmm(getattr(obj, attr_name))

        day = [pretty_dayname, open_time, closed_time, lunch_start, lunch_end]        
        return day

    def get_context_data(self, **kwargs):
        context = super(DisplayProfileView, self).get_context_data(**kwargs)


        obj = OpenHours.objects.get(user__exact=self.request.user.id)

        # Important: first value in every tuple must be exactly same as in OpenHours model.        
        weekday_list =  [('mon', 'Måndag'), ('tues', 'Tisdag'), ('wed', 'Onsdag'), 
                         ('thurs', 'Torsdag'), ('fri', 'Fredag'), ('sat', 'Lördag'),
                         ('sun', 'Söndag')
                        ]
    
        context['weekdays'] = []
        for day in weekday_list:
            day_dict = self.weekday_factory(obj, day[0], day[1])
            context['weekdays'].append(day_dict)
        
        
        return context


   

class CurrentUserProfileView(DisplayProfileView):
    slug_field = "temporary_profile_url__exact"

class RedirectToProfileView(RedirectView):
    """
    Redirect to the profile with the profile_url or if it's not set,
    with temporary_profile_url
    """
    
    # if this is set to True, browsers will cache the redirect for ever
    # which is no good (breaks the way we display the profile)
    permanent = False
    
    def get_redirect_url(self):
        profile_url = self.get_user_profile_url()

        # if user havent set a profile_url, use the temporary_profile_url which is a uuid string
        if not profile_url:
            temporary_profile_url = self.get_user_temporary_profile_url()
            return reverse('profile_display_without_profile_url', kwargs={'slug': temporary_profile_url})

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

    def is_unique_url_name(self, profile_url):
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

    # check if the url is unique ie. it's not in use
    def clean_profile_url(self):
        data = self.cleaned_data['profile_url']
        if not self.is_unique_url_name(data):
            raise ValidationError("Den här sökvägen är redan tagen")
        return data

    class Meta:
        model = UserProfile

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
        return {'form': ServiceForm(auto_id=True)}

class ServiceFormAPI(ModelForm):
    class Meta:
        model = Service
        exclude = ('order')

class PerUserAuthorization(Authorization):
    """
    Only show objects that's related to the user
    http://stackoverflow.com/questions/7015638/django-and-backbone-js-questions
    """
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated():
                object_list = object_list.filter(user=request.user)
                return object_list

            return object_list.none()

class DjangoBasicAuthentication(BasicAuthentication):
    """
    First check session data if user is logged in, with the Django authentication.
    If it doesn't find it, fall back to http auth.
    http://stackoverflow.com/questions/7363460
    /how-do-i-check-that-user-already-authenticated-from-tastypie
    """
    def __init__(self, *args, **kwargs):
        super(DjangoBasicAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return True
        return super(DjangoBasicAuthentication, self).is_authenticated(request, **kwargs)



class ServiceResource(ModelResource):

    # TODO: Better way to set user field to current user
    # than having whole function here
    # Possible solution https://github.com/toastdriven/django-tastypie/pull/214
    # but doesnt seem to implemented in our tastypie version
    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        # CHANGED: Add current user to user field
        bundle.obj.user = request.user

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    class Meta:
        model = Service
        pass_request_user_to_django = True
        authentication = DjangoBasicAuthentication()
        authorization = PerUserAuthorization()
        queryset = Service.objects.all()
        limit = 50
        max_limit = 0
        validation = FormValidation(form_class=ServiceFormAPI)



class OpenHoursView(UpdateView):
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

