from django.conf.urls.defaults import *
from accounts.views import ServicesView, EditProfileView, DisplayProfileView, CurrentUserProfileView, RedirectToProfileView

from accounts.views import OpenHoursView

urlpatterns = patterns('',   
    (r'^p/edit$', EditProfileView.as_view(),{},'profile_edit'),
    (r'^p/(?P<slug>\w+)/$', DisplayProfileView.as_view(),{},'profile_display_with_profile_url'),
    (r'^p/(?P<slug>\w+)$', CurrentUserProfileView.as_view(),{},'profile_display_without_profile_url'), 
    (r'^profile$', RedirectToProfileView.as_view(),{},'profile_display_redirect'),
    (r'^p/add-service$', ServicesView.as_view(),{},'profiles_add_service'),


    (r'^add-hours$', OpenHoursView.as_view(),{},'profiles_add_hours'),
)

