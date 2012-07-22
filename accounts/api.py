#-*- coding:utf-8 -*-
import os
from django.conf import settings
from accounts.models import (Service,
                             GalleryImage,
                             ProfileImage,
                             UserProfile,
                             Featured,
                             get_image_url)
from accounts.signals import approved_user_criteria_changed
from django.forms import ModelForm
from django.contrib.auth.models import User
from tastypie.validation import FormValidation
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from sorl.thumbnail import get_thumbnail
from django.http import QueryDict
from datetime import datetime


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

        approved_user_criteria_changed.send(
                                sender=self,
                                request=request,
                                userprofile=request.user.userprofile
        )
        return bundle

    def obj_delete(self, request=None, **kwargs):
        pre = super(ServiceResource, self).obj_delete(request, **kwargs)
        approved_user_criteria_changed.send(
                                sender=self,
                                request=request,
                                userprofile=request.user.userprofile
        )
        return pre

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

        approved_user_criteria_changed.send(
                                sender=self,
                                request=request,
                                userprofile=request.user.userprofile
        )
        return bundle

    def obj_delete(self, request=None, **kwargs):
        pre = super(PictureResource, self).obj_delete(request, **kwargs)
        approved_user_criteria_changed.send(
                                sender=self,
                                request=request,
                                userprofile=request.user.userprofile
        )
        return pre

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


class InspirationResource(ModelResource):
    def time_since_upload(self, upload_date):
        """
        Convert upload_date to minutes, or hours or days
        since upload.
        """
        time_since_upload_delta = datetime.now() - upload_date
        minutes_since_upload = time_since_upload_delta.seconds / 60
        # days
        if time_since_upload_delta.days > 0:
            return "".join([str(time_since_upload_delta.days), " dagar"])
        # hours
        elif minutes_since_upload >= 60:
            plural_or_singular = " timmar"
            if minutes_since_upload / 60 == 1:
                plural_or_singular = " timme"
            return "".join([str(minutes_since_upload / 60),
                            plural_or_singular])
        # minutes
        else:
            return "".join([str(minutes_since_upload), " minuter"])

    def dehydrate(self, bundle):

        bundle.data['first_name'] = bundle.obj.user.first_name
        bundle.data['last_name'] = bundle.obj.user.last_name
        bundle.data['profile_url'] = bundle.obj.user.userprofile.profile_url
        bundle.data['salon_city'] = bundle.obj.user.userprofile.salon_city
        #now = datetime.now() #

        bundle.data['time_since_upload'] = self.time_since_upload(
            bundle.obj.upload_date)
        # rescaled image with sorl-thumbnail
        bundle.data['image_url'] = "".join([settings.MEDIA_URL,
                                            get_thumbnail(bundle.obj.file, '560').name])
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = QueryDict('')

        # get all userprofiles objects
        users = UserProfile.objects.filter(visible=True)
        # create a filter for those profiles based on pk
        filter = {'user__in': [i.pk for i in users]}

        # build the rest of the filters
        orm = super(InspirationResource, self).build_filters(filters)
        # update the filter with our userprofiles
        orm.update(filter)
        return orm

    class Meta:
        resource_name = 'inspiration'
        queryset = GalleryImage.objects.filter(display_on_profile=True).order_by('-upload_date')
        excludes = ['user']
        allowed_methods = ['get']
        limit = 50
        max_limit = 0


class ProfileResource(ModelResource):
    """
    Resource to access a profile
    """
    profile_image_size = ""

    def move_up(self, id, data):
        for i in range(len(data['objects'])):
            if int(data['objects'][i].data['id']) == id:
                if i > 2:
                    obj = data['objects'].pop(i)
                    import random
                    pos = random.randint(0, 2)
                    data['objects'].insert(pos, obj)
        return data

    def move_down(self, id, data):
        for i in range(len(data['objects'])):
            if int(data['objects'][i].data['id']) == id:
                if i < 3 and len(data['objects']) > 3:
                    obj = data['objects'].pop(i)
                    import random
                    pos = random.randint(3, len(data['objects']) - 1)
                    data['objects'].insert(pos, obj)
        return data

    def serialize(self, request, data, format, options=None):
        #data = self.move_down(15, data)
        #data = self.move_up(57, data)
        #data = self.move_up(38, data)
        return super(ProfileResource, self).serialize(request,
                                                      data,
                                                      format,
                                                      options)

    def build_filters(self, filters=None):
        if filters is None:
            filters = QueryDict('')
            filters._mutable = True

        # save the requested profile_image_size for later use in ``dehydrate``
        if 'profile_image_size' in filters:
            self.profile_image_size = filters['profile_image_size']
            del filters['profile_image_size']

        return super(ProfileResource, self).build_filters(filters)

    def dehydrate(self, bundle):
        """
        Some additional fields needs to be added:
         - ``profile_image``
         - ``profile_url`` (which is either ``profile_url`` or ``temporary_profile_url``
         - ``first_name`` (retrieved from django.auth)
         - ``last_name`` (same as ``first_name``)
        """

        img = ProfileImage.objects.filter(user=bundle.data['id'])
        chosen_img = None
        if len(img) > 0:
            if img[0].cropped or len(img) < 2:
                chosen_img = img[0]
            else:
                chosen_img = img[1]

            # Use a thumbnail version if image size has been set in request
            # See build_filters()
            if self.profile_image_size:
                from sorl.thumbnail import get_thumbnail
                tn = get_thumbnail(chosen_img.file,
                                   self.profile_image_size,
                                   cropped="center")
                bundle.data['profile_image'] = tn.url
            else:
                bundle.data['profile_image'] = get_image_url(chosen_img.filename)
        else:
            bundle.data['profile_image'] = os.path.join(
                            settings.STATIC_URL, 'img',
                            'default_image_profile_not_logged_in.jpg')

        # if profile_url isn't set, use temporary_profile_url
        # temporary_profile_url isn't needed
        if ('profile_url' in bundle.data and
                not bundle.data['profile_url']):
            bundle.data['profile_url'] = bundle.data['temporary_profile_url']
        del bundle.data['temporary_profile_url']

        try:
            user = User.objects.get(pk=bundle.data['id'])
            bundle.data['first_name'] = user.first_name
            bundle.data['last_name'] = user.last_name
        except User.DoesNotExist:
            bundle.data['first_name'] = ""
            bundle.data['last_name'] = ""
        return bundle

    class Meta:
        allowed_methods = ['get']
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
                'salon_city' : ['iexact',], # 'startswith','endswith'],
                'show_booking_url' : ['exact',],
                'profile_image_size': ['exact',],
                }
        resource_name = "profiles"
        model = UserProfile
        limit = 10
        # NOTE: Ordering by random is slow
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#order-by
        queryset = UserProfile.objects.filter(visible=True).order_by('?')


class FeaturedProfileResource(ProfileResource):

    def build_filters(self, filters=None):
        if filters is None:
            filters = QueryDict('')

        # get all featured profile objects
        featured = Featured.objects.all()
        # create a filter for those profiles based on pk
        filter = {'pk__in' : [i.user.pk for i in featured]}

        # build the rest of the filters
        orm = super(FeaturedProfileResource, self).build_filters(filters)
        # update the filter with our featured profiles
        orm.update(filter)
        return orm

    class Meta(ProfileResource.Meta):
        resource_name = "featured_profiles"
