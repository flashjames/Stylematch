from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView, ServicesView, EditProfileView, DisplayProfileView, CurrentUserProfileView, RedirectToProfileView

urlpatterns = patterns('',   
    (r'^p/edit$', EditProfileView.as_view(),{},'profile_edit'),
    (r'^p/(?P<slug>\w+)/$', DisplayProfileView.as_view(),{},'profile_display_with_profile_url'),
    (r'^p/(?P<slug>\w+)$', CurrentUserProfileView.as_view(),{},'profile_display_without_profile_url'), 
    (r'^profile$', RedirectToProfileView.as_view(),{},'profile_display_redirect'),
    (r'^p/add-service$', ServicesView.as_view(),{},'profiles_add_service'),

    # remove these two asap
    (r'^p/add-service2$', ServiceCreateView.as_view(),{},'nana'),
    (r'^p/list-services$', ServiceListView.as_view(), {}, 'profiles_list_services'),
)

