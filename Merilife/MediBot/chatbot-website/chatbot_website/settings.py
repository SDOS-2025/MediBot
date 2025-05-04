import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'medico_db',  # Change this to your actual database name
        'USER': 'root',  # MySQL username (usually 'root' for local development)this
        'PASSWORD': '45221313',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'medico_db',
#         'USER': 'medico_user',
#         'PASSWORD': 'strongpassword',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         }
#     }
# }


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot',
    'behave_django',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Move this BEFORE your custom middleware
    'chatbot.middleware.AuthenticationMiddleware',  # Your custom middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour session lifetime

ROOT_URLCONF = 'chatbot_website.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chatbot_website.wsgi.application'
ASGI_APPLICATION = 'chatbot_website.asgi.application'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'chatbot/static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

# deeeeeecod
DEBUG = True
# huggingface-cli login
# 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
import secrets
keyy=secrets.token_urlsafe()
print(keyy)
SECRET_KEY = keyy


# AUTH_USER_MODEL = 'chatbot.SystemUser'
AUTHENTICATION_BACKENDS = [
    'chatbot.backends.UIDAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # Keep this as fallback
]

AUTH_USER_MODEL = 'chatbot.CustomUser'

X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
# settings.py
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES['default']['TEST'] = {
    'NAME': 'test_db.sqlite3',
}
# Optional: Enable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
# Set testing mode
TESTING = True
SILENCED_SYSTEM_CHECKS = ['auth.E003', 'auth.E004']  # Temporarily silence auth warnings
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# At the top with other path configurations
BASE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Then later in the testing section:
if TESTING:
    MEDIA_ROOT = os.path.join(BASE_MEDIA_ROOT, 'test')
    # Optionally add automatic cleanup
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    MEDIA_ROOT = BASE_MEDIA_ROOT
    # Production storage configuration
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'