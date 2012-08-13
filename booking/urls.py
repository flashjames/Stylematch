# coding:utf-8
from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from booking.api import (CalendarEventResource)
from tastypie.api import Api

booking_api = Api(api_name='booking')
booking_api.register(CalendarEventResource())


urlpatterns = patterns('',
                       (r'^client/',
                        TemplateView.as_view(template_name="client_booking.html"),
                        {},
                        'client-booking'),
                       (r'^api/',
                        include(booking_api.urls)),


)
