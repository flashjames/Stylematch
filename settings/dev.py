from .base import *
import os

DEVELOPMENT = True
DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR + '/database/test.db',
        'TEST_NAME': PROJECT_DIR + '/database/testest.db',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = BASE_LOGGING

# set up Django Debug Toolbar if installed
try:
    import debug_toolbar
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda *args, **kwargs: True
    }
except ImportError:
    pass

# store sorl-thumbnail cache under /media dir
UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS
