# -*- coding: utf-8 -*-

import random
import logging
from datetime import datetime
from collections import OrderedDict
from collections import namedtuple
from gensim.models import KeyedVectors

from utils import env

Score = namedtuple('Score', ['error', 'percentile', 'score'])

class Game:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)


    def __init__(self, lexique, model):
        self.in_game = True
        self.lexique = lexique
        self.model = model
        self.last_activity = datetime.now()
        self.random_word()


    def random_word(self):
        self.word_to_guess = self.lexique[random.randrange(0, len(self.lexique))][0]


    def score(self, word):
        self.last_activity = datetime.now()
        error_str = None
        percentile = None
        score = None

        if self.in_game:
            if word is not None and word != '':
                try:
                    if word == self.word_to_guess:
                        self.in_game = False
                        # with gensim rank of word with itself is 1 and similarity can be 0.99999994
                        score = 1.0
                        rank = 0
                    else:
                        score = float(self.model.similarity(word, self.word_to_guess))
                        rank = self.model.rank(self.word_to_guess, word)

                    percentile = 1000 - rank if rank <= 1000 else None
                except KeyError:
                    error_str = f'Je ne connais pas le mot <i>{word}</i>.'
            else:
                error_str = 'Je ne connais pas ce mot.'
        else:
            error_str = f'Partie terminée, le mot était <i>{self.word_to_guess}</i>.'

        return Score(error_str, percentile, score)


    def nearby(self, word):
        if word == self.word_to_guess:
            result = self.top(word, 999)
        else:
            result = ''
        return result


    def giveup(self):
        self.in_game = False
        return self.word_to_guess