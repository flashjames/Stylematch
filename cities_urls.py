from django.conf.urls.defaults import *
from index.views import SearchView

cities = ['linkoping','stockholm']

urlpatterns = patterns('',)
for city in cities:
    urlpatterns += patterns('',
        # need to be first, or redirection to profile wont work.
        (r'^'+city,
                SearchView.as_view(),
                {'city':city}),
    )
