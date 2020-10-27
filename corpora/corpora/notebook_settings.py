import os

from corpora.settings import *


### DATABASE CONFIG ###

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['READ_DATABASE_USER'],
        'PASSWORD': os.environ['READ_DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': '5432',
    }
}

### DATABASE CONFIG ###

### LOGGING (Disabled for testing) ###

LOGGING = {}

### LOGGING ###


### IPython notebook config ###

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

NOTEBOOK_ARGUMENTS = [
    # exposes IP and port
    '--ip', '0.0.0.0',
    '--port', '9999',
    '--NotebookApp.base_url', '/corpora-ipython-notebook',
    '--NotebookApp.password', 'sha1:0fd79e03d39f:aab45f20dbba3587fbabc29a335a52ecfefa6e69',
    '--notebook-dir', '/home/corpora/notebook_scripts/',
    '--no-browser',
    '--allow-root'
]

### IPython notebook config ###
