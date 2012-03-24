# Django settings for MYPROJECT project.
import sys
import os

from path import path

SETTINGS_FILE_FOLDER = path(__file__).parent.abspath()
sys.path.append(SETTINGS_FILE_FOLDER.joinpath("../libs").abspath())

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ("127.0.0.1", "localhost")

ADMINS = (
    ("Devendra K Rane", "ranedk@gmail.com"),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'myproject',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'asd',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.

#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Asia/Calcutta'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SETTINGS_FILE_FOLDER,'../static')
STATIC_PATH = '/static'
SITE_NAME = 'www.myproject.com'
SITE_URL = 'www.myproject.com'

#AUTH_PROFILE_MODULE = 'core.UserProfile'
#LOGIN_REDIRECT_URL = '/accounts/login/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'w%_%(hu!pfu*99i%$^*($%#@#%@@#$FD$%^$%TR%YWET'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
   SETTINGS_FILE_FOLDER.joinpath("templates"),
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes', 
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'django.contrib.comments',
    'django.contrib.humanize',
    
    'south', #Django South Tutorial: Migration of modified models : http://south.aeracode.org/docs/tutorial/part1.html
    
    'core',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",

    "putils.context_processor",
)

# python -m smtpd -n -c DebuggingServer localhost:1025
DEFAULT_FROM_EMAIL = "bot@glitterbug.in"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_PASSWORD = 'WJdb5yDp'
EMAIL_HOST_USER = 'bot@glitterbug.in' 
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

try:
    from local_settings import *
except ImportError: pass
