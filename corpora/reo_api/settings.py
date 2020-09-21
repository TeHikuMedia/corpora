
try:
    from .local_settings import *
except ImportError:
    pass

# from corpora.base_settings import *
from reo_api.base_settings import *
from corpus.base_settings import *
from people.base_settings import *
from transcription.base_settings import *

