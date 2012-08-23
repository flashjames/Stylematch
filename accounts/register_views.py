#-*- coding:utf-8 -*-
from accounts.models import UserProfile
from braces.views import LoginRequiredMixin
from django import forms
from django.forms import ModelForm, ValidationError
from django.views.generic import UpdateView
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from registration.backends.default import DefaultBackend
from registration.forms import RegistrationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from registration.signals import user_registered
from django.conf import settings
from django.contrib.auth.models import Group

from accounts.models import OpenHours, UserProfile, ClientUserProfile
from accounts.views import (OpenHoursView,
                            ServicesView,
                            SaveProfileImageView,
                            get_unique_filename)

from index.models import BetaEmail

import uuid
import logging
logger = logging.getLogger(__name__)


class SignupViewForm(ModelForm):
    """
    Form used in registration step 1, used to filter out wanted fields

    """
    salon_phone_number = forms.CharField(label='Telefonnummer för bokning',
                                         required=False)

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
        context['progress_width'] = "40.5%"

        context['no_menu'] = True

        # used to determine if it's a newly registered user
        # -> display more clearly where he should go on profile page
        self.request.session['extra_user_guidance'] = True
        return context


class SignupStep2View(SaveProfileImageView):
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
        context['progress_width'] = "66%"

        context['no_menu'] = True
        return context


def handle_invite_code(request, new_user):
    """
    Check if the user uses an invite code, if it's a valid invite cod,
    set the invite code as used by this user.
    
    ´new user´ is the user that was created with the invite code
    """
    if request.GET.get('kod'):
        supplied_invite_code = request.GET.get('kod')
        #try:
        #    pass
        #invite_code = InviteCode.objects.get(
        #            invite_code__iexact=supplied_invite_code,
        #            used=False,
        #            reciever=None)
        #except InviteCode.DoesNotExist:
        #    logger.debug('New user registered: Supplied invite code'
        #                 ' but it wasnt valid')
        #else:
        #    logger.info('New user registered: Used a valid invite code')
        #    invite_code.used = True
        #    invite_code.reciever = new_user
        #    invite_code.save()


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


class UserRegistrationForm(forms.Form):
    """
    Custom user registration form. Used as the main registration form.
    """

    email = forms.CharField(required=False)
    first_name = forms.CharField(label="Förnamn")
    last_name = forms.CharField(label="Efternamn")

    username = forms.EmailField(max_length=64, label="Emailadress")
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=True),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=True),
                                label=_("Password (again)"), required=False)

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']


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


    def clean(self):
        """
        Verifies that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """

        if 'password1' in self.cleaned_data:
            MIN_LENGTH = 5
            password1 = self.cleaned_data.get('password1')
            if len(password1) < MIN_LENGTH:
                error_msg = "Lösenordet är för kort, minst 5 tecken."
                self._errors['password1'] = self.error_class([error_msg])
                raise forms.ValidationError(error_msg)

        if ('password1' in self.cleaned_data and
            'password2' in self.cleaned_data):
            password2 = self.cleaned_data.get('password2')

            #  we may have came from a template that only ask user to supply one password
            # so this is not always checked
            if password1 != password2:
                error_msg = "Lösenorden stämmer ej överens"
                self._errors['password1'] = self.error_class([error_msg])
                raise ValidationError(error_msg)

        return self.cleaned_data

    class Meta:
        exclude = ('email',)

def register(request, success_url=None, form_class=None,
             template_name='registration/registration_form.html',
             redirect_to="signupstep1_page", stylist=True):

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            username, email, password = form.cleaned_data['username'], form.cleaned_data['username'], form.cleaned_data['password1'] # username contains the email
            
            new_user = User.objects.create_user(username, email, password)

            # login user
            new_user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, new_user)
            
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            
            # set is_active = True, must be set and saved to DB after login
            # function is called.
            new_user.is_active = True
            new_user.save()
            
            if stylist:
                UserProfile.objects.create(
                    user=new_user,
                    temporary_profile_url=uuid.uuid4().hex,
                    )
            
                OpenHours.objects.create(user=new_user)
                group, created = Group.objects.get_or_create(name='Stylist')
                new_user.groups.add(group)

                subject = render_to_string('registration/activation_email_subject.txt')
                # Email subject *must not* contain newlines
                subject = ''.join(subject.splitlines())
        
                message = render_to_string('registration/activation_email.txt')
                new_user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

                user_registered.send(sender="register",
                                     user=new_user,
                                     request=request)



            else:
                ClientUserProfile.objects.create(user=new_user)
                group, created = Group.objects.get_or_create(name='Client')
                new_user.groups.add(group)

            if success_url is None:
                return redirect(redirect_to)
            else:
                return redirect(success_url)
    else:
        form = form_class()
    
    context = RequestContext(request)

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)
