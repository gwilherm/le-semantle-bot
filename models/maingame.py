# -*- coding: utf-8 -*-

from .game import Game

import os
import json
import logging
from utils import env
from collections import namedtuple
from apscheduler.schedulers.background import BackgroundScheduler

Stats = namedtuple('Stats', ['num', 'solvers'])
Score = namedtuple('Score', ['error', 'num', 'percentile', 'score', 'solvers'])

class MainGame(Game):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)


    def __init__(self, lexique, model):
        self.lexique = lexique
        self.model = model

        if not os.path.exists(env.WORD_FILE):
            self.random_word()
            self.save_word()
        else:
            self.restore_word()
        self.logger.info(f'Le mot à deviner est: {self.word_to_guess}')

        if not os.path.exists(env.HIST_FILE):
            self.history = [[0, 0, '']]
        else:
            self.restore_history()

        # initialize global
        self.solvers = 0
        self.day_num = len(self.history)

    def start(self):
        scheduler = BackgroundScheduler(timezone='Europe/Paris')
        scheduler.add_job(self.game_over, 'cron', hour=0, minute=0)
        scheduler.start()


    def save_word(self):
        with open(env.WORD_FILE, 'w') as f:
            f.write(self.word_to_guess)


    def restore_word(self):
        with open(env.WORD_FILE, 'r') as f:
            self.word_to_guess = f.read()


    def save_history(self):
        with open(env.HIST_FILE, 'w') as f:
            json.dump(self.history, f)


    def restore_history(self):
        with open(env.HIST_FILE, 'r') as f:
            self.history = json.load(f)


    def score(self, word):
        score = super().score(word)
        if score.score == 1.0:
            self.solvers += 1
        return Score(score.error, self.day_num, score.percentile, score.score, self.solvers)


    def top(self, word, topn):
        result = []
        top = self.model.most_similar(word, topn=topn)
        for rank,w in enumerate([(word, 1.0), *top]):
            result.append((w[0], 1000 - rank, float(w[1] * 100)))

        return result


    def nearby(self, word):
        if word == self.word_to_guess:
            result = self.top(word, 999)
        elif word == self.history[1][2]:
            result = self.top(word, 100)
        else:
            result = ''
        return result


    def stats(self):
        return Stats(self.day_num, self.solvers)._asdict()


    def game_over(self):
        self.history[0] = [self.day_num, self.solvers, self.word_to_guess]
        self.day_num += 1
        self.solvers = 0
        self.history = [[self.day_num, 0, ''], *self.history]
        self.save_history()
        self.random_word()
        self.save_word()
        self.logger.info(f'Le nouveau mot à deviner est: {self.word_to_guess}')

