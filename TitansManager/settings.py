import os
import sys
from socket import gethostbyname, gethostname
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-1ffaq*8vo0!kjzo*u$u7p7(8i(h#5qo!2lyh9e=ohpx2nz4ro_")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = bool(os.environ.get("DEBUG", default=0))


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    'tms.ops.infotitans.ca',
    gethostname(),  # Add hostname
    gethostbyname(gethostname()),  # Add host IP
]

# Kubernetes sets POD_IP env variable for pods
POD_IP = os.getenv('POD_IP')
if POD_IP:
    ALLOWED_HOSTS.append(POD_IP)


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",
    "rangefilter",
    "rest_framework",
    "rest_framework_simplejwt",
    "django.contrib.humanize",
    "drf_spectacular",
    "django_filters",
    "core",
]

JAZZMIN_SETTINGS = {
    "site_title": "TitansManager Admin",
    "site_header": "TitansManager",
    "site_brand": "TitansManager",
    "welcome_sign": "Welcome to the TitansManager Admin Portal",
    "copyright": "TitansManager Ltd",
    # Logo to use for your site, must be present in static files, used for brand on top left
    # "site_logo": "books/img/logo.png",
    "search_model": ["core.User", "core.Client", "core.Project"],
    "user_avatar": None,

    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/yourusername/TitansManager/issues", "new_window": True},
        {"model": "core.User"},
    ],

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
     "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.client": "fas fa-building",
        "core.project": "fas fa-project-diagram",
        "core.task": "fas fa-tasks",
        "core.income": "fas fa-money-bill-wave",
        "core.expense": "fas fa-file-invoice-dollar",
        "core.invoice": "fas fa-file-invoice",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": True,

    "sidebar_fixed": True,

    # Whether to enable collapsing the sidebar
    "sidebar_collapse": False,

    # Whether to start the sidebar collapsed
    "sidebar_collapse_pin": False,

    # Whether to enable collapsing the menu
    "collapse_navbar": False,

    # Dark mode
    "dark_mode_theme": None,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = "TitansManager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "TitansManager.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('DATABASE_NAME', 'tmsdb'),
        "USER": os.getenv('DATABASE_USERNAME', 'dbuser'),
        "PASSWORD": os.getenv('DATABASE_PASSWORD', 'dbpassword'),
        "HOST": os.getenv('DATABASE_HOST', '127.0.0.1'),
        "PORT": os.getenv('DATABASE_PORT', 5432),
    }
}

AUTH_USER_MODEL = 'core.User'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))

# Extra places for collectstatic to find static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'TitansManager API',
    'DESCRIPTION': 'API documentation for TitansManager application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1').split(',')
# CSRF_TRUSTED_ORIGINS = ["https://*.ops.infotitans.ca"]
CSRF_COOKIE_SECURE = not DEBUG
CSRF_USE_SESSIONS = True

# Additional Security Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG

# Session Management Settings
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Session Security Settings
SESSION_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Protection against CSRF

# Session timeout settings
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# Login redirect settings
LOGIN_REDIRECT_URL = '/titans-admin/'
LOGIN_URL = '/titans-admin/login/'
LOGOUT_REDIRECT_URL = '/'

# Timezone settings
TIME_ZONE = 'America/Vancouver'
USE_TZ = True
USE_L10N = True
USE_I18N = True

AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', 'DEFAULT')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', 'DEFAULT')
AZURE_RECEIPT_CONTAINER = os.environ.get('AZURE_RECEIPT_CONTAINER', 'tms-receipts')
AZURE_EXPIRATION_SECS = int(os.environ.get('AZURE_EXPIRATION_SECS', 86400))

# Default file storage
DEFAULT_FILE_STORAGE = 'custom_storage.AzureReceiptStorage'

ENVIRONMENT = os.environ.get('DJANGO_ENV', 'production')

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
