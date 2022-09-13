#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import logging
from flask import Flask
from flask import request
from flask import g, current_app

from models import main_game
from gamecleaner import GameCleaner

from blueprints import *

# configure the logger
logging.basicConfig(format='%(asctime)s - %(name)s::%(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False


game_cleaner = GameCleaner()


if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    main_game.start()
    game_cleaner.start()


@app.route('/features', methods=['GET'])
def features():
    return list(app.blueprints.keys())


app.register_blueprint(vanilla)
app.register_blueprint(side_game)