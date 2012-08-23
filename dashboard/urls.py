# coding:utf-8
from django.conf.urls.defaults import *
from dashboard.views import DashboardView, InviteFriendsView
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (u'^översikt/invitecode/$',
            InviteFriendsView.as_view(),
            {},
            'dashboard-invitecode'),
    (u'^översikt/$',
            DashboardView.as_view(), {},
            'dashboard'),
    (u'^översikt-klient/',
     TemplateView.as_view(template_name="client_dashboard.html"),
     {},
     'client_dashboard'),

)
