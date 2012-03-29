from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView

urlpatterns = patterns('',    
    (r'^add-service$', ServiceCreateView.as_view(),{},'profiles_add_service'),
    (r'^list-services$', ServiceListView.as_view(), {}, 'profiles_list_services'),
)

