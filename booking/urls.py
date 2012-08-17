# coding:utf-8
from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from booking.views import ClientBookingView, BookEventAPI
from booking.api import (CalendarEventResource)
from tastypie.api import Api

booking_api = Api(api_name='booking')
booking_api.register(CalendarEventResource())


urlpatterns = patterns('',
                       (r'^client/',
                        ClientBookingView.as_view(),
                        {},
                        'client-booking'),
                       (r'^api/',
                        include(booking_api.urls)),
                       (r'^api/book-event',
                        BookEventAPI.as_view(),
                        {},
                        'book-event'),



)
