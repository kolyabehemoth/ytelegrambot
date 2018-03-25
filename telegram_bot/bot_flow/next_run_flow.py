from crontab import CronTab
import collections
import logging
from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.dao.db_manager import CronsRepository
from telegram_bot.entities.domain_entities import FlowTypes

logger = logging.getLogger(__name__)


class NRFlow(AbstractFlow):
    flow_type = FlowTypes.NEXT_RUN
    cronRepository = CronsRepository()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('NEXT_RUN')
        crons = self.cronRepository.read_by_user_id(user_id=user_id)
        crons_d = {}
        for c in crons:
            crons_d[c.next_run()] = c
        sorted_c = collections.OrderedDict(sorted(crons_d.items()))
        v = next(iter(sorted_c.values()))
        next_run = int(round(v.next_run()))
        logger.info("cron_next_run: name: %s, time: %s" %(v.name, next_run))
        update.message.reply_text('next cron: %s will be run in %s sec' % (v.name, next_run))
        cache.flow_step = 0
        cache.flow_ended = True
