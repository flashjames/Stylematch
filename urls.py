# coding:utf-8
from django.conf.urls.defaults import (patterns,
                                       include,
                                       url,
                                       handler404,
                                       handler500)
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from index.views import (IndexPageView,
                         BetaEmailView,
                         TipView,
                         StylistView,
                         InspirationPageView,
                         LikeView,
                         error500)
from dashboard.views import DashboardView

from django.contrib import admin
from django.views.generic.simple import redirect_to
from registration.views import register
from accounts.register_views import (UserRegistrationForm,
                                     SignupView,
                                     SignupStep2View)
from index.sitemap import StaticPagesSitemap

admin.autodiscover()

"""
WHEN ADDING NEW URLS
https://docs.djangoproject.com/en/dev/ref/settings/#append-slash

Django have a setting called APPEND_SLASH, if Django doesnt find for example
/index it will redirect to /index/ and try that instead
(if APPEND_SLASH=True which it is by default).
-> Always set urls with slash at the end.
"""

handler500 = 'index.views.error500'

urlpatterns = patterns('',)
if settings.DEVELOPMENT or settings.STAGING:
    urlpatterns = patterns('',
        url(r'^404/$',
                handler404),
        url(r'^500/$',
                handler500)
    )


sitemaps = {
    'static': StaticPagesSitemap
}

urlpatterns += patterns(
    '',
    # favicon
    url(r'^favicon\.ico$',
            RedirectView.as_view(url=settings.STATIC_URL + "img/favicon.ico")),
    # redirects to main-page
    (r'^logout/$',
            'index.views.logout_page',
            {},
            'logout'),
    (r'^utloggad/$',
            TemplateView.as_view(template_name="logged_out.html"),
            {},
            'logged_out_page'),
    # urls to connect with social media accountsm for example facebook
    url(r'',
            include('social_auth.urls')),
    url(r'^accounts/register/$',
            register,
            {'backend': 'accounts.register_views.RegisterCustomBackend',
             'form_class': UserRegistrationForm},
            name='registration_register'),
    url(r'accounts/register/complete/',
            redirect_to,
            {'url': '/konto/registrering-steg1/'},
            'registration_complete'),
    # login/logout/password-management urls
    (r'',
            include('registration.auth_urls')),
    url(r'^admin/',
            include(admin.site.urls)),
    (r'^$',
            IndexPageView.as_view(),
            {},
            'index_page'),
    (r'^konto/registrering-steg1/',
            SignupView.as_view(),
            {},
            'signupstep1_page'),
    (r'^konto/registrering-steg2/',
            SignupStep2View.as_view(),
            {},
            'signupstep2_page'),
    (r'^accounts/edit-settings/',
            TemplateView.as_view(template_name="edit-account-settings.html"),
            {},
            'edit-account-settings'),
    (r'^get_invite/',
            BetaEmailView.as_view(),
            {},
            'get_invite'),
    (r'^start/',
            TemplateView.as_view(template_name="betaemail_index.html"),
            {},
            'beta_index_page'),
    # 'Tipsa frisör'-page. Template in index/templates
    (r'^tip/',
     TipView.as_view(),
     {},
     'tip'),
    (r'^om-oss/',
     TemplateView.as_view(template_name="about_us.html"),
     {},
     'about_page'),
    (r'^jobb/',
     TemplateView.as_view(template_name="jobb.html"),
     {},
     'work_page'),

    (r'^kontakt/',
            TemplateView.as_view(template_name="contact_us.html"),
            {},
            'contact_page'),

    (r'^features/',
            TemplateView.as_view(template_name="features.html"),
            {},
            'features_page'),
    (u'^frisor/',
            StylistView.as_view(),
            {},
            'frisor_page'),
    (u'^faq-frisör/',
            TemplateView.as_view(template_name="faq_frisor.html"),
            {},
            'faq-frisor-page'),
    (r'^faq-privatperson/',
            TemplateView.as_view(template_name="faq_privatperson.html"),
            {},
            'faq-privatperson-page'),
    (r'^faq/',
            TemplateView.as_view(template_name="faq.html"),
            {},
            'faq-page'),
    (r'^press/',
            TemplateView.as_view(template_name="press.html"),
            {},
            'press_page'),
    (r'^anvandarvillkor/',
            TemplateView.as_view(template_name="anvandarvillkor.html"),
            {},
            'anvandarvillkor'),
    (r'^salongsprofil/',
            TemplateView.as_view(template_name="salongsprofil.html"),
            {},
            'salongsprofil'),
    url(r"^su/",
            include("django_su.urls")),

    # tracking-code so google apps know we own the domain.
    (r'^google66ca7050dfade3e4.html',
                TemplateView.as_view(template_name="google134dd4a575584854.html")),
    # tracking-code google api
    (r'^google66ca7050dfade3e4.html',
     TemplateView.as_view(template_name="google134dd4a575584854.html")),
    (r'^inspiration/',
            InspirationPageView.as_view(),
            {},
            'inspiration_page'),
    (r'^like/$',
            LikeView.as_view(),
            {},
            'api_like_view'),

    (r'^dashboard/$',
            DashboardView.as_view(), {},
            'dashboard'),

    (r'^search/',
            TemplateView.as_view(template_name="search.html"),
            {},
            'search'),
    url(r'^',
            include('cities_urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
     {'sitemaps': sitemaps}),
    # accounts/profile, should always be at the end. since a user may set a
    # profile url that match another url -> if it's not at the end it may
    # overwrite it.
    url(r'^',
        include('accounts.urls')),
    )

if settings.DEVELOPMENT:
    urlpatterns += patterns('django.views.static',
                            url(r'^static/(?P<path>.*)$', 'serve'),
                            url(r'^media/(?P<path>.*)$',
                                'serve', {
                                    'document_root': settings.MEDIA_ROOT,
                                    }),
                            )
