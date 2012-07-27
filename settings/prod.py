from .base import *

DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = False
PRODUCTION = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_stylematch',
        'USER': 'djangostylematch',
        'PASSWORD': 'KALSl23lKL31skk1',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        },
    }
}

# Sentry (loggin) DSN value, the key used to send logs to Sentry
SENTRY_DSN = 'http://3d949b7351ba4e4e803fdd131ee267b7:4c3da4fdcf7d40a785e18f9f75badffe@sentry.stylematch.se/1'

LOGGING = SENTRY_LOGGING

# Add raven to the list of installed apps (sentry logging client)
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django',
    )

STATIC_URL = 'http://stylematch.s3-website-eu-west-1.amazonaws.com/'
MEDIA_URL = 'http://stylematch.s3-website-eu-west-1.amazonaws.com/'

# reset, STATIC_URL has changed
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
JQUERY_SCRIPT = STATIC_URL + "js/jquery/jquery-1.7.1.js"
GALLERIA_URL = STATIC_URL + "js/galleria/src/"

DEFAULT_FILE_STORAGE = STATICFILES_STORAGE = ('storages.backends'
                                              '.s3boto.S3BotoStorage')

AWS_STORAGE_BUCKET_NAME = 'stylematch'

UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS

# reset, MEDIA_URL has changed
FULL_PATH_USER_IMGS = os.path.join(MEDIA_URL, PATH_USER_IMGS)

# Google analytics key
GOOGLE_ANALYTICS_KEY = "UA-31224755-1"

# Google API key
GOOGLE_API_KEY = "AIzaSyDA3wWYlEqxN178D42MBkL2wcZwZCCtqwk"

# Kissmetrics Key
KISSMETRICS_KEY = "6baa0dd7f1e6af4d6ab136449204547afab5afaf"
