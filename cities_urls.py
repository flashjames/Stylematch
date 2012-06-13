from django.conf.urls.defaults import *
from index.views import SearchCityView

cities = ['linkoping','stockholm']

urlpatterns = patterns('',)
for city in cities:
    urlpatterns += patterns('',
        # need to be first, or redirection to profile wont work.
        url(r'^'+city,
                SearchCityView.as_view(),
                {'city':city}),
    )
