# coding:utf-8
from django.conf.urls.defaults import *
from accounts.api import (ServiceResource,
                          PictureResource,
                          ProfileResource,
                          FeaturedProfileResource,
                          InspirationResource)
from accounts.views import (ServicesView,
                            EditProfileView,
                            DisplayProfileView,
                            RedirectToProfileView,
                            EditImagesView,
                            EditSpecialitiesView,
                            OpenHoursView,
                            SaveProfileImageView,
                            CropPictureView,
                            MakeVisibleView)
from tastypie.api import Api

profile_api = Api(api_name='profile')
profile_api.register(ServiceResource())
profile_api.register(PictureResource())
profile_api.register(ProfileResource())
profile_api.register(FeaturedProfileResource())
profile_api.register(InspirationResource())


urlpatterns = patterns('',
    # need to be first, or redirection to profile wont work.
    (r'^profil/$',
            RedirectToProfileView.as_view(),
            {},
            'profile_display_redirect'),
    (r'^profil/edit/$',
            EditProfileView.as_view(),
            {},
            'profile_edit'),
    (r'^profil/edit-services/$',
            ServicesView.as_view(),
            {},
            'profiles_edit_services'),
    (u'^profil/lägg-upp-bilder/$',
            EditImagesView.as_view(),
            {},
            'edit_images'),
    (u'^profil/förändra-profilbild/$',
            EditImagesView.as_view(),
     {'change_profileimage': True},
            'edit_profileimage'),
    (r'^profil/save-profile-image/$',
            SaveProfileImageView.as_view(),
            {},
            'save_profile_image'),
    (r'^profil/crop-image/$',
            CropPictureView.as_view(),
            {},
            'crop_image'),
    (r'^profil/add-hours/$',
            OpenHoursView.as_view(),
            {},
            'profiles_add_hours'),
    url(r'^profil/specialities/$',
            EditSpecialitiesView.as_view(),
            name='profiles_edit_specialities'),
    (r'^api/',
            include(profile_api.urls)),

    (r'^admin/makevisible/(?P<slug>\d+)/$',
            MakeVisibleView.as_view(),
            {},
            'makevisible'),
    (r'^(?P<slug>[-\w]+)/$',
            DisplayProfileView.as_view(),
            {},
            'profile_display_with_profile_url'),
)
