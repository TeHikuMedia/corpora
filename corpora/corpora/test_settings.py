from corpora.settings import *

sys.path.append('/webapp/corpora/corpora')

### FILE STORAGE SETTINGS ###
# TURNED OFF FOR NOW AS IT BREAKS TESTS THAT NEED UPDATING
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
### FILE STORAGE SETTINGS ###

### ALLOWED HOSTS ###
ALLOWED_HOSTS=['koreromaori.com', 'corporalocal.nz', 'testserver']
### ALLOWED HOSTS ###

### LOGGING (Disabled for testing) ###
LOGGING = {}
### LOGGING ###


### Modify Database Settings ###
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'], # TODO: Give this a better name?
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'], # TODO: Secure this!
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': '5432',
        },
    }
DATABASE_ROUTERS = []
