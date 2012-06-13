# coding:utf-8
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from index.views import SearchCityView
import unicodedata
import urllib as ul

cities = [u'linköping','stockholm']

urlpatterns = patterns('',)
for city in cities:
    urlpatterns += patterns('',
        # need to be first, or redirection to profile wont work.
        url(u'^'+city,
                SearchCityView.as_view(),
                {'city':city}),
    )
