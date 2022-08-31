# -*- coding: utf-8 -*-

import os

APP_STORAGE = os.environ['APP_STORAGE']
WORD2VEC_MODEL = os.path.join(APP_STORAGE, os.environ['WORD2VEC_MODEL'])
LEXIQUE_CSV    = os.path.join(APP_STORAGE, os.environ['LEXIQUE_CSV'])
WORD_FILE = os.path.join(APP_STORAGE, 'word.txt')
HIST_FILE = os.path.join(APP_STORAGE, 'history.json')
