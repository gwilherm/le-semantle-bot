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


def get_game(room_uuid):
    try:
        game = games[room_uuid]
    except KeyError:
        abort(404)
    return game

@side_game.route('/create', methods=['GET'])
def create():
    room = uuid.uuid4()
    games[str(room)] = Game(lexique, model)
    return f'"{room}"\n'


@side_game.route('/<room>/score', methods=['POST'])
def score(room):
    form = request.form

    result = get_game(room).score(form.get('word'))

    return convert_namedtuple_to_dict(result)    


@side_game.route('/<room>/nearby', methods=['POST'])
def nearby(room):
    form = request.form

    result = get_game(room).nearby(form.get('word'))

    return result


@side_game.route('/<room>/giveup', methods=['GET'])
def giveup(room):
    form = request.form

    result = get_game(room).giveup()

    return f'"{result}"\n'