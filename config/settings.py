"""
Django settings for the School Management System.
Environment-driven via django-environ (see .env.example).
"""

import os
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

# --- Core ---
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip() or "insecure-dev-key"
DEBUG = env.bool("DEBUG", default=False)
_raw_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "").strip()
if _raw_allowed_hosts:
    ALLOWED_HOSTS = [h.strip() for h in _raw_allowed_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", ".vercel.app", "*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    # local apps
    "core",
    "accounts",
    "academics",
    "students",
    "attendance",
    "activities",
    "communications",
    "reporting",
    "fees",
    "public_site",
    "warehouse",
    "ai_assistants",
    "admissions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.AuditLogMiddleware",  # captures request.user/IP for audit logs
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

import sys

# --- Database ---
_raw_db_url = os.environ.get("DATABASE_URL", "").strip()
if "test" in sys.argv or "pytest" in sys.modules or os.environ.get("USE_SQLITE"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif _raw_db_url:
    DATABASES = {"default": env.db_url_config(_raw_db_url)}
else:
    _sqlite_path = (
        Path("/tmp/db.sqlite3") if os.environ.get("VERCEL") else BASE_DIR / "db.sqlite3"
    )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "school_mgt_db",
            "USER": "school_mgt_user",
            "PASSWORD": "Esther456@",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static / media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# NOTE: we deliberately keep django.contrib.auth's built-in User model and
# attach a 1:1 accounts.Profile for role/contact fields, rather than
# swapping AUTH_USER_MODEL. This keeps auth machinery (admin, permissions,
# password reset) stock, and is easy to migrate to a custom user model
# later if multi-tenancy requires it (see README "Assumptions").

# --- DRF ---

# Stage 10: OWASP Baseline (Enabled in prod/secure contexts)
import os

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = (
    os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
)
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Add REST_FRAMEWORK throttling defaults


import sys

TESTING = "pytest" in sys.modules

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": (
        []
        if TESTING
        else [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ]
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100000/day" if TESTING else "100/day",
        "user": "100000/day" if TESTING else "1000/day",
        "auth": "100000/minute" if TESTING else "5/minute",
        "public_write": "100000/hour" if TESTING else "10/hour",
        "register": "100000/hour" if TESTING else "10/hour",
        "admin_sensitive": "100000/day" if TESTING else "100/day",
    },
}

CACHES = (
    {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
    if TESTING
    else {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "school-management-system-local",
        }
    }
)
# --- Celery ---
CELERY_BROKER_URL = (
    os.environ.get("CELERY_BROKER_URL", "").strip() or "redis://localhost:6379/1"
)
CELERY_RESULT_BACKEND = (
    os.environ.get("CELERY_RESULT_BACKEND", "").strip() or "redis://localhost:6379/2"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# --- Email (used by Celery reminder tasks) ---
EMAIL_HOST = os.environ.get("EMAIL_HOST", "").strip() or "localhost"
_raw_email_port = os.environ.get("EMAIL_PORT", "").strip()
EMAIL_PORT = int(_raw_email_port) if _raw_email_port.isdigit() else 25
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "").strip()
_email_tls_str = os.environ.get("EMAIL_USE_TLS", "").strip().lower()
EMAIL_USE_TLS = False if _email_tls_str in ("false", "0", "no") else True
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL", "").strip() or "no-reply@school.example.com"
)

# --- File upload limits (assignments: max 10MB) ---
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# --- Sentry (optional) ---
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[DjangoIntegration()], traces_sample_rate=0.2
    )

# Allow frontend requests
CORS_ALLOW_ALL_ORIGINS = True
