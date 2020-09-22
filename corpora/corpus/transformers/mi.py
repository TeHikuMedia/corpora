# -*- coding: utf-8 -*-
import re


def strip_commas(text):
    return re.sub(r'[,]', u'', text, flags=re.U)


def strip_punctuation(text):
    return re.sub(r'[^\w\s]', u'', text, flags=re.U)


def digits_to_text(match):

    num = int(match.group())

    if abs(num) >= 10000:
        # Get rid of large numbers
        return ''

    digits = [int(i) for i in str(num)]

    ones = ['kore', 'tahi', 'rua', 'toru', u'whā',
            'rima', 'ono', 'whitu', 'waru', 'iwa']
    places = ['mano', 'rau', 'tekau', '']

    ones_dict = dict(zip([i for i in range(10)], ones))
    places_dict = dict(zip([3, 2, 1, 0], places))

    digit_words = []
    for place, digit in enumerate(digits[::-1]):
        ones_digit = ones_dict[digit]

        place_digit = places_dict[place]

        if place == 1:
            place_digit = place_digit + u" mā"

        if place > 1 and ones_digit == 'tahi':
            ones_digit = "kotahi"

        place_words = ones_digit + " " + place_digit
        place_words = place_words.strip()

        digit_words.append(place_words)

    digit_text = u' '.join(digit_words[::-1])

    digit_text = digit_text.replace(u" mā kore", u"")
    digit_text = digit_text.replace(u" kore rau", u"")
    digit_text = digit_text.replace(u"kore tekau", u"")
    digit_text = digit_text.replace(u"tahi tekau", u"tekau")
    digit_text = digit_text.strip()

    return digit_text


def fix_numbers(text):
    return re.sub(r'\d+', digits_to_text, text, flags=re.U)
