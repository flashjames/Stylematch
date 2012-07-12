from django.conf.urls.defaults import *
from dashboard.views import DashboardView, InviteCodeView

urlpatterns = patterns('',
    (r'^dashboard/invitecode/$',
            InviteCodeView.as_view(),
            {},
            'dashboard-invitecode'),
    (r'^dashboard/$',
            DashboardView.as_view(), {},
            'dashboard'),
)
