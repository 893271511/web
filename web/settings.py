"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 1.8.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kx%lo5)@9(&d3&z!rk&ss9t$f5d+w1n14n9)(p($@ekr_r7y20'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False

ALLOWED_HOSTS = ['10.2.52.81']


# Application definition
#    'debug_toolbar',
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'release',
    'guardian'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'breadcrumbs.middleware.BreadcrumbsMiddleware',


)

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'zh_CN'
#DEFAULT_CHARET = 'UTF-8'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

PROJECT_ROOT=os.path.join(os.path.abspath(os.path.dirname(__file__)),'..')

STATIC_ROOT = os.path.join(PROJECT_ROOT,'static')

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/index/'

LOGIN_URL = '/'

APPEND_SLASH=False


LOGGING = {
    'version': 1,#指明dictConnfig的版本，目前就只有一个版本，哈哈
    'disable_existing_loggers': True,#禁用所有的已经存在的日志配置
    'formatters': {#格式器
        'verbose': {#详细
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {#简单
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {#过滤器
        'special': {#使用project.logging.SpecialFilter，别名special，可以接受其他的参数
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {#处理器，在这里定义了三个处理器
        'default': {
            'level':'DEBUG',
            #'class':'django.utils.log.NullHandler',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':'logs/debug.log',  #日志输出文件
            'maxBytes':1024*1024*5,      #文件大小
            'backupCount':5,          #备份份数
            'formatter':'verbose'     #日志格式
        },
        'console':{#流处理器，所有的高于（包括）debug的消息会被传到stderr，使用的是simple格式器
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {#AdminEmail处理器，所有高于（包括）而error的消息会被发送给站点管理员，使用的是special格式器
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['special']
        }
    },
    'loggers': {#定义了三个记录器
        'django': {
            'handlers': ['default','console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {#所有高于（包括）error的消息会被发往mail_admins处理器，消息不向父层次发送
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'myproject.custom': {#所有高于（包括）info的消息同时会被发往console和mail_admins处理器，使用special过滤器
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'filters': ['special']
        }
    }
}


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # django默认的backend
    'guardian.backends.ObjectPermissionBackend',
)
