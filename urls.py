from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from index.views import AboutPageView, IndexPageView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'styleseat.views.home', name='home'),
    # url(r'^styleseat/', include('styleseat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls'))
    # Login / logout.
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'index.views.logout_page'),
    url(r'', include('social_auth.urls')),
                     
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^$', 'direct_to_template', {'template': 'index.html'}, name='index'),
    #url(r'^profile_index$', 'index.views.profile_index'),
    (r'^$', IndexPageView.as_view(),{}, 'index_page'),
    (r'^accounts/', include('registration.urls')), # django-registration
    url(r'^upload/', include('fileupload.urls')), # django-fileupload
    url(r'^', include('accounts.urls')), # accounts
    (r'^about-us', AboutPageView.as_view(),{}, 'about_page'),
    
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                url(r'^static/(?P<path>.*)$', 'serve'),
                        )
