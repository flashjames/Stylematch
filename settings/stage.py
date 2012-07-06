from .base import *

DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = False
STAGING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stylebackup',
        'USER': 'root',
        'PASSWORD': 'bulle',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        },
    }
}

MEDIA_URL = 'http://stylematch.s3-website-eu-west-1.amazonaws.com/'
DEFAULT_FILE_STORAGE = ('storages.backends.s3boto.S3BotoStorage')
AWS_STORAGE_BUCKET_NAME = 'stylematch'

LOGGING = BASE_LOGGING

UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS
FULL_PATH_USER_IMGS = os.path.join(MEDIA_URL, PATH_USER_IMGS)
