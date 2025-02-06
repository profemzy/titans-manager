import os
import sys
from socket import gethostbyname, gethostname
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure#")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = bool(os.environ.get("DEBUG", default=True))


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "tms.ops.infotitans.ca",
    gethostname(),  # Add hostname
    gethostbyname(gethostname()),  # Add host IP
]

# Kubernetes sets POD_IP env variable for pods
POD_IP = os.getenv("POD_IP")
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
    # Branding
    "site_title": "InfoTitans",
    "site_header": "InfoTitans Portal",
    "site_brand": "InfoTitans",
    "welcome_sign": "Welcome to InfoTitans",
    # "copyright": "© 2025 InfoTitans Ltd",
    "site_logo": "img/infotitans-logo.svg",
    "site_logo_classes": "elevation-2",
    # Search and Navigation
    "search_model": ["core.User", "core.Client", "core.Project"],
    "user_avatar": None,
    # Top Menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {
            "name": "Support",
            "url": "https://github.com/profemzy/titans-manager/issues",
            "new_window": True,
        },
        {"model": "core.User"},
    ],
    # UI Settings
    "show_sidebar": True,
    "navigation_expanded": True,
    "sidebar_fixed": True,
    "sidebar_collapse": False,
    "related_modal_active": True,
    # Visual Customization
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    # Icons (using consistent Font Awesome styling)
    "icons": {
        "auth": "fas fa-shield-alt",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.client": "fas fa-building",
        "core.project": "fas fa-project-diagram",
        "core.task": "fas fa-tasks",
        "core.income": "fas fa-hand-holding-usd",
        "core.expense": "fas fa-file-invoice-dollar",
        "core.invoice": "fas fa-file-invoice",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    # Dark mode settings
    "dark_mode_theme": None,
    "site_logo": "img/infotitans-logo.svg",
}

JAZZMIN_UI_TWEAKS = {
    # Text Settings
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    # Color Scheme (Light Mode)
    "brand_colour": "navbar-light",
    "accent": "accent-primary",
    "navbar": "navbar-light bg-white",
    "sidebar": "sidebar-light-primary",
    # Layout Settings
    "layout_boxed": False,
    "navbar_fixed": True,
    "footer_fixed": True,
    "sidebar_fixed": True,
    # Sidebar Navigation Style
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    # Theme and Borders
    "theme": "cerulean",  # Clean, light theme
    "no_navbar_border": False,
    # Button Styling
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = "TitansManager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
        "NAME": os.getenv("DATABASE_NAME", "tmsdb"),
        "USER": os.getenv("DATABASE_USERNAME", "dbuser"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "dbpassword"),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
    }
}

AUTH_USER_MODEL = "core.User"

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

STATIC_URL = "/static/"
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, "staticfiles"))

# Extra places for collectstatic to find static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "TitansManager API",
    "DESCRIPTION": "API documentation for TitansManager application",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "http://localhost, http://127.0.0.1"
).split(",")

CSRF_COOKIE_SECURE = not DEBUG
CSRF_USE_SESSIONS = True

# Additional Security Settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG

# Session Management Settings
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Session Security Settings
SESSION_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = "Lax"  # Protection against CSRF

# Session timeout settings
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# Login redirect settings
LOGIN_REDIRECT_URL = "/titans-admin/"
LOGIN_URL = "/titans-admin/login/"
LOGOUT_REDIRECT_URL = "/"

# Timezone settings
TIME_ZONE = "America/Vancouver"
USE_TZ = True
USE_L10N = True
USE_I18N = True

AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME", "DEFAULT")
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY", "DEFAULT")
AZURE_RECEIPT_CONTAINER = os.environ.get("AZURE_RECEIPT_CONTAINER", "tms-receipts")
AZURE_EXPIRATION_SECS = int(os.environ.get("AZURE_EXPIRATION_SECS", 86400))

# Default file storage
DEFAULT_FILE_STORAGE = "custom_storage.AzureReceiptStorage"

ENVIRONMENT = os.environ.get("DJANGO_ENV", "production")
