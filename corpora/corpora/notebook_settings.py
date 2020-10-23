import os

from corpora.settings import *


### LOGGING (Disabled for testing) ###
LOGGING = {}
### LOGGING ###


### IPython notebook config ###

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
NOTEBOOK_ARGUMENTS = [
    # exposes IP and port
    '--ip=0.0.0.0',
    '--port=9999',
    '--NotebookApp.base_url=/corpora-ipython-notebook',
]

### IPython notebook config ###
