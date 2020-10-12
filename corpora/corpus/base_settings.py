# -*- coding: utf-8 -*-

import django.conf.locale
from django.utils.translation import ugettext_lazy as _

# This is required for languages that aren't in Django by default
EXTRA_LANG_INFO = {
    'mi': {
        'bidi': False,  # right-to-left
        'code': 'mi',
        'name': 'Maori',
        'name_local': u'Māori',
    },
    'en-NZ': {
        'bidi': False,  # right-to-left
        'code': 'en-NZ',
        'name': 'New Zealand English',
        'name_local': u'New Zealand English',
    },
    'haw': {
        'bidi': False,  # right-to-left
        'code': 'haw',
        'name': 'Hawaiian',
        'name_local': u'ʻŌlelo Hawaiʻi',
    },
    'smo': {
        'bidi': False,  # right-to-left
        'code': 'smo',
        'name': 'Samoan',
        'name_local': u'Gagana faʻa Sāmoa',
    },
    'rar': {
        'bidi': False,  # right-to-left
        'code': 'rar',
        'name': 'Cook Islands Maori',
        'name_local': u'Māori Kūki ʻĀirani',
    },
    'moh': {
        'bidi': False,  # right-to-left
        'code': 'moh',
        'name': 'Mohawk',
        'name_local': u'Kanienʼkéha',
    },
    'en-US': {
        'bidi': False,  # right-to-left
        'code': 'en-US',
        'name': 'American English',
        'name_local': u'English',
    },
}

LANG_INFO = \
    {**django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO}

# update the language info
django.conf.locale.LANG_INFO = LANG_INFO


LANGUAGE_COOKIE_NAME = 'corpora-language'
# LOCALE_PATHS = (
# We're making a local directory in each app and the project-app folder
#     os.path.join(BASE_DIR, 'locale'),
# )

# We need to start using the 3 character names
# https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
LANGUAGES = (

    ('mi',    _('Māori')),
    ('haw',    _('Hawaiian')),
    # ('smo',    _('Samoan')),
    ('rar',    _('Cook Island Māori')),
    # ('en',    _('English')),
    ('en-NZ', _('New Zealand English')),
    # ('en_US', _('American English')),
    # ('moh', _('Mohawk')),
)

DIALECTS = (

    # ('mi', (
    #         ('kaitahu',  _('Kaitahu')),
    #         ('muriwhen', _('Muriwhenua')),
    #         ('taranaki', _('Taranaki')),
    #         ('tuhoe', _('Tuhoe')),
    # )),

    ('mi', (
            ('tokerau', _('Te Tai Tokerau')),
            ('tainui', _('Tainui')),
            ('rawhiti', _('Te Tai Rawhiti')),
            ('hauauru', _('Te Tai Hauauru')),
            ('matatua', _('Mataatua')),
            ('tepuku', _('Te Puku o te Ika')),
            ('waipouna', _('Te Waipounamu')),
    )),

)

DIALECTS_HELP_TEXT = (

    ('mi', (
            ('tokerau', _('Te Tai Tokerau')),
            ('rawhiti', _('Te Tai Rāwhiti')),
            ('hauauru', _('Te Tai Hauāuru')),
            ('taitonga', _('Te Tai Tonga')),
            # ('tepuku', _('Te Puku o te Ika')),
            # ('waipouna', _('Te Waipounamu')),
    )),


)

ACCENTS = (

    ('mi', (
            # ('academic', _('Academic')),
            # ('modern',   _('Modern')),
            # ('englishi', _('English "i"')),
    )),

    ('en', (
            ('australi', _('Australian')),
            ('newzeald', _('New Zealand')),
            ('american', _('American')),
    )),

)

LANGUAGE_CODE = 'mi'


LANGUAGE_DOMAINS = {
    'dev.olelomaoli.com': 'haw',
    'dev.koreromaori.com': 'mi',
    'dev.koreromaori.io': 'mi',
    'olelohawaii.com': 'haw',
    'koreromaori.com': 'mi',
    'koreromaori.io': 'mi',
    'corporalocal.com': 'mi',
    'corporalocal.nz': 'mi',
    'corporalocal.io': 'mi',
    'corpora.com': 'en-NZ',
    'corporadocker.nz': 'mi',
}
