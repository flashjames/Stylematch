from .base import *

DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = False
STAGING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR + '/database/test.db',
        'TEST_NAME': PROJECT_DIR + '/database/testest.db',
    }
}

LOGGING = BASE_LOGGING

DEFAULT_FILE_STORAGE = STATICFILES_STORAGE = ('storages.backends'
                                              '.s3boto.S3BotoStorage')

STATIC_URL = 'http://dev-jens.s3-website-eu-west-1.amazonaws.com/'
MEDIA_URL = 'http://dev-jens.s3-website-eu-west-1.amazonaws.com/'

# reset, STATIC_URL has changed
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
GALLERIA_URL = STATIC_URL + "js/galleria/src/"

DEFAULT_FILE_STORAGE = STATICFILES_STORAGE = ('storages.backends'
                                              '.s3boto.S3BotoStorage')

AWS_STORAGE_BUCKET_NAME = 'dev-jens'

UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS

# reset, MEDIA_URL has changed
FULL_PATH_USER_IMGS = os.path.join(MEDIA_URL, PATH_USER_IMGS)
