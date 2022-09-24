# -*- coding: utf-8 -*-

import os
import uuid
import logging
from flask import Blueprint
from flask import request
from flask import abort

from models import games, model, lexique
from models import Game

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


side_game = Blueprint('side_game', __name__)


def convert_namedtuple_to_dict(nt):
    return dict(filter(lambda item: item[1] is not None, nt._asdict().items()))


@side_game.route('/create', methods=['GET'])
def create():
    room = uuid.uuid4()
    games[str(room)] = Game(lexique, model)
    return f'"{room}"\n'


@side_game.route('/<room>/score', methods=['POST'])
def hello(room):
    form = request.form

    try:
        game = games[room]
    except KeyError:
        abort(404)

    result = game.score(form.get('word'))

    return convert_namedtuple_to_dict(result)    
