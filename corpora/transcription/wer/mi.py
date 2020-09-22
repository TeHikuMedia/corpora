# -*- coding: utf-8 -*-

from corpus.transformers import mi


def clean_text_for_wer_calculation(text):
    text = mi.strip_commas(text)
    text = mi.fix_numbers(text)
    text = mi.strip_punctuation(text)
    return text
