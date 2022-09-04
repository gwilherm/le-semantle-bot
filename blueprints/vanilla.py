# -*- coding: utf-8 -*-

import os
import logging
from flask import Blueprint
from flask import g, current_app

from models import games

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


vanilla = Blueprint('vanilla', __name__)

game = games['main']

def convert_namedtuple_to_dict(nt):
    return dict(filter(lambda item: item[1] is not None, nt._asdict().items()))


@vanilla.route('/score', methods=['POST'])
def score():
    form = request.form

    result = game.score(form.get('word'))

    return convert_namedtuple_to_dict(result)


@vanilla.route('/nearby', methods=['POST'])
def nearby():
    form = request.form

    result = game.nearby(form.get('word'))

    return result


@vanilla.route('/stats', methods=['GET'])
def stats():
    return game.stats()


@vanilla.route('/history', methods=['GET'])
def hist():
    return game.history
