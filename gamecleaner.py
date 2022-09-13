# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from models import games


class GameCleaner(BackgroundScheduler):
    '''Scheduled task to clean every 30 minutes games inactive for more than 24 hours.'''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARN)


    def __init__(self):
        super().__init__(timezone='Europe/Paris')
        super().add_job(self.run, 'interval', minutes=30)


    def run(self):
        for id,game in dict(games).items():
            if datetime.now() >= game.last_activity + timedelta(hours=24):
                del games[id]
        self.logger.info(str(len(games)) + ' running games')