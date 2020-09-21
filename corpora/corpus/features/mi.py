# -*- coding: utf-8 -*-
# Library functions for manipulating Māori text corpora.
"""Typically you will only use the def get_features() function, which
you do like this:

sentence = "ko wai au?"
features = get_features(sentence)
print('|'.join(sorted(features.elements())))
# prints
#" | |ai|ai»|au|au»|i»|k|ko|ko»|o|o»|u»|w|wa|wai|«a|«au|«k|«ko|«w|«wa|ä|ȧ"

What are these features?
========================

For a start, there are all the unigrams, counting macronised vowels
and diphongs as single units. For example, the unigrams in "ko wai
au?" are 'k', 'o', ' ', 'w', 'ai', ' ', and 'au'. The diphthongs are
represented by ad-hoc characters ('ä' and 'ȧ' in this case), but don't
worry about that -- it doesn't matter. The consonants 'wh' and 'ng'
are represented as 'f' and 'ŋ' respectively.

Next there are all the bigrams, calculated by splitting macrons and
diphthongs. That is, "ngā hau" would be converted to "ŋaa hau" and
result in the bigrams 'ŋa', 'aa', 'a ', ' h', 'ha', 'au'.

Finally there are all the trigrams, which would be 'ŋaa', 'aa ',
'a h', ' ha', 'hau' for "ngā hau".

"""
from __future__ import print_function, unicode_literals
import re
import unicodedata
import sys
from collections import Counter

DIPHTHONGS = {
    'ae': 'æ',
    'ai': 'ȧ',
    'ao': 'å',
    'au': 'ä',
    'oi': 'ȯ',
    'oe': 'œ',
    'ou': 'ö',
    'ei': 'ė',
    'eu': 'ë'
}


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def possible_n_grams(n, state='v'):
    """Estimate the number of possible n-grams, very roughly."""
    # let's assume there are two states, vowel and consonant.
    # vowels = 10     # a e i o u ā ē ī ō ū
    # consonants = 10 # h k m n ng p r t w wh
    if n <= 0:
        return 1

    total = 0
    if state == 'v':
        total += 10 * possible_n_grams(n - 1, 'c')
    total += 10 * possible_n_grams(n - 1, 'v')
    return total


def generate_n_grams(n, prefix, diphthongs, macrons):
    """Estimate the number of possible n-grams, very roughly."""
    # let's assume there are two states, vowel and consonant.
    if n <= 0:
        return [prefix]

    chars = 'aeiou'
    if diphthongs:
        chars += ''.join(DIPHTHONGS.values())

    if macrons:
        chars += 'āēīōū'

    if prefix == '' or prefix[-1] in chars:
        chars += 'fhkmnŋprtw'

    ngrams = []
    for c in chars:
        ngrams.extend(generate_n_grams(n - 1, prefix + c, diphthongs, macrons))
    return ngrams


has_bad_letter = re.compile('[^aeiouāēīōūfhkmnŋprtw ]', re.UNICODE).search
has_bad_cluster = re.compile('[fhkmnŋprtw][fhkmnŋprtw]', re.UNICODE).search
has_bad_end = re.compile('[^aeiouāēīōū ]\\b', re.UNICODE).search


def has_english(text):
    if (has_bad_letter(text) or
        has_bad_cluster(text) or
        has_bad_end(text)):
        return True
    return False


def remove_english(text):
    words = text.split()
    good_words = []
    for word in words:
        if has_english(word):
            continue
        good_words.append(word)
    return ' '.join(good_words)


def normalise_text(text):
    if isinstance(text, bytes):
        text = text.decode('utf8')
    text = unicodedata.normalize('NFC', text)
    text = text.lower()
    text = re.sub(r'[^\wāēōūī]+', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\b[0-9]+\d', ' ', text, flags=re.UNICODE)
    text = re.sub(r'ng', 'ŋ', text, flags=re.UNICODE)
    text = re.sub(r'wh', 'f', text, flags=re.UNICODE)
    return text


def find_features(text, word_boundaries, trigram_mode):
    text = normalise_text(text)

    if has_english(text):
        return Counter()

    # count unigrams first (including diphthongs and macrons and spaces).
    features = Counter(mangle_text(text, diphthongs=True, macrons=True))

    text = mangle_text(text, diphthongs=False, macrons=False,
                       space_padding=True)
    words = text.split()
    is_vowel = set('aeiou').__contains__
    for word in words:
        if word_boundaries:
            word = '«%s»' % word
        if len(word) < 2:
            continue
        g2 = word[:2]
        features[g2] += 1
        for i in range(2, len(word)):
            g3 = g2 + word[i]
            g2 = g3[1:]
            features[g2] += 1

            if trigram_mode != 'none':
                if trigram_mode == 'all':
                    features[g3] += 1
                else:
                    for x, y in zip(g3, trigram_mode):
                        if y == 'v' and not is_vowel(x):
                            break
                    else:
                        features[g3] += 1

    return features


def mangle_text(text, diphthongs, macrons, no_english=True,
                space_padding=False):
    if no_english:
        text = remove_english(text)
    if not macrons:
        text = demacronise(text)
    if diphthongs:
        new = []
        i = 0
        while i < len(text):
            pair = text[i: i + 2]
            if pair in DIPHTHONGS:
                new.append(DIPHTHONGS[pair])
                i += 2
            else:
                new.append(pair[0])
                i += 1
        text = ''.join(new)

        for k, v in DIPHTHONGS.items():
            text = re.sub(k, v, text, flags=re.UNICODE)
    text = text.strip()
    if space_padding:
        text = ' ' + text + ' '
    return text


def denormalise_text(text):
    text = re.sub(r'ŋ', 'ng', text, flags=re.UNICODE)
    text = re.sub(r'f', 'wh', text, flags=re.UNICODE)
    for k, v in DIPHTHONGS.items():
        text = re.sub(v, k, text, flags=re.UNICODE)
    return text


def demacronise(text):
    return (text
            .replace('ā', 'aa')
            .replace('ē', 'ee')
            .replace('ī', 'ii')
            .replace('ō', 'oo')
            .replace('ū', 'uu'))


def load_raw_text(filenames):
    raw = []
    for fn in filenames:
        f = open(fn)
        raw.append(f.read())
        f.close()
    return '\n\n'.join(raw)


def load_text(filenames, **kwargs):
    text = load_raw_text(filenames)
    text = normalise_text(text)
    text = mangle_text(text, **kwargs)
    return text


def partially_normalise_text(text):
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\n\s*\n+', '. ', text, flags=re.UNICODE)
    text = re.sub(r'\n\s*', ' ', text, flags=re.UNICODE)
    return text


def get_features(sentence):
    features =  find_features(sentence,
                              word_boundaries=True,
                              trigram_mode='all')
    return features
