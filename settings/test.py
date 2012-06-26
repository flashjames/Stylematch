# Settings file optimized for test running. Sets up in-memory database
# and disables South and Sentry for the tests

from .base import *

DEVELOPMENT = True
DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = True

# Use in-memory SQLIte3 database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR + '/database/test.db',
        'TEST_NAME': PROJECT_DIR + '/database/testest.db',
    }
}

# No need to use South in testing
SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

# Don't run functional tests on production server
SKIP_FTS_TESTS = True

# Disable Sentry if it was installed
INSTALLED_APPS = [ app for app in INSTALLED_APPS
    if not app.startswith('raven.') ]
MIDDLEWARE_CLASSES = [ cls for cls in MIDDLEWARE_CLASSES
    if not cls.startswith('raven.') ]
LOGGING = BASE_LOGGING
