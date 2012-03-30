from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView, ServicesView

urlpatterns = patterns('',    
    (r'^add-service$', ServicesView.as_view(),{},'profiles_add_service'),
    (r'^list-services$', ServiceListView.as_view(), {}, 'profiles_list_services'),
)

