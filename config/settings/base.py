from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

APP_NAME = 'ROInsight'
APP_SLOGAN="Hospitality Intelligance"
APP_LOGO = "img/logo.svg"

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'unsafe-demo-secret-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    'apps.core.common.apps.CoreCommonConfig',
    'apps.core.security.apps.CoreSecurityConfig',
    'apps.properties.core.apps.PropertiesCoreConfig',
    'apps.usermanagement.users.apps.UserManagementUsersConfig',
    'apps.usermanagement.profiles.apps.UserManagementProfilesConfig',
    'apps.usermanagement.roles.apps.UserManagementRolesConfig',
    'apps.dashboard.home.apps.DashboardHomeConfig',
    'apps.analytics.kpi.apps.AnalyticsKPIConfig',
    'apps.notifications.inbox.apps.NotificationsInboxConfig',
    'apps.notifications.announcements.apps.NotificationsAnnouncementsConfig',
    'apps.powerbi.embedded.apps.PowerBIEmbeddedConfig',
    'apps.dataops.files.apps.DataOpsFilesConfig',
    'apps.settings.mappings.apps.SettingsMappingsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.common.context_processors.global_ui',
                'apps.core.common.context_processors.app_navigation',
                "apps.powerbi.embedded.context_processors.report_menu",
            ],
        },
    },
]

DATABASES = {
    # 'default': dj_database_url.config(
    #     default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    #     conn_max_age=600,
    #     conn_health_checks=True,
    # ),
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "django"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "options": f"-c search_path={os.getenv('DB_SCHEMA', 'core')},public",
        },
    },
}

# Dynamic app -> database mapping
APP_DATABASE_MAPPING = {
    # "settingsmappings": "reports_db",
}

DATABASE_ROUTERS = [
    # "config.db_routers.DynamicAppRouter",
]

AUTH_USER_MODEL = 'usercore.User'
AUTHENTICATION_BACKENDS = [
    'apps.usermanagement.users.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dubai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / os.getenv('STATIC_ROOT', 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'login'
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'HorizonBI <noreply@example.com>')

SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = True

TAILWIND_USE_CDN = os.getenv('TAILWIND_USE_CDN', 'True').lower() == 'true'
POWERBI_TENANT_ID = os.getenv('POWERBI_TENANT_ID', '')
POWERBI_CLIENT_ID = os.getenv('POWERBI_CLIENT_ID', '')
POWERBI_CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET', '')
POWERBI_SCOPE = os.getenv('POWERBI_SCOPE', 'https://analysis.windows.net/powerbi/api/.default')
POWERBI_API_BASE_URL = os.getenv('POWERBI_API_BASE_URL', 'https://api.powerbi.com/v1.0/myorg')
POWERBI_AUTHORITY_URL = os.getenv('POWERBI_AUTHORITY_URL', 'https://login.microsoftonline.com')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
