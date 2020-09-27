from corpora.settings import *

sys.path.append('/webapp/corpora/corpora')

### FILE STORAGE SETTINGS ###
# TURNED OFF FOR NOW AS IT BREAKS TESTS THAT NEED UPDATING
# DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
### FILE STORAGE SETTINGS ###

### ALLOWED HOSTS ###
ALLOWED_HOSTS=['koreromaori.com', 'corporalocal.nz', 'testserver']
### ALLOWED HOSTS ###

### LOGGING (Disabled for testing) ###
LOGGING = {}
### LOGGING ###
