"""
Django settings for volunteerapi project.

Generated by 'django-admin startproject' using Django 4.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = '%s/volunteer/static/' % BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t5ej*1f*$3n=xqas@3bo+2aoorwg1qvfk$4(uhh9rqfy57#q2k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

import pymysql

pymysql.install_as_MySQLdb()

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'volunteer',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'drf_yasg',
    'oauth2_provider',
    'corsheaders',
]

JAZZMIN_SETTINGS = {
    'site_title': 'Volunteer Admin',
    'site_header': 'Volunteer',
    "site_brand": "Volunteer",
    'welcome_sign': 'Welcome to the Volunteer Administration Site',
    'show_ui_builder': True,
    'topmenu_links': [
            {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
            {"name": "Thống Kê", "url": "http://127.0.0.1:8000/admin/volunteer-stats/", "permissions": ["auth.view_user"]},
            {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
            {'model': 'auth.User'},
            {'app': 'volunteer'},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-blue navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-blue",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "lumen",
    "dark_mode_theme": "superhero",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('oauth2_provider.contrib.rest_framework.OAuth2Authentication',)
}

CKEDITOR_UPLOAD_PATH = "ckeditors/images/"

AUTH_USER_MODEL = 'volunteer.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'volunteerapi.urls'

STATICFILES_DIRS = [
    BASE_DIR / "volunteer/static",
]

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

import cloudinary

cloudinary.config(
    cloud_name="dxpphrk8f",
    api_key="925856721441817",
    api_secret="yxLTnD3LaL3M--_ZZ8-nxNlIA0U",  # Click 'View API Keys' above to copy your API secret
    secure=True
)

WSGI_APPLICATION = 'volunteerapi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'volunteerdb',
        'USER': 'root',
        'PASSWORD': 'Admin@123',
        'HOST': ''  # mặc định localhost
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CLIENT_ID = 'LnWA6PTJxDjLEHhCiW2EpgAPow9Y18cBavUmN0YL'
CLIENT_SECRET = 'PCua6MbQzJtujy6aew1EyVEwwpS1I2FCGbxxSO02Qy2vdQUCB8YrQPOEfWLqrsWtiByzWy3kNhOWZtr0XPDokDO3CdmpS4JWw8IyfL2DLNyekL0Y76g71U94Kpsm0wAK'

CLIENT_ID_PAYPAL ='AU2F14M5fgAunODLfDultP3_fh5B2b0dXjFtKafC_xU0WPxqZnyZSx7VVN-RFcVeq6j8pyRdvAwd1UJV'
CLIENT_SECRET_PAYPAL = 'EIl_7Sy_AoyBdBuYPNNn8x7_fCa6csfddkokUIuKvcfPu5sbZZqJcz6k_v366Bk2h6HRmx-63vjcuc_W'
