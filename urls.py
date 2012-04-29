from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView
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
    (r'^login/$', 'django.contrib.auth.views.login',{},'login'),
    (r'^logout/$', 'index.views.logout_page',{},'logout'),
    url(r'', include('social_auth.urls')),
    (r'', include('registration.auth_urls')),
                     
    url(r'^admin/', include(admin.site.urls)),
    (r'^startsida', IndexPageView.as_view(),{}, 'index_page'),
    
    url(r'accounts/signup-step1', SignupStep1PageView.as_view(), {}, 'signup_step1'),
    url(r'accounts/register/complete', redirect_to, {'url': '/accounts/signup-step1'}, 'redirect_to_signup_step1'),
    (r'^accounts/signup-step1', SignupStep1PageView.as_view(),{}, 'signupstep1_page'),
    (r'^accounts/signup-step2', SignupStep2PageView.as_view(),{}, 'signupstep2_page'),

    url(r'^accounts/register/$', register, {'backend': 'registration.backends.default.DefaultBackend','form_class': UserRegistrationForm}, name='registration_register'),
    (r'^accounts/', include(registrationURLs)), # django-registration

   
    (r'^about-us', AboutPageView.as_view(),{}, 'about_page'),
    (r'^$', BetaPageView.as_view(),{}, 'beta_page'),
    (r'^features', FeaturesPageView.as_view(),{}, 'features_page'),
   
    (r'^google66ca7050dfade3e4.html', TemplateView.as_view(template_name="google66ca7050dfade3e4.html")), #tracking-code so google apps know we own the domain.
     url(r'^', include('accounts.urls')), # accounts, should always be at the end. since a user may set a profile url that match another url.
    
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                url(r'^static/(?P<path>.*)$', 'serve'),
                        )
