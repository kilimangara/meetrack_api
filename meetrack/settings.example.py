"""
Django settings for meetrack project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'anen3z#=i$41626%9xhso+ina8_s5^$v+jtz1+9v36d!x+c+ij'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'common_fields',
    'authtoken',
    'registration',
    'meetings',
    'users',
    'msg_queue',
]
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meetrack.urls'

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

WSGI_APPLICATION = 'meetrack.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'meetrack',
        'USER': 'gaz',
        'PASSWORD': 'sudo',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
# LOGGING
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'django.request': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authtoken.authentication.RedisTokenAuthentication'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # 'DATETIME_FORMAT': '%s',
    # 'DATETIME_INPUT_FORMATS': ['%S'],
}

SMS_AUTH = {
    'REQUEST_URL': 'https://api.twilio.com/2010-04-01/Accounts/ACb3942b775d299a83395ac07b89c8890e/Messages.json',
    'ACCOUNT_SID': 'ACb3942b775d299a83395ac07b89c8890e',
    'AUTH_TOKEN': 'b3855a93c588996d3be0de9dba142d49',
    'FROM_NUMBER': '+12054154471',
    'ATTEMPTS_LIMIT': 5,
    'CODE_LIFE_TIME': 5 * 60,
    'ATTEMPTS_LIFE_TIME': 10,
    'DEBUG_CODE': '00000',
}

REDIS = {
    'HOST': 'localhost',
    'PORT': '6379',
    'PASSWORD': None,
    'DB': 1,
}
RABBITMQ = {
    'HOST': 'localhost',
    'PORT': 5672,
    'user': 'guest',
    'password': 'guest',
    'EXCHANGE': 'meetrack',
    'PUSHER_KEY': 'pusher',
    'PUSHER_QUEUE': 'meetrack_pusher',
    'SOCKET_KEY': 'socket',
    'SOCKET_QUEUE': 'meetrack_socket',
}

# STORAGE
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STORAGE_URL = 'http://localhost:8000' + MEDIA_URL
