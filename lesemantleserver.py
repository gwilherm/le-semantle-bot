#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import random
import logging
from flask import Flask
from flask import request
from gensim.models import KeyedVectors
from collections import OrderedDict
from collections import namedtuple
from apscheduler.schedulers.background import BackgroundScheduler

WORD_FILE = 'word.txt'
HIST_FILE = 'history.json'

Stats = namedtuple('Stats', ['num', 'solvers'])
Score = namedtuple('Score', ['error', 'num', 'percentile', 'score', 'solvers'])

def save_word(word):
    with open(WORD_FILE, 'w') as f:
        f.write(word)


def restore_word():
    with open(WORD_FILE, 'r') as f:
        word = f.read()
    return word


def random_word():
    return lexique[random.randrange(0, len(lexique))][0]


def save_history(history):
    with open(HIST_FILE, 'w') as f:
        json.dump(history, f)


def restore_history():
    with open(HIST_FILE, 'r') as f:
        hist = json.load(f)

    return hist


def game_over():
    global logger
    global day_num
    global history
    global word_to_guess

    history[0] = [day_num, word_to_guess, solvers]
    day_num += 1
    history    = [[day_num, '', 0], *history]
    save_history(history)

    word_to_guess = random_word()
    save_word(word_to_guess)
    logger.info(f'Le nouveau mot à deviner est: {word_to_guess}')


def convert_namedtuple_to_dict(nt):
    return dict(filter(lambda item: item[1] is not None, nt._asdict().items()))


# create logger
logger = logging.getLogger('LeSemantleServer')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# load the model
model = KeyedVectors.load_word2vec_format(os.environ['WORD2VEC_MODEL'], binary=True, unicode_errors="ignore")

# load the dictionary
csv_reader = csv.reader(open(os.environ['LEXIQUE_CSV']), delimiter='\t')
lexique = list(filter(lambda c: ((c[3] == 'NOM' or c[3] == 'ADJ' or c[3] == 'VER') and
                                    (c[4] == '' or c[4] == 'm') and
                                    (c[5] == '' or c[5] == 's') and
                                    (float(c[6]) >= 1.0) and
                                    (c[10] == '' or c[10][:3] == 'inf') and
                                    (c[0] in model.key_to_index)),
                        csv_reader))


if not os.path.exists(WORD_FILE):
    word_to_guess = random_word()
    save_word(word_to_guess)
else:
    word_to_guess = restore_word()
logger.info(f'Le mot à deviner est: {word_to_guess}')

if not os.path.exists(HIST_FILE):
    history = [[0, '', 0]]
else:
    history = restore_history()

# initialize global
solvers = 0
day_num = len(history)

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    scheduler = BackgroundScheduler(timezone='Europe/Paris')
    scheduler.add_job(game_over, 'cron', hour=0, minute=0)
    scheduler.start()


@app.route('/score', methods=['POST'])
def score():
    global logger
    global solvers
    global day_num

    form = request.form

    word = None
    try:
        word = form['word']
        if word == word_to_guess:
            rank = 0
            solvers += 1
        else:
            rank = model.rank(word_to_guess, word)

        score = float(model.similarity(word, word_to_guess))
        
        percentile = 1000 - rank if rank <= 1000 else None

        result = Score(None, day_num, percentile, score, solvers)
    except KeyError:
        if word is not None and word != '':
            error_str = f'Je ne connais pas le mot <i>{word}</i>.'
        else:
            error_str = 'Je ne connais pas ce mot.'
        result = Score(error_str, day_num, None, None, solvers)

    return convert_namedtuple_to_dict(result)


@app.route('/nearby', methods=['POST'])
def nearby():
    global logger
    global solvers
    global day_num

    form = request.form

    word = None
    try:
        word = form['word']
        if word == word_to_guess:
            result = []
            top999 = model.most_similar(word, topn=999)
            for rank,w in enumerate([(word, 1.0), *top999]):
                result.append((w[0], 1000 - rank, float(w[1] * 100)))
        else:
            result = ''
    except KeyError:
        result = ''

    return result


@app.route('/stats', methods=['GET'])
def stats():
    return Stats(day_num, solvers)._asdict()


@app.route('/history', methods=['GET'])
def hist():
    global history
    return history