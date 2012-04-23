from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from index.views import AboutPageView, IndexPageView, BetaPageView, FeaturesPageView, SignupStep1PageView, SignupStep2PageView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin



from django.views.generic.simple import redirect_to

from registration.views import register
import registration.backends.default.urls as registrationURLs

from accounts.views import UserRegistrationForm

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
    (r'^startsida', IndexPageView.as_view(),{}, 'index_page'),
    
    url(r'accounts/register/signup-step1', SignupStep1PageView.as_view(), {}, 'signup_step1'),
    url(r'accounts/register/complete', redirect_to, {'url': '/accounts/register/signup-step1'}, 'redirect_to_signup_step1'),

    url(r'^accounts/register/$', register, {'backend': 'registration.backends.default.DefaultBackend','form_class': UserRegistrationForm}, name='registration_register'),
	(r'^accounts/', include(registrationURLs)), # django-registration


    url(r'^', include('accounts.urls')), # accounts
    (r'^about-us', AboutPageView.as_view(),{}, 'about_page'),
    (r'^$', BetaPageView.as_view(),{}, 'beta_page'),
    (r'^features', FeaturesPageView.as_view(),{}, 'features_page'),
    (r'^signup-step1', SignupStep1PageView.as_view(),{}, 'signupstep1_page'),
    (r'^signup-step2', SignupStep2PageView.as_view(),{}, 'signupstep2_page'),
    
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                url(r'^static/(?P<path>.*)$', 'serve'),
                        )
