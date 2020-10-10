from importlib import import_module
import sys

from collections import Counter

# rely only on the set of characters.
default_feature_finder = Counter

def import_finder(lang):
    if lang.isalpha():
        try:
            m = import_module('corpus.features.'+lang)
            return m.get_features
        except ImportError as e:
            print("unknown language %s" % lang, file=sys.stderr)
            return default_feature_finder
        except AttributeError as e:
            return default_feature_finder
    return default_feature_finder
