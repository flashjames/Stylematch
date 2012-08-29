from tastypie.resources import ModelResource
from booking.models import CalendarEvent
from accounts.api_auth import PerUserAuthorization, DjangoBasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation, FormValidation
from django.contrib.auth.models import User
from accounts.models import Service
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
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
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
            test = bundle.data['stylist_user_id'] + 1
        except TypeError:
            errors['stylist_user_id'] = ["This field needs to be an integer"]
            logger.error("Supplied a bad stylist id")
        else:
            # is it a valid stylist id?
            try:
                User.objects.get(id=bundle.data['stylist_user_id'])
            except User.DoesNotExist:
                logger.error("Supplied a bad stylist id")
                errors['stylist_user_id'] = ["There's no stylist with this ID"]

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
            minutes_between = time_between_dates(bundle.data['start_time'],bundle.data['end_time'])
            if total_service_length != minutes_between:
                errors['services'] = ["The end_time isnt what it should be according "
                                      "to which services we are trying to book"]
            else:
                # save for use in hydrate_m2m
                bundle.data['service_objects'] = service_objects
        
        return errors


# filter on dates - http://stackoverflow.com/questions/1317714/how-can-i-filter-a-date-of-a-datetimefield-in-django
# will need a child of this class for client-booking, with more locked down permissions
# for example we should not send out any information about the event to the client-booking - only
# the start/end-time
class CalendarEventResource(ModelResource):
    def apply_authorization_limits(self, request, object_list):
        # poor mans filtering (objects between dates). according to documentation
        # you should be able to filter client side with get parameters
        # but didnt work.
        if request.GET.has_key("_start_time") and request.GET.has_key("_end_time"):
            start_time = request.GET["_start_time"]
            end_time = request.GET["_end_time"]
            reg_exp = r'\d*\-*'
            if re.match(reg_exp, start_time) and re.match(reg_exp, start_time):                             
                return object_list.filter(start_time__range=[start_time, end_time])

        return object_list

    def hydrate(self, bundle):
        bundle.obj.stylist_user_id = bundle.data['stylist_user_id']
        bundle.obj.client_user_id = bundle.request.user.id
        return bundle

    def hydrate_m2m(self, bundle):
        for service_object in bundle.data['service_objects']:
            bundle.obj.services.add(service_object)
        return bundle
        
    class Meta:
        limit = 500
        queryset = CalendarEvent.objects.all()
        validation = ClientValidation(form_class=CalendarEventForm)
        resource_name = 'calendar_event'
        authorization = Authorization()
        authentication = DjangoBasicAuthentication()
        pass_request_user_to_django = True
        # should be sorted after date and maybe return a list for each date
        # also limit permissions
