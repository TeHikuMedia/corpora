import os
import sys
import analytical

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.environ['PROJECT_NAME']
APPLICATION_USER = os.environ['PROJECT_NAME']
APPLICATION_GROUP = os.environ['PROJECT_NAME']
ENV_TYPE = os.environ['ENVIRONMENT_TYPE']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ['DJANGO_ISNOT_PRODUCTION'])

ALLOWED_HOSTS = ['{0}'.format(i) for i in os.environ['ALLOWED_HOSTS'].split(' ')]

# Manual for now
ALLOWED_HOSTS.append('olelohawaii.com')

# INTERNAL_IPS = ['corporalocal.nz', 'corporalocal.io', 'dev.koreromaori.com', '10.1.160.139', '127.0.0.1']

# For ELB Certificate & NGINX settings.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [

    'dal',
    'dal_select2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',

    'collectfast',
    # 'django.contrib.staticfiles',
    'corpora.staticfiles.CorporaStaticFilesConfig',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'corpora',
    'corpus',
    'people',
    'license',
    'message',
    'transcription',
    'reo_api',
    'helpers',

    'storages',
    'djangobower',

    'sekizai',
    'compressor',
    # 'compressor_toolkit',
    # 'sass_processor',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.google',

    'rest_framework',
    'rest_framework.authtoken',

    'analytical',
    'ckeditor',
    'ckeditor_uploader',

    # 'debug_toolbar',

    'corsheaders',

    'django_celery_beat',
    'webpack_loader',
]

MIDDLEWARE = [


    'corsheaders.middleware.CorsMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware', # <= for caching entire site


    'django.middleware.locale.LocaleMiddleware',



    'corpora.middleware.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware', # <= for caching entire site
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corpora.middleware.PersonMiddleware',
    'corpora.middleware.LicenseMiddleware',
    'corpora.middleware.ExpoLoginMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',

]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": 'corpora.middleware.show_toolbar_callback'
}


ROOT_URLCONF = 'corpora.urls'

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
                'django.template.context_processors.i18n',
                'sekizai.context_processors.sekizai',
                'license.context_processors.license',
                'corpora.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'corpora.wsgi.application'

# CORS
CORS_ORIGIN_WHITELIST = \
    ['https://{0}'.format(i) for i in os.environ['ALLOWED_HOSTS'].split(',')]
CORS_ORIGIN_WHITELIST = tuple(CORS_ORIGIN_WHITELIST)


CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + ('https://172.28.128.13', 'https://kaituhi.nz')

CORS_ORIGIN_ALLOW_ALL = True

# STORAGES #
DEFAULT_FILE_STORAGE =      os.environ['FILE_STORAGE']
AWS_ACCESS_KEY_ID =         os.environ['AWS_ID']
AWS_SECRET_ACCESS_KEY =     os.environ['AWS_SECRET']
AWS_STORAGE_BUCKET_NAME =   os.environ['AWS_BUCKET']
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'private'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# S3 only access
AWS_ACCESS_KEY_ID_S3 =         os.environ['AWS_ID_S3']
AWS_SECRET_ACCESS_KEY_S3 =     os.environ['AWS_SECRET_S3']


CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"
CKEDITOR_IMAGE_BACKEND = 'pillow'
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
# We use ansible to create the environment variables to use.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'], # TODO: Give this a better name?
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'], # TODO: Secure this!
        'HOST': os.environ['DATABASE_HOST'],           
        'PORT': '5432',
        }
    }

# All auth
AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

)
LOGIN_REDIRECT_URL = 'people:profile'  # is there a more fool proof option?
ACCOUNT_ADAPTER = "people.adapter.PersonAccountAdapter"
SOCIALACCOUNT_ADAPTER = "people.adapter.PersonSocialAccountAdapter"
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile', ],  # Will require app approval for user_about_me access.
        'FIELDS': [  # see https://developers.facebook.com/docs/graph-api/reference/user/
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'locale',
            'timezone',
            'languages'],
        #  'LOCALE_FUNC': 'path.to.callable',
        'VERSION': 'v2.4'},
    'google': {
        'SCOPE': ['profile', 'email'],  # https://developers.google.com/identity/protocols/OAuth2
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'locale',
            'timezone',
            'languages'],
    }}

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'


# Email
EMAIL_BACKEND = 'django_ses.SESBackend' # Use AWS Simple Email Service
AWS_REGION = None if 'local' in ENV_TYPE else os.environ['AWS_REGION']
AWS_SES_REGION_NAME =  'ap-southeast-2'
AWS_SES_REGION_ENDPOINT = "email.ap-southeast-2.amazonaws.com"
DEFAULT_FROM_EMAIL = u'"Kōrero Māori" <koreromaori@tehiku.nz>'


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

# Site ID
SITE_ID = 1


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
TIME_ZONE = 'Pacific/Auckland'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ['STATIC_PATH'] #os.path.join(BASE_DIR, 'public', 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ['MEDIA_PATH']

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'corpora/static')

# BOWER IS DEPRICATED - FIND AN ALTERNATIVE!
BOWER_INSTALLED_APPS = {
    'jquery',
    'jquery-ui',
    'bootstrap',
    #'opus-recorderjs#v5.1.1',
    'js-cookie',
    'popper.js',
    'chart.js',
}

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, '...', 'static'),
# )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',

    # Additional finders
    'djangobower.finders.BowerFinder',
    # 'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',

)

# memcache_server = os.environ['DJANGO_MEMCACHED_IP']
# memcache_servers = []
# for srv in memcache_server.split(','):
#     srv = srv.strip()
#     if srv != '':
#         memcache_servers.append(
#             "{0}:{1}".format(
#                 srv.strip(), os.environ['DJANGO_MEMCACHED_PORT']))




# DJANGO-COMPRESSOR SETTINGS
COMPRESS_PRECOMPILERS = (
    # ('text/coffeescript', 'coffee --compile --stdio'),
    # ('text/less', 'lessc {infile} {outfile}'),
    # ('text/x-sass', 'sass {infile} {outfile}'),
    # ('text/x-scss', 'sass --scss {infile} {outfile}'),
    # ('module', 'compressor_toolkit.precompilers.ES6Compiler'),
    ('text/x-scss', 'django_libsass.SassCompiler'),
    # ('text/stylus', 'stylus < {infile} > {outfile}'),
    # ('text/foobar', 'path.to.MyPrecompilerFilter'),
)
COMPRESS_LOCAL_NPM_INSTALL = False
COMPRESS_ENABLED = not DEBUG
# COMPRESS_NODE_MODULES = "/usr/local/lib/node_modules/"


'''
There are a set of settings that allow us to use CloudFront for s3 hosted
files. We also use a separate bucket for static files, because Corpora
needs protected s3 files (e.g. recordings).
'''
ENVIRONMENT_TYPE = os.environ['ENVIRONMENT_TYPE']

COLLECTFAST_CACHE = 'collectfast'
COLLECTFAST_THREADS = 10
if ENVIRONMENT_TYPE != 'local':
    AWS_PRELOAD_METADATA = True
    AWS_STATIC_BUCKET_NAME = os.environ['AWS_STATIC_BUCKET']
    AWS_STATIC_DEFAULT_ACL = 'public-read'
    COMPRESS_URL = 'https://'+os.environ['AWS_CLOUDFRONT_CNAME']+'/'
    AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_CLOUDFRONT_CNAME']
    STATIC_URL = COMPRESS_URL
    COMPRESS_STORAGE = 'corpora.storage.CachedS3BotoStorage'
    STATICFILES_STORAGE = 'corpora.storage.CachedS3BotoStorage'
    COLLECTFAST_STRATEGY = 'collectfast.strategies.boto3.Boto3Strategy'

    # AWS_IS_GZIPPED = True
    CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + \
        ('https://' + os.environ['AWS_CLOUDFRONT_CNAME'],)

else:
    COLLECTFAST_STRATEGY = 'collectfast.strategies.filesystem.FileSystemStrategy'



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s -- %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'testconsole': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../../logs/django.log',
            'formatter': 'verbose',
            'maxBytes': 1024 * 1000,  # 1kb * X
            'backupCount': 20,
        },
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../../logs/celery.log',
            'formatter': 'simple',
            'maxBytes': 1024 * 1000,  # 500 kb,
            'backupCount': 20,
        }
    },
    'loggers': {
        'django.test': {
            'handlers': ['testconsole'],
            'level': 'DEBUG',
            'propogate': True
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'corpora': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propogate': True
        },
        'celery': {
            'handlers': ['celery', 'console'],
            'level': 'DEBUG',
            'propogate': True
        }
    }
}


# API Stuff
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'reo_api.authentication.ApplicationAPITokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'reo_api.renderers.PlainTextRenderer',
        'reo_api.renderers.WebVTTRenderer',
    ),
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',

    ],
    'DEFAULT_THROTTLE_RATES': {
        'listen': '200/day',
        'sentence': '500/day',
        'anon': '50/day',
        'user': '1000/day',
    }
}


# CELERY #
if 'local' in ENV_TYPE:
    CELERY_BROKER_URL = 'amqp://%s:%s@%s:%s/%s' % (
        os.environ['CELERY_USER'],
        os.environ['CELERY_PASSWORD'],
        os.environ['CELERY_HOST'],
        os.environ['CELERY_PORT'],
        os.environ['CELERY_VHOST'])
    CELERY_RESULT_BACKEND= 'cache+memcached://%s:%s/' % ( os.environ['DJANGO_MEMCACHED_IP'], os.environ['DJANGO_MEMCACHED_PORT'])
else:
    REDIS_URL = os.environ['AWS_ELASTICACHE_URL']
    CELERY_BROKER_URL = f"redis://{REDIS_URL}:6379/0"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_URL}:6379/0"
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'fanout_prefix': True,
        'fanout_patterns': True,
    }

CELERY_TASK_DEFAULT_QUEUE = f"celery_{ENV_TYPE}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_EVENT_QUEUE_PREFIX: f"celery:{ENV_TYPE}"
CELERY_TASK_RESULT_EXPIRES = 21600  # 6 hours.


# CACHE
if 'local' in ENV_TYPE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '%s:%s' % (
                os.environ['DJANGO_MEMCACHED_IP'],
                os.environ['DJANGO_MEMCACHED_PORT']),
            "KEY_PREFIX": f"{PROJECT_NAME}:{ENV_TYPE}",
            'TIMEOUT': 300,
        },
        'collectfast': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp/django_cache',
        },
    }
else:
    if 'stag' in ENV_TYPE:
        timeout = 180
    else:
        timeout = 300

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{REDIS_URL}/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient"
            },
            "KEY_PREFIX": f"{PROJECT_NAME}:{ENV_TYPE}",
            'TIMEOUT': 300,
        },
        'collectfast': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{REDIS_URL}/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient"
            },
            "KEY_PREFIX": f"{PROJECT_NAME}:cf:{ENV_TYPE}",
            'TIMEOUT': timeout,
        },
    }



# These may be required if caching the entire site.
# CACHE_MIDDLEWARE_ALIAS 
# CACHE_MIDDLEWARE_SECONDS
# CACHE_MIDDLEWARE_KEY_PREFIX



### ERROS WITH UTC = FALSE!
# CELERY_TIMEZONE = TIME_ZONE
# CELERY_ENABLE_UTC = False


# DJANGO ANALYTICAL
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-114290321-1'
# GOOGLE_ANALYTICS_TRACKING_STYLE = \
#     analytical.templatetags.google_analytics.SCOPE_TRACK_MULTIPLE_DOMAINS
GOOGLE_ANALYTICS_DISPLAY_ADVERTISING = True
GOOGLE_ANALYTICS_SITE_SPEED = True
GOOGLE_ANALYTICS_ANONYMIZE_IP = True
FACEBOOK_PIXEL_ID = '158736294923584'
# INTERCOM_APP_ID =''


# Transcode API Stuff
TRANSCODE_API_TOKEN = os.environ['TRANSCODE_API_TOKEN']


### Vue frontend Config ###
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'vue_bundles/',  # must end with slash
        'STATS_FILE': os.path.join(
            PROJECT_NAME,
            'static',
            'vue_bundles',
            'webpack-stats.json'
        ),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}
