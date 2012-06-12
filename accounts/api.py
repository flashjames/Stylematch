#-*- coding:utf-8 -*-
from django.conf import settings
from accounts.models import (Service,
                             GalleryImage,
                             ProfileImage,
                             UserProfile,
                             get_image_url)
from django.forms import ModelForm
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.validation import FormValidation
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
import os


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
    First check session data if user is logged in, with the Django
    authentication.
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
        return super(DjangoBasicAuthentication, self).is_authenticated(
                                                         request,
                                                         **kwargs)


class ServiceForm(ModelForm):
    class Meta:
        model = Service
        exclude = ('order')


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
        validation = FormValidation(form_class=ServiceForm)


class PictureForm(ModelForm):
    class Meta:
        model = GalleryImage


class PictureResource(ModelResource):

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

    def dehydrate(self, bundle):
        # add client side image url to each Picture object
        bundle.data['image_url'] = get_image_url(bundle.data['filename'])
        return bundle

    class Meta:
        resource_name = 'picture'
        pass_request_user_to_django = True
        authentication = DjangoBasicAuthentication()
        authorization = PerUserAuthorization()
        queryset = GalleryImage.objects.all()

        excludes = ['file', 'user']
        limit = 50
        max_limit = 0
        validation = FormValidation(form_class=PictureForm)


class ProfileImageResource(ModelResource):

    def dehydrate(self, bundle):
        """
        Return the real URL instead of the local machine place
        """
        if 'filename' in bundle.data:
            bundle.data['filename'] = get_image_url(bundle.data['filename'])
        return bundle

    class Meta:
        include_resource_uri = False
        allowed_methods = []
        resource_name = 'profile_image'
        fields = ['filename']
        queryset = ProfileImage.objects.all()


class ProfileResource(ModelResource):
    """
    Resource to access a profile
    """
    profile_image = fields.ForeignKey(ProfileImageResource,
                                      'profile_image_cropped',
                                      full=True,
                                      null=True)

    def dehydrate(self, bundle):
        """
        'profile_image' is in a second level bundle, from
        ProfileImageResource, and this is extracting that to make the
        data structure more logical
        """
        if ('profile_image' in bundle.data and
            bundle.data['profile_image'] is not None and
            'filename' in bundle.data['profile_image'].data):
                bundle.data['profile_image'] = bundle.data['profile_image'].\
                                                      data['filename']
        else: #use standard image
            bundle.data['profile_image'] = os.path.join(
                                settings.STATIC_URL, 'img',
                                'default_image_profile_not_logged_in.jpg')

        # if profile_url isn't set, use temporary_profile_url
        # temporary_profile_url isn't needed
        if ('profile_url' in bundle.data and
                not bundle.data['profile_url']):
            bundle.data['profile_url'] = bundle.data['temporary_profile_url']
        del bundle.data['temporary_profile_url']
        return bundle

    class Meta:
        include_resource_uri = False
        # temporary_profile_url is not passed to the user, it's only there
        # because it is needed in 'dehydrate'
        fields = ['zip_adress',
                  'show_booking_url',
                  'profile_text',
                  'salon_phone_number',
                  'personal_phone_number',
                  'url_online_booking',
                  'profile_image',
                  'salon_name',
                  'salon_city',
                  'salon_adress',
                  'number_on_profile',
                  'salon_url',
                  'id',
                  'profile_url',
                  'temporary_profile_url']
        filtering = {
                'salon_city' : ['iexact','startswith','endswith'],
                }
        resource_name = "profiles"
        model = UserProfile
        # NOTE: Ordering by random is slow
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#order-by
        queryset = UserProfile.objects.filter(visible=True).order_by('?')
