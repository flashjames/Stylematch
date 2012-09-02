# coding:utf-8
from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from booking.views import StylistBookingView
from booking.api import ClientEventResource, StylistEventResource
from tastypie.api import Api

booking_api = Api(api_name='booking')
booking_api.register(ClientEventResource())
booking_api.register(StylistEventResource())


urlpatterns = patterns('',
                       (r'^booking/',
                        StylistBookingView.as_view(),
                        {},
                        'client-booking'),
                       (r'^api/',
                        include(booking_api.urls)),
)
