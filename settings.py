# Django settings
import os
import iptools

import socket

if socket.gethostname() == 'avizera-deploy':
    DEBUG = TEMPLATE_DEBUG = False
else:
    DEBUG = TEMPLATE_DEBUG = True

INTERNAL_IPS = iptools.IpRangeList(
    '127.0.0.1',                # single ip
    '192.168/16',               # CIDR network block
    ('10.0.0.1', '10.0.0.19'),  # arbitrary range
)

# Absolute path to project directory.
# If you rename/remove this you will break things
PROJECT_DIR = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Jenso', 'jenso1988@gmail.com'),
)

MANAGERS = ADMINS

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': PROJECT_DIR + '/database/test.db',
            }
        }
else:
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


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Stockholm'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sv'

SITE_ID = 1
SITE_DOMAIN = 'stylematch.se'
SITE_NAME = 'Stylematch'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_DOC_ROOT = os.path.join(PROJECT_DIR, "static/")


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"

if DEBUG:
    STATIC_URL = '/static/'
else:
    STATIC_URL = 'http://stylematch.s3-website-eu-west-1.amazonaws.com/'

STATIC_ROOT = os.path.join(PROJECT_DIR,"static/")

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_DIR+"/media/",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '11ju*buxq(sqnmg%!^za&&v_+0=j#p2)iuhu+o6sw+lcdyfytl'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    PROJECT_DIR+"/templates/",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'debug_toolbar',
    'social_auth',
    'registration',
    'django_extensions',
    'south',
    'bootstrap',
    'braces',
    'index',
    'accounts',
    'storages',
    'defaultsite',
    'django_su',
)

### S3 storage - production

if not DEBUG:
    DEFAULT_FILE_STORAGE = STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
### END S3 storage

### Amazon credentials and mail

# credentials should maybe be set as environment variables on production server?
# -> more secure.
AWS_ACCESS_KEY_ID = 'AKIAJHCGEY6XAXXOSYXA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'stylematch'
#AWS_STORAGE_BUCKET_NAME = 'dev-jens'
EMAIL_BACKEND = 'django_ses.SESBackend'
# SERVER_EMAIL, default error message email.
# DEFAULT_FROM_EMAIL, all other mails
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'hampus.bergqvist@stylematch.se'

### END Amazon credentials


### social auth

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)


FACEBOOK_APP_ID              = '279761435376574'
FACEBOOK_API_SECRET          = 'c3325b623f9f09303004b77aed231a71'

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login-error/'


"""
Can be used to style social_auth in templates

TEMPLATE_CONTEXT_PROCESSORS = (
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'django.contrib.auth.context_processors.auth',
)
"""
SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
SOCIAL_AUTH_EXTRA_DATA = False
SOCIAL_AUTH_EXPIRATION = 'expires'
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_ERROR_KEY = 'socialauth_error'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
# END social_auth

# inform where user profile model is defined
AUTH_PROFILE_MODULE = "accounts.UserProfile"

### django-registration

# number of days users will have to activate their accounts after registering
ACCOUNT_ACTIVATION_DAYS = 7

# END django-registration

###Logging local
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
                }
            },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
                },
            }
        }
### Logging with Sentry, production
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
            },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
            },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.handlers.SentryHandler',
                },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
                },
            },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
                },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
                },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
                },
            },
        }

    # Sentry (loggin) DSN value, the key used to send logs to Sentry
    SENTRY_DSN = 'http://20195eef47244f21a845b9eaa12a3af3:68325bc8efe64aceaec134815ef41850@www.stylematch.se:9000/1'

    # Add raven to the list of installed apps (sentry logging client)
    INSTALLED_APPS = INSTALLED_APPS + (
        # ...
        'raven.contrib.django',
        )

# Debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    }

# Galleria, jquery

# should use some cdn in production
JQUERY_SCRIPT = STATIC_URL + "js/jquery/jquery-1.7.1.js"

GALLERIA_URL = STATIC_URL + "js/galleria/src/"

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'index.context_processors.jquery_script',
    'index.context_processors.galleria_urls',
    'django.core.context_processors.static', #used to access STATIC_URL in templates
    )

# Paths to user uploaded images, used in fileupload app

PATH_USER_IMGS = "user-imgs/"
if DEBUG:
    UPLOAD_PATH_USER_IMGS = "media/" + PATH_USER_IMGS
else:
    UPLOAD_PATH_USER_IMGS = PATH_USER_IMGS

MAX_IMAGE_SIZE = 20 * 1024 * 1024
FULL_PATH_USER_IMGS = os.path.join(STATIC_URL, PATH_USER_IMGS)

# use gmail as smtp server, should use own smtp server for this later?
"""
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'hello@stylematch.se'
EMAIL_HOST_PASSWORD = 'kj234kjklJKLj324lk1jKlkj231'
EMAIL_PORT = 587
"""
