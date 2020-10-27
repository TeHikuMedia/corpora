# -*- coding: utf-8 -*-
from jellyfish import levenshtein_distance as levd

import logging
logger = logging.getLogger('corpora')


def word_error_rate(original, asr, language):
    original = original.lower()
    asr = asr.lower()

    if language.lower() in 'mi':
        from transcription.wer.mi import clean_text_for_wer_calculation
    else:
        logger.warn('No WER implemented for language {0}.'.format(language))
        return None

    original = clean_text_for_wer_calculation(original)

    return levd(original, asr) / float(len(original))
