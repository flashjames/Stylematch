from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView, ServicesView, EditProfileView, DisplayProfileView

urlpatterns = patterns('',   
    (r'^edit$', EditProfileView.as_view(),{},'profile_edit'),
    (r'^(?P<slug>\w+)/$', DisplayProfileView.as_view(),{},'profile_display'), 
    (r'^add-service$', ServicesView.as_view(),{},'profiles_add_service'),
    (r'^list-services$', ServiceListView.as_view(), {}, 'profiles_list_services'),
)

