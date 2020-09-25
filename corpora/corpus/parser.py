# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError

import re
import unicodedata
import codecs

# import nltk

from .models import Sentence

MIN_SENTENCE_LENGTH = 12
MAX_SENTENCE_LENGTH = 12*8*10*10


def save_sentences_from_text(text_obj):
    try:
        contents = get_textfile_contents(text_obj.cleaned_file)
    except Exception as e:
        contents = get_textfile_contents(text_obj.original_file)

    errors = 0
    saved = 0
    for info in get_sentences(contents):
        sentence_data = {
            'source': text_obj.source,
            'language': text_obj.primary_language,
            'text': info['sentence']
        }
        sentence = Sentence(**sentence_data)

        try:
            sentence.clean()
        except ValidationError:
            continue

        sentence.save()
        saved += 1

    return {'saved': saved, 'errors': errors}


def get_textfile_contents(file_obj):
    file_obj.seek(0)
    contents = file_obj.read()

    # convert to unicode if it's a plain str
    if not isinstance(contents, str):  # NOQA ignore F821
        contents = codecs.decode(contents, 'utf-8')

    return contents


def get_sentences(text):
    """Extract a list of desirable sentences from a text. Return a list of
    dicts containing a 'sentence' key (so we can add additional metadata if
    needed in the future). """

    # for sentence in nltk.sent_tokenize(text):

    # assume all linebreaks denote end of sentence
    for line in map(str.strip, text.splitlines()):
        if not line or line.startswith('# '):
            continue
        line = line.replace('Mr.', 'Mika')
        line = line.replace('Mrs.', 'Miki')

        for sentence in map(normalise_sentence, line.split('.')):
            if len(sentence) < MIN_SENTENCE_LENGTH or len(sentence) > MAX_SENTENCE_LENGTH:  # has_english(sentence)
                continue
            yield {'sentence': sentence}


def normalise_sentence(sentence):
    return sentence.strip().rstrip('.')


# adapted from https://github.com/douglasbagnall/mi.wikipedia/

def normalise_text(text):
    text = unicodedata.normalize('NFC', text)
    text = text.lower()
    # text = re.sub(r'[^\wāēōūī]+', ' ', text)
    return text


has_bad_letter = re.compile('[bcdfjlqsvxyz]').search
# note wh and ng are valid clusters
has_bad_cluster = re.compile(
    r'[ghkmprt][ghkmnprtw]|w[gkmnprtw]|n[hkmnprtw]').search
has_bad_end = re.compile(r'[ghkmnprtw](?:\s\.,)').search


def has_english(text):
    text = normalise_text(text)
    if has_bad_letter(text) or has_bad_cluster(text) or has_bad_end(text):
        return True
    return False



### Hawaiian notes
# need to keep Mr. & Mrs. 
# Mrs. = Miki
# Mr. = Mika

#         line = line.replace('Mr.', 'Mika')
        # line = line.replace('Mrs.', 'Miki')
