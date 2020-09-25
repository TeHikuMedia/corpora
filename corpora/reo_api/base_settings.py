# -*- coding: utf-8 -*-
from corpora.base_settings import *
import os

SITE_ID = 2

ALLOWED_HOSTS = "*"  #['{0}'.format(i) for i in os.environ['ALLOWED_HOSTS_2'].split(' ')]

ROOT_URLCONF = 'reo_api.urls'
LANGUAGE_CODE = 'en'


LOGIN_REDIRECT_URL = "transcription:dashboard"

X_FRAME_OPTIONS = 'ALLOW-FROM koreromaori.com koreromaori.io \
dev.koreromaori.com dev.koreromaori.io corporalocal.io \
172.28.128.13 kaituhi.nz'

CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + ('172.28.128.13', 'kaituhi.nz')

# CORS_ORIGIN_ALLOW_ALL = True
