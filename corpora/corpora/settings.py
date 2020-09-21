
try:
    from .local_settings import *
except ImportError:
    pass

from corpus.base_settings import *
from people.base_settings import *
from corpora.base_settings import *
from transcription.base_settings import *

# Determine which language to set
# os import language the import settings/haw.py
