#-*- coding:utf-8 -*-
from django.views.generic import TemplateView, UpdateView, DetailView, RedirectView
from accounts.models import Service, UserProfile, OpenHours
from fileupload.models import Picture
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from django.forms import ModelForm, ValidationError, Textarea

from django.contrib.auth.models import User

from accounts.models import weekdays_model
# TODO: import those that are used?
from tools import *


from registration.forms import RegistrationForm
from registration.views import register
from django.contrib.auth import login
from registration.signals import user_registered


from django import forms


# TODO: We should discuss a better structure for signals....
# Store in another file?
def user_created(sender, user, request, **kwargs):

    # For future reasons we store the form data here
    # could do something fun with it.
    form = UserRegistrationForm(request.POST)

    # Force successfully created users to be activated since authorization
    # script requires this.
    userObject = User.objects.get(username = user)
    userObject.is_active = True
    userObject.save()

    # Automatically login a user who was just created
    # This probably makes them more keen on proceeding the signup form.
    user.backend='django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
user_registered.connect(user_created)



class UserRegistrationForm(RegistrationForm):    
    

    email = forms.CharField(required = False)
    first_name = forms.CharField(label = "Förnamn")   
    last_name = forms.CharField(label = "Efternamn")       
    invite_code = forms.CharField(label = "Inbjudningskod ('a' är giltig)")

    username = forms.EmailField(max_length=64, label = "Emailadress")
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        #self.fields['username'].label = "Användarnamn"
        #self.fields['email'].label = "Emailadress"
        self.fields['password1'].label = "Lösenord"
        self.fields['password2'].label = "Upprepa lösenord"

        required_str = "Detta fält krävs för registeringen."

        self.fields['username'].error_messages['invalid'] = "Skriv in en giltig e-mailadress."
        # Since __init__ is called after the creation of invite_code and other
        # extra fields, we can execute this loop and add our own error message
        # for required fields.
        for field in self.fields:
            self.fields[field].error_messages['required'] =  required_str


    def clean_email(self):
        # Since its actually not the email field but the username presented on form
        # we use username as email too.
        email = ""
        try:
            email = self.cleaned_data['username']
        except:
            email = ""

        return email


    def clean_invite_code(self):

        str = self.cleaned_data['invite_code']        

        # TODO: Validate invite code through programming
        code_valid = (str == 'a')
        code = self.cleaned_data['invite_code']        
        if code_valid == False:
            raise forms.ValidationError(u'Din inbjudningskod (\'%s\') var felaktig. Vänligen kontrollera att du skrev rätt.' % code)
 
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
        # send back urls to the images, instead of Picture objects
        images_lst = []
        for index, image in enumerate(queryset):
            images_lst.append(self.get_image_url(image))
            
        return images_lst

    def get_gallery_images(self, user, limit=0):
        # TODO: should have limit on number of imgs to display
        # 'G' = gallery images
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='G').filter(display_on_profile=True)

        return self.get_images(queryset)
        
    def get_profile_image(self, user):
        # 'C' = current profile image
        queryset = Picture.objects.filter(user__exact=user).filter(
            image_type='C')
        
        return self.get_images(queryset)

    def weekday_factory(self, obj, day = 'mon', pretty_dayname = 'Måndag'):

        """
        Helper function to create a dict with relevant day information.
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

    def get_profile_image_url(self, profile_user_id):
        profile_picture = ''
        try:
            profile_picture  = self.get_profile_image(profile_user_id)[0]
            print "\n"*10, profile_picture
        except:
            # TODO: Genders?
            profile_picture = '/static/user-imgs/profile_male.jpg'

        return profile_picture

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

class PicturesView(LoginRequiredMixin, TemplateView):
    """
    Display edit pictures page
    Many javascript dependencies one this page which interacts with the
    REST API specified in class PictureResource
    """
    template_name = "accounts/profile_images_edit.html"

    def get_context_data(self, **kwargs):
        context = super(PicturesView, self).get_context_data(**kwargs)
        return context


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

