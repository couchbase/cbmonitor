# Django settings for cbmonitor project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cbmonitor.db'
    }
}

# Local time zone for this installation.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation.
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = ''

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static').replace('\\', '/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c9j1v$z(t#-(_%i38wu@(n+&amp;^w6ki@$c!k0b80ts8=(@hb+*ln'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'httpproxy',
    'pyjade',
    'litmus',
    'demos',
    'reports',
)

# Proxy settings
PROXY_DOMAIN = 'localhost'
PROXY_PORT = 3133

# Couchbase Single Server
URI = "http://perf-cabinet.hq.couchbase.com:5984/"
