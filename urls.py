from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView
from index.views import AboutPageView, IndexPageView, BetaPageView, FeaturesPageView, SignupStep1PageView, SignupStep2PageView

from django.contrib import admin
from django.views.generic.simple import redirect_to
from registration.views import register
from accounts.views import UserRegistrationForm

admin.autodiscover()

"""
WHEN ADDING NEW URLS

Django have a setting called APPEND_SLASH, if Django doesnt find for example /index
it will redirect to /index/ and try that instead (if APPEND_SLASH=True which it is by default).
-> Always set urls without slash at the end, since there's no REMOVE_SLASH.
"""


urlpatterns = patterns(
    '',
    (r'^logout$', 'index.views.logout_page',{},'logout'), # redirects to main-page
    url(r'', include('social_auth.urls')), # urls to connect with social media accountsm for example facebook
     url(r'^accounts/register$', register, {'backend': 'registration.backends.default.DefaultBackend','form_class': UserRegistrationForm}, name='registration_register'),
    url(r'accounts/register/complete', redirect_to, {'url': '/accounts/signup-step1'}, 'registration_complete'),
    (r'', include('registration.auth_urls')), # login/logout/password-management urls             
    url(r'^admin/', include(admin.site.urls)),
    (r'^startsida', IndexPageView.as_view(),{}, 'index_page'),
    
    url(r'accounts/signup-step1', SignupStep1PageView.as_view(), {}, 'signup_step1'),
    
    (r'^accounts/signup-step1', SignupStep1PageView.as_view(),{}, 'signupstep1_page'),
    (r'^accounts/signup-step2', SignupStep2PageView.as_view(),{}, 'signupstep2_page'),

   
    
    (r'^accounts/edit-settings', TemplateView.as_view(template_name="edit-account-settings.html"),{},'edit-account-settings'),
   
    (r'^about-us', AboutPageView.as_view(),{}, 'about_page'),
    (r'^$', BetaPageView.as_view(),{}, 'beta_page'),
    (r'^features', FeaturesPageView.as_view(),{}, 'features_page'),
   
    (r'^google66ca7050dfade3e4.html', TemplateView.as_view(template_name="google66ca7050dfade3e4.html")), #tracking-code so google apps know we own the domain.
    
     url(r'^', include('accounts.urls')), # accounts/profile, should always be at the end. since a user may set a profile url that match another url -> if it's not at the end it may overwrite it.
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                url(r'^static/(?P<path>.*)$', 'serve'),
                        )
