import os
import csv
from gensim.models import KeyedVectors

from utils import env
from .game import Game
from .maingame import MainGame

# load the model
model = KeyedVectors.load_word2vec_format(env.WORD2VEC_MODEL, binary=True, unicode_errors="ignore")

# load the dictionary
csv_reader = csv.reader(open(env.LEXIQUE_CSV), delimiter='\t')
lexique = list(filter(lambda c: ((c[3] == 'NOM' or c[3] == 'ADJ' or c[3] == 'VER') and
                                    (c[4] == '' or c[4] == 'm') and
                                    (c[5] == '' or c[5] == 's') and
                                    (float(c[6]) >= 1.0) and
                                    (c[10] == '' or c[10][:3] == 'inf') and
                                    (c[0] in model.key_to_index)),
                        csv_reader))

games = dict()
main_game = MainGame(lexique, model)
