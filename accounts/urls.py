from django.conf.urls.defaults import *
from accounts.views import ServiceCreateView, ServiceListView

urlpatterns = patterns('',    
    (r'^test$', ServiceCreateView.as_view(),{},'service-new'),
    (r'^test2/$', ServiceListView.as_view()),           
)

