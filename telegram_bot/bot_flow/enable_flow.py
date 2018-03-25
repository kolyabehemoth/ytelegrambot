from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities.domain_entities import FlowTypes
from telegram_bot.dao.db_manager import CronsRepository
import re
import logging

logger = logging.getLogger(__name__)


class EFlow(AbstractFlow):
    flow_type = FlowTypes.ENABLE_CRON
    cronRepository = CronsRepository()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('ENABLE FLOW')
        if cache.flow_step == 0:
            update.message.reply_text('Enter pls id of cron which you want to enable')
            cache.flow_step = 1
        elif cache.flow_step == 1:
            cron_to_dis = self.parse_cron_id(update.message.text)
            cron = self.cronRepository.read_by_user_id(cron_to_dis)
            try:
                if not cron:
                    update.message.reply_text('Shit happened, can\'t find cron with such id')
                    return
                cron.active = True
                self.cronRepository.update(cron)
                update.message.reply_text('Updating cron was successful')
            except Exception as e:
                logger.error('Exception in Enable_flow happened: %s' % e)
                update.message.reply_text('Exception in Enable_flow happened')
            finally:
                cache.flow_step = 0
                cache.flow_ended = True

    def parse_cron_id(self, txt):
        for m in self._split_message(txt):
            if re.compile('\d{4}').match(m):
                return int(m)