from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from telegram_bot import bot_main
from telegram_bot.adsense_api.api import AdSenseAPIClientv2
from telegram_bot.dao.db_manager import CronsRepository, UserRepository
from telegram_bot.entities import domain_entities
import logging

logger = logging.getLogger(__name__)

sched = BlockingScheduler()
cronRep = CronsRepository()
userRep = UserRepository()


@sched.scheduled_job('interval', minutes=3)
def timed_cron_job():
    crons = cronRep.read_all()
    crons_to_execute = []
    users = {} #some day will migrate to sqlalchemy orm(NOPE) to avoid dat shit
    for c in crons:
        user = users.get(c.user_id, None)
        if not user:
            user = userRep.read_by_id(c.user_id)
            users[c.user_id] = user
        if c.next_run() < 180 and c.active and user.active:
            crons_to_execute.append(c)

    logger.info('crons to execute: %s ' % str(len(crons_to_execute)))
    with ThreadPoolExecutor(max_workers=4) as e:
        for cron in crons_to_execute:
            e.submit(s_function, cron)
    logger.info('This job is run every 3 minutes.')


def s_function(cron):
    print('cron_name: %s' % cron.name)
    bot = bot_main.bot
    user = userRep.read_by_id(cron.user_id)
    args = [user.chat_id]
    api = AdSenseAPIClientv2(bot.send_message, cron.user_id, *args)
    logger.info('scheduler api authenthiasdjfcasdfsadf')
    report = api.get_report_by_params(cron.request_params)
    logger.info('got report  HAHAHAHAHHA')
    logger.info(report)
    if not report:
        logger.debug('No data in report for user: %s' % str(user.id))
        bot.send_message(user.chat_id, 'No data in report')
        return
    bot.send_message(user.chat_id, domain_entities.format_report(report))
    pass


def main():
    logger.debug('Scheduler starting')
    t = Scth()
    t.start()
    logger.debug('Scheduler STARTED')


class Scth(Thread):

    def run(self):
        sched.start()
