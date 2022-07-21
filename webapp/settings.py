# Django settings for cbmonitor project.
from os import path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ("cbmonitor.sc.couchbase.com", "127.0.0.1", "172.23.98.70")

INTERNAL_IPS = ("127.0.0.1",)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/opt/cbmonitor/cbmonitor.db",
        "OPTIONS": {
            "timeout": 30,
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11411",
        "TIMEOUT": None,
        "OPTIONS": {
            "MAX_ENTRIES": 100000,
        }
    }
}

# Local time zone for this installation.
TIME_ZONE = None

# Language code for this installation.
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = path.join(path.dirname(path.abspath(__file__)), "media")

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = ""

# URL prefix for static files.
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    path.join(path.dirname(__file__), "cbmonitor/static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don"t share it with anybody.
SECRET_KEY = "c9j1v$z(t#-(_%i38wu@(n+&amp;^w6ki@$c!k0b80ts8=(@hb+*ln"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "urls"

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "wsgi.application"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cbmonitor",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s - %(message)s",
            "datefmt": "[%d/%b/%Y %H:%M:%S]"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "null": {
            "level": "DEBUG",
            "class": "django.utils.log.NullHandler",
        },
        "request_handler": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/tmp/cbmonitor.log",
            "formatter": "default",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["request_handler"],
            "level": "ERROR",
            "propagate": True
        },
    }
}
