from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView, ServicesView, EditProfileView, DisplayProfileView, CurrentUserProfileView

urlpatterns = patterns('',   
    (r'^p/edit$', EditProfileView.as_view(),{},'profile_edit'),
    (r'^p/(?P<slug>\w+)/$', DisplayProfileView.as_view(),{},'profile_display'),
    (r'^profile$', CurrentUserProfileView.as_view(),{},'profile_display'), 
    (r'^p/add-service$', ServicesView.as_view(),{},'profiles_add_service'),
    (r'^p/list-services$', ServiceListView.as_view(), {}, 'profiles_list_services'),
)

