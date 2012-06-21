#-*- coding:utf-8 -*-
from accounts.models import InviteCode, UserProfile
from braces.views import LoginRequiredMixin
from django import forms
from django.forms import ModelForm, ValidationError
from django.views.generic import UpdateView
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from registration.backends.default import DefaultBackend
from registration.forms import RegistrationForm

from accounts.views import (OpenHoursView,
                            ServicesView,
                            EditImagesView,
                            get_unique_filename)

from index.models import BetaEmail


class SignupViewForm(ModelForm):
    """
    Form used in registration step 1, used to filter out wanted fields
    """
    salon_phone_number = forms.CharField(label='Telefonnummer för bokning')
    
    def __init__(self, *args, **kwargs):
        super(SignupViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('salon_name',
                  'salon_adress',
                  'salon_city',
                  'salon_phone_number')


class SignupView(LoginRequiredMixin, UpdateView):
    """
    Step 1 in the user registration, after the main user registration.
    The user is asked to fill in some of the other fields.
    """
    template_name = "accounts/signup_step1.html"
    form_class = SignupViewForm

    def __init__(self, *args, **kwargs):
        super(SignupView, self).__init__(*args, **kwargs)
        self.success_url = reverse('signupstep2_page')

    def get_object(self, queryset=None):
        obj = UserProfile.objects.get(user__exact=self.request.user.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)

        context['progress_salon_info'] = "reached-progress"
        context['progress_width'] = "32%"

        return context


class SignupStep2View(EditImagesView):
    template_name = "accounts/signup_step2.html"

    def __init__(self, *args, **kwargs):
        super(SignupStep2View, self).__init__(*args, **kwargs)
        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url = reverse('signupstep2_page')

    def get_context_data(self, **kwargs):
        context = super(SignupStep2View, self).get_context_data(**kwargs)

        context['progress_salon_info'] = "reached-progress"
        context['progress_salon_hours'] = "reached-progress"
        context['progress_salon_price'] = "reached-progress"
        context['progress_profile_pic'] = "reached-progress"
        context['progress_width'] = "83%"

        return context

    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        f = self.request.FILES.get('file')

        filename = get_unique_filename(f.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.filename = filename

        # default image type, Gallery
        self.object.image_type = 'C'
        self.object.save()
        form.save_m2m()
        return super(SignupStep2View, self).form_valid(form)


class RegisterCustomBackend(DefaultBackend):
    """
    Extends django registration DefaultBackend, since we want
    to activate the user, save first_name and last_name.
    Followed this example:
    http://inka-labs.com/en-us/blog/2012/01/13/add-custom-backend-django-registration/

    TODO:
    Possible problem, the guide said you have to define a skeleton and
    call super, for the other functions to work. But I dont think you need to.
    """
    def register(self, request, **kwargs):
        user = super(RegisterCustomBackend, self).register(request, **kwargs)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        # login the newly registered user
        login(request, user)

        user.first_name = kwargs['first_name']
        user.last_name = kwargs['last_name']
        # set is_active = True, must be set and saved to DB after login
        # function is called.
        user.is_active = True

        user.save()
        return user


class UserRegistrationForm(RegistrationForm):
    """
    Custom user registration form. Used as the main registration form.
    """

    email = forms.CharField(required=False)
    first_name = forms.CharField(label="Förnamn")
    last_name = forms.CharField(label="Efternamn")
    invite_code = forms.CharField(label="Inbjudningskod "
                                        "(just nu behövs en inbjudan "
                                        "för att gå med)")

    username = forms.EmailField(max_length=64, label="Emailadress")

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
        queryset = InviteCode.objects.filter(
                        invite_code__iexact=supplied_invite_code).filter(
                        used=False)

        # a permanent key which can be used by us
        if supplied_invite_code == "permanent1":
            return supplied_invite_code

        # check that the invite_code exists
        invite_code = queryset[:1]
        if not invite_code:
            raise forms.ValidationError(u'Din inbjudningskod (\'%s\') '
                                        u'var felaktig. Vänligen kontrollera '
                                        u'att du skrev rätt.'
                                        % supplied_invite_code)

        # only set the invite code to used=True if all other fields have
        # validated correctly
        # TODO:
        # this is run even if the passwords doesnt match in the clean()
        # method. since this function is run before clean()
        if self.is_valid():
            invite_code = invite_code[0]
            invite_code.used = True
            invite_code.save()

        return supplied_invite_code

    def clean(self):
        """
        Verifies that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if ('password1' in self.cleaned_data and
            'password2' in self.cleaned_data):
            password1 = self.cleaned_data.get('password1')
            password2 = self.cleaned_data.get('password2')


            if password1 != password2:
                error_msg = "Lösenorden stämmer ej överens"
                self._errors['password1'] = self.error_class([error_msg])
                raise ValidationError(error_msg)
            

            MIN_LENGTH = 5
            if len(password1) < MIN_LENGTH:
                error_msg = "Lösenordet är för kort, minst 5 tecken."
                self._errors['password1'] = self.error_class([error_msg])
                raise forms.ValidationError(error_msg)
            
        return self.cleaned_data

    class Meta:
        exclude = ('email',)
