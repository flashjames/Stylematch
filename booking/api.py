from tastypie.resources import ModelResource
from booking.models import CalendarEvent
from accounts.api_auth import DjangoBasicAuthentication, StylistAuthorization
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.validation import Validation, FormValidation
from django.contrib.auth.models import User
from accounts.models import Service
from django.http import HttpResponse
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http
from tastypie.http import HttpBadRequest
from django.db.models import Q

from django import forms
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)


def time_between_dates(start_time, end_time):
    """
    Parses two datetime strings in format %Y-%m-%dT%H:%M
    and returns time between them in minutes.
    """
    delta = end_time - start_time
    return delta.seconds / 60


class CalendarEventForm(forms.Form):
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
    note = forms.CharField(max_length=200)


class ClientValidation(FormValidation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Not quite what I had in mind.'}

        errors = {}
        
        try:
            # check if it's an integer
            test = bundle.data['stylist_user'] + 1
        except TypeError:
            errors['stylist_user'] = ["This field needs to be an integer"]
            logger.error("Supplied a bad stylist id")
        else:
            # is it a valid stylist id?
            try:
                User.objects.get(id=bundle.data['stylist_user'])
            except User.DoesNotExist:
                logger.error("Supplied a bad stylist id")
                errors['stylist_user'] = ["There's no stylist with this ID"]

        service_objects = []
        total_service_length = 0
        try:
            # valid service id's?
            for service in bundle.data['services']:
                service_object = Service.objects.get(id=service)
                service_objects.append(service_object)
                total_service_length += service_object.length
        except Service.DoesNotExist:
            logger.error("Supplied a bad service id")
            errors['services'] = ["You supplied a service id that DoesNotExist"]
        except ValueError:
            logger.error("Supplied a bad service id")
            errors['services'] = ["You need to supply service id's as int's"]
        else:
            start_time = start_time = datetime.strptime(bundle.data['start_time'], "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(bundle.data['end_time'], "%Y-%m-%dT%H:%M")
            minutes_between = time_between_dates(start_time, end_time)
            if total_service_length != minutes_between:
                errors['services'] = ["The end_time isnt what it should be according "
                                      "to which services we are trying to book"]
            else:
                # save for use in hydrate_m2m
                bundle.data['service_objects'] = service_objects


            # any event at this time and date already?
            stylist_user=bundle.data['stylist_user']
            result = CalendarEvent.objects.filter(Q(start_time__lt=end_time) &
                                         Q(end_time__gt=start_time), stylist_user=stylist_user)
            if result:
                errors['general_error'] = ["There's already an event at this time"]
            
        
        
        return errors

# for example we should not send out any information about the event to the client-booking - only
# the start/end-time
class ClientEventResource(ModelResource):
    def apply_authorization_limits(self, request, object_list):
        if not request.method in ('GET'):
            return object_list

        # poor mans filtering (objects between dates). according to documentation
        # you should be able to filter client side with get parameters
        # but didnt work.        
        if request.GET.has_key("_start_time") and request.GET.has_key("_end_time") and (
            request.GET.has_key("stylist_user")):
            start_time = request.GET["_start_time"]
            end_time = request.GET["_end_time"]
            stylist_user = request.GET["stylist_user"]
            reg_exp = r'\d*\-*'
            if re.match(reg_exp, start_time) and re.match(reg_exp, start_time) and (
                stylist_user.isdigit()):                             
                return object_list.filter(start_time__range=[start_time, end_time],
                                          stylist_user=stylist_user)

        raise ImmediateHttpResponse(HttpBadRequest("Input didnt match expected data"))

    def obj_get(self, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_get``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        try:
            base_object_list = self.get_object_list(request).filter(**kwargs)
            
            # CHANGED: Since we hijacked apply_authorization_limits for GET requests of multiple objects
            # we dont want to call it when getting one object
            #object_list = self.apply_authorization_limits(request, base_object_list)
            object_list = base_object_list
            
            stringified_kwargs = ', '.join(["%s=%s" % (k, v) for k, v in kwargs.items()])

            if len(object_list) <= 0:
                raise self._meta.object_class.DoesNotExist("Couldn't find an instance of '%s' which matched '%s'." % (self._meta.object_class.__name__, stringified_kwargs))
            elif len(object_list) > 1:
                raise MultipleObjectsReturned("More than '%s' matched '%s'." % (self._meta.object_class.__name__, stringified_kwargs))

            return object_list[0]
        except ValueError:
            raise NotFound("Invalid resource lookup data provided (mismatched type).")


    def is_authenticated(self, request):
        """
        Handles checking if the user is authenticated and dealing with
        unauthenticated users.

        Mostly a hook, this uses class assigned to ``authentication`` from
        ``Resource._meta``.
        """
        # Authenticate The Request As Needed.
        auth_result = self._meta.authentication.is_authenticated(request)

        # we want to allow GET requests without authentication
        if not request.method in ('GET'):
            if isinstance(auth_result, HttpResponse):
                raise ImmediateHttpResponse(response=auth_result)
            
            if not auth_result is True:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
    
    def hydrate(self, bundle):
        if not bundle.data.has_key('stylist_user'):
            raise ImmediateHttpResponse(HttpBadRequest("Input didnt match expected data2"))
        
        bundle.obj.stylist_user_id = bundle.data['stylist_user']
        bundle.obj.client_user = bundle.request.user
        return bundle

    def hydrate_m2m(self, bundle):
        for service_object in bundle.data['service_objects']:
            bundle.obj.services.add(service_object)
        return bundle

    class Meta:
        validation = ClientValidation(form_class=CalendarEventForm)
        limit = 500
        queryset = CalendarEvent.objects.all()
        authentication = DjangoBasicAuthentication()
        authorization = Authorization()
        allowed_methods = ['get', 'post']
        resource_name = 'client_calendar_event'
        pass_request_user_to_django = True
        fields = ['start_time', 'end_time']

        
class StylistEventResource(ModelResource):
    def hydrate(self, bundle):
        bundle.obj.stylist_user_id = bundle.request.user.id
        bundle.obj.client_user_id = bundle.request.user.id
        return bundle

    class Meta:
        authorization = StylistAuthorization()
        authentication = DjangoBasicAuthentication()
        resource_name = 'stylist_calendar_event'
        limit = 500
        queryset = CalendarEvent.objects.all()
        pass_request_user_to_django = True
