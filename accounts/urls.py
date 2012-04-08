from django.conf.urls.defaults import *
from accounts.views import ServicesView, EditProfileView, DisplayProfileView, CurrentUserProfileView, RedirectToProfileView, PicturesView

from accounts.views import OpenHoursView

from tastypie.api import Api
from accounts.api import ServiceResource, PictureResource
profile_api = Api(api_name='profile')
profile_api.register(ServiceResource())
profile_api.register(PictureResource())

urlpatterns = patterns('',   
    (r'^p/edit$', EditProfileView.as_view(),{},'profile_edit'),
    (r'^p/(?P<slug>\w+)/$', DisplayProfileView.as_view(),{},'profile_display_with_profile_url'),
    (r'^p/(?P<slug>\w+)$', CurrentUserProfileView.as_view(),{},'profile_display_without_profile_url'), 
    (r'^profile$', RedirectToProfileView.as_view(),{},'profile_display_redirect'),
    (r'^p/edit-services$', ServicesView.as_view(),{},'profiles_edit_services'),
    (r'^p/edit-images$', PicturesView.as_view(),{},'profiles_edit_images'),
    (r'^add-hours$', OpenHoursView.as_view(),{},'profiles_add_hours'),
    (r'^api/', include(profile_api.urls)),
)

