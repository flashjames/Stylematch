# coding:utf-8
from django.conf.urls.defaults import *
from dashboard.views import DashboardView, InviteFriendsView

urlpatterns = patterns('',
    (u'^översikt/invitecode/$',
            InviteFriendsView.as_view(),
            {},
            'dashboard-invitecode'),
    (u'^översikt/$',
            DashboardView.as_view(), {},
            'dashboard'),
)
