# coding:utf-8
from django.conf.urls.defaults import *
from dashboard.views import DashboardView, InviteCodeView, MessageReadView

urlpatterns = patterns('',
    (u'^översikt/invitecode/$',
            InviteCodeView.as_view(),
            {},
            'dashboard-invitecode'),
    (u'^översikt/meddelande-läst/$',
            MessageReadView.as_view(),
            {},
            'dashboard-message-read'),
    (u'^översikt/$',
            DashboardView.as_view(), {},
            'dashboard'),
)
