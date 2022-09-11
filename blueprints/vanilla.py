# -*- coding: utf-8 -*-

import os
import logging
from flask import Blueprint
from flask import request

from models import main_game

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


vanilla = Blueprint('vanilla', __name__)


def convert_namedtuple_to_dict(nt):
    return dict(filter(lambda item: item[1] is not None, nt._asdict().items()))


@vanilla.route('/score', methods=['POST'])
def score():
    form = request.form

    result = main_game.score(form.get('word'))

    return convert_namedtuple_to_dict(result)


@vanilla.route('/nearby', methods=['POST'])
def nearby():
    form = request.form

    result = main_game.nearby(form.get('word'))

    return result


@vanilla.route('/stats', methods=['GET'])
def stats():
    return main_game.stats()


@vanilla.route('/history', methods=['GET'])
def hist():
    return main_game.history
