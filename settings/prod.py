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
SENTRY_DSN = 'http://20195eef47244f21a845b9eaa12a3af3:68325bc8efe64aceaec134815ef41850@www.stylematch.se:9000/1'

LOGGING = SENTRY_LOGGING

# Add raven to the list of installed apps (sentry logging client)
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django',
    )

STATIC_URL = 'http://stylematch.s3-website-eu-west-1.amazonaws.com/'

# reset, STATIC_URL has changed
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
JQUERY_SCRIPT = STATIC_URL + "js/jquery/jquery-1.7.1.js"
GALLERIA_URL = STATIC_URL + "js/galleria/src/"

DEFAULT_FILE_STORAGE = STATICFILES_STORAGE = ('storages.backends'
                                              '.s3boto.S3BotoStorage')

AWS_STORAGE_BUCKET_NAME = 'stylematch'

UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS


# reset, STATIC_URL has changed
FULL_PATH_USER_IMGS = os.path.join(STATIC_URL, PATH_USER_IMGS)