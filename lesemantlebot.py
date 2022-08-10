#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import random
import logging
import asyncio
import discord
from discord.ext import commands
from gensim.models import KeyedVectors
from collections import OrderedDict
from collections import namedtuple
from apscheduler.schedulers.asyncio import AsyncIOScheduler

WORD_FILE = 'word.txt'
MAX_HISTORY = 20

Result = namedtuple('Result', ['word', 'try_number', 'temperature', 'points'])

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category='Commands'
)

bot = commands.Bot(
    command_prefix='!',
    description='LeSemantleBot',
    help_command=help_command
)


def save_word(word):
    f = open(WORD_FILE, 'w')
    f.write(word)
    f.close()


def restore_word():
    f = open(WORD_FILE, 'r')
    word = f.read()
    f.close()
    return word


def random_word():
    return lexique[random.randrange(0, len(lexique))][0]


async def game_over():
    global bot
    global guesses
    global guessed
    global word_to_guess
    async with mutex:
        for chan in guesses.keys():
            await bot.get_channel(chan).send(f'Partie terminée ! Le mot à deviner était `{word_to_guess}`')
        await bot.change_presence(activity=None)
        word_to_guess = random_word()
        save_word(word_to_guess)
        guesses = dict()
        guessed = dict()
        logger.info(f'Le nouveau mot à deviner est: {word_to_guess}')


def format_result(result: Result):
    result_str = f'n°{result.try_number:>4}\t{result.word:>20}\t{result.temperature:>6.2f}°C'
    if result.points > 0:
        result_str += f'\t{result.points}‰'
    result_str += '\n'
    return result_str


@bot.command(help='Try your word', aliases=['g'])
async def guess(context, *args):
    async with mutex:
        if len(args) > 0:
            proposition = args[0]

            if context.channel.id not in guesses:
                guesses[context.channel.id] = dict()

            try_number = len(guesses[context.channel.id]) + 1

            try:
                if proposition == word_to_guess:
                    rank = 0
                    if context.channel.id not in guessed:
                        await context.send(f'Bien joué <@{context.author.id}> ! Le mot était `{word_to_guess}`')
                        guessed[context.channel.id] = context.author
                        number_of_wins = len(guessed)
                        await bot.change_presence(activity=discord.Activity(name=f'{number_of_wins} gagnants aujourd\'hui.',
                                                                            type=discord.ActivityType.watching))
                    else:
                        await context.send(f'Trop tard, le mot a déjà été trouvé par {guessed[context.channel.id].name} !')
                else:
                    rank = model.rank(word_to_guess, proposition)

                temperature = model.similarity(proposition, word_to_guess) * 100
                points = 1000-rank

                result = Result(proposition, try_number, temperature, points)
                guesses[context.channel.id][rank] = result

                result_str = '```\n' + format_result(result) + '\n```'
                await context.send(result_str)
            except KeyError:
                await context.send(f'Je ne comprends pas `{proposition}`')

            history_str = '```\n'
            od = OrderedDict(sorted(guesses[context.channel.id].items()))
            for k, v in list(od.items())[:MAX_HISTORY]:
                history_str += format_result(Result(*v))
            history_str += '\n```'
            await context.send(history_str)


@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)


@bot.event
async def on_ready():
    await bot.change_presence(activity=None)

if __name__ == '__main__':
    # create logger
    logger = logging.getLogger('LeSemantleBot')
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

    # initialize global
    guesses = dict()
    guessed = dict()
    if not os.path.exists(WORD_FILE):
        word_to_guess = random_word()
        save_word(word_to_guess)
    else:
        word_to_guess = restore_word()
    logger.info(f'Le mot à deviner est: {word_to_guess}')

    # multithreading
    mutex = asyncio.Lock()

    scheduler = AsyncIOScheduler(timezone='Europe/Paris')
    scheduler.add_job(game_over, 'cron', hour=0, minute=0)
    scheduler.start()

    bot.run(os.environ['LESEMANTLE_BOT_TOKEN'])
