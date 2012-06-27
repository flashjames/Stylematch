# coding:utf-8
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from index.views import SearchCityView

from index.cities import *

cities = []
for city in popular + other:
    if city not in cities:
        cities += [city.lower()]

urlpatterns = patterns('',)
for city in cities:
    urlpatterns += patterns('',
        # need to be first, or redirection to profile wont work.
        url(u'^'+city,
                SearchCityView.as_view(),
                {'city':city}),
    )
