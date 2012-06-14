from django.conf.urls.defaults import *
from accounts.api import ServiceResource, PictureResource, ProfileResource
from accounts.views import (ServicesView,
                            EditProfileView,
                            DisplayProfileView,
                            RedirectToProfileView,
                            EditImagesView,
                            OpenHoursView,
                            SaveProfileImageView,
                            CropPictureView)
from tastypie.api import Api

profile_api = Api(api_name='profile')
profile_api.register(ServiceResource())
profile_api.register(PictureResource())
profile_api.register(ProfileResource())

urlpatterns = patterns('',
    # need to be first, or redirection to profile wont work.
    (r'^profile/$',
            RedirectToProfileView.as_view(),
            {},
            'profile_display_redirect'),
    (r'^profile/edit/$',
            EditProfileView.as_view(),
            {},
            'profile_edit'),
    (r'^profile/edit-services/$',
            ServicesView.as_view(),
            {},
            'profiles_edit_services'),
    (r'^profile/edit-images/$',
            EditImagesView.as_view(),
            {},
            'edit_images'),
    (r'^profile/save-profile-image/$',
            SaveProfileImageView.as_view(),
            {},
            'save_profile_image'),
    (r'^profile/crop-image/$',
            CropPictureView.as_view(),
            {},
            'crop_image'),
    (r'^profile/add-hours/$',
            OpenHoursView.as_view(),
            {},
            'profiles_add_hours'),
    (r'^api/',
            include(profile_api.urls)),
    (r'^(?P<slug>\w+)/$',
            DisplayProfileView.as_view(),
            {},
            'profile_display_with_profile_url'),
)
