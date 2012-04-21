from django.conf.urls.defaults import *
from fileupload.views import PictureCreateView, PictureDeleteView

urlpatterns = patterns('',
    (r'^upload-images/$', PictureCreateView.as_view(), {}, 'upload-images'),
    (r'^delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), {}, 'upload-delete'),
)

